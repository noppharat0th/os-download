# https://github.com/ventoy/Ventoy

import psutil
import subprocess
import os
import sys
import time
import threading
import ctypes
import struct
from modules.config import state, resource_path


class Ventoy:
    VENTOY_DIR = resource_path("bin")
    
    # Use x64 exe on 64-bit Windows, fallback to x86
    if sys.maxsize > 2**32:
        VENTOY_EXE = os.path.join(VENTOY_DIR, "altexe", "Ventoy2Disk_X64.exe")
    else:
        VENTOY_EXE = os.path.join(VENTOY_DIR, "Ventoy2Disk.exe")

    FS_OPTIONS = ["exFAT", "NTFS", "FAT32"]
    PARTITION_OPTIONS = ["MBR", "GPT"]

    @staticmethod
    def _get_physical_drive_number(drive_letter):
        try:
            # Use wmic to get physical drive number from drive letter
            letter = drive_letter.rstrip(":\\")
            result = subprocess.run(
                ["powershell", "-Command",
                 f"(Get-Partition -DriveLetter '{letter}').DiskNumber"],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0 and result.stdout.strip().isdigit():
                return int(result.stdout.strip())
        except Exception:
            pass
        return None

    @staticmethod
    def list_usb_drives():
        usb_drives = []
        for disk in psutil.disk_partitions():
            if 'removable' in disk.opts:
                try:
                    usage = psutil.disk_usage(disk.mountpoint)
                    total_gb = round(usage.total / (1024**3), 2)
                    free_gb = round(usage.free / (1024**3), 2)
                    drive_letter = disk.device.rstrip("\\")

                    # Get physical drive number
                    phy_drive = Ventoy._get_physical_drive_number(drive_letter)

                    usb_drives.append({
                        "device": disk.device,
                        "drive_letter": drive_letter,
                        "phy_drive": phy_drive,
                        "mountpoint": disk.mountpoint,
                        "fstype": disk.fstype,
                        "total_gb": total_gb,
                        "free_gb": free_gb,
                        "label": f"{drive_letter} ({total_gb} GB - {disk.fstype})" + (f" [Disk {phy_drive}]" if phy_drive is not None else ""),
                    })
                except Exception:
                    pass
        return usb_drives

    @staticmethod
    def refresh_usb_list():
        state.ventoy_usb_list = Ventoy.list_usb_drives()
        state.ventoy_selected_usb = 0

    @staticmethod
    def _clean_cli_files():
        for fname in ["cli_percent.txt", "cli_done.txt", "cli_log.txt"]:
            fpath = os.path.join(Ventoy.VENTOY_DIR, fname)
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except Exception:
                    pass

    @staticmethod
    def _read_cli_file(filename):
        fpath = os.path.join(Ventoy.VENTOY_DIR, filename)
        try:
            if os.path.exists(fpath):
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read().strip()
        except Exception:
            pass
        return ""

    @staticmethod
    def _monitor_progress():
        max_progress = 0.0
        while state.ventoy_installing:
            # Check installation phase from log to scale progress
            log_content = Ventoy._read_cli_file("cli_log.txt")
            current_phase = 1
            if log_content:
                # Phase 2 starts when it begins formatting/writing the FAT img
                if "Writing part2 FAT img" in log_content or "FormatPart2Fat" in log_content:
                    current_phase = 2
                
                # Update status if retrying to inform user
                if state.ventoy_status.startswith("Installing"):
                    if "InstallVentoy2PhyDrive try3" in log_content:
                        state.ventoy_status = "Installing (Retry 2/3)..."
                    elif "InstallVentoy2PhyDrive try2" in log_content:
                        state.ventoy_status = "Installing (Retry 1/3)..."

            percent_str = Ventoy._read_cli_file("cli_percent.txt")
            if percent_str:
                try:
                    raw_percent = int(percent_str) / 100.0
                    if current_phase == 1:
                        calculated = raw_percent * 0.30
                    else:
                        calculated = 0.30 + (raw_percent * 0.70)
                    if calculated > max_progress:
                        max_progress = calculated
                    state.ventoy_progress = min(max_progress, 0.99)
                except ValueError:
                    pass

            done_str = Ventoy._read_cli_file("cli_done.txt")
            if done_str != "":
                if done_str == "0":
                    state.ventoy_progress = 1.0
                    state.ventoy_status = "Success"
                else:
                    state.ventoy_status = "Failed"

                if log_content:
                    state.ventoy_log = log_content

                state.ventoy_installing = False
                return

            time.sleep(0.5)

    @staticmethod
    def install_ventoy(drive_letter, phy_drive=None):
        if not os.path.exists(Ventoy.VENTOY_EXE):
            state.ventoy_status = "Failed"
            state.ventoy_log = f"Ventoy exe not found at:\n{Ventoy.VENTOY_EXE}"
            return

        # Reset state
        state.ventoy_installing = True
        state.ventoy_progress = 0.0
        state.ventoy_status = "Preparing..."
        state.ventoy_log = ""

        # Clean old CLI files
        Ventoy._clean_cli_files()

        # Dismount volumes on this disk to prevent other processes from interfering
        Ventoy._prepare_disk(drive_letter, phy_drive)

        # Build command — /I = Install, /U = Update
        action = "/U" if state.ventoy_mode == 1 else "/I"
        
        # Use PhyDrive if available (more reliable), otherwise fallback to Drive letter
        if phy_drive is not None:
            cmd = [Ventoy.VENTOY_EXE, "VTOYCLI", action, f"/PhyDrive:{phy_drive}"]
        else:
            cmd = [Ventoy.VENTOY_EXE, "VTOYCLI", action, f"/Drive:{drive_letter}"]

        # Partition style
        if state.ventoy_partition_style == 1:
            cmd.append("/GPT")

        # Secure boot
        if not state.ventoy_secure_boot:
            cmd.append("/NOSB")

        # File system
        fs_name = Ventoy.FS_OPTIONS[state.ventoy_fs]
        cmd.append(f"/FS:{fs_name}")

        # Skip USB check
        cmd.append("/NOUSBCheck")

        def _run():
            try:
                monitor_thread = threading.Thread(target=Ventoy._monitor_progress, daemon=True)
                monitor_thread.start()

                if Ventoy._is_admin():
                    process = subprocess.Popen(
                        cmd,
                        cwd=Ventoy.VENTOY_DIR,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    process.wait()
                else:
                    params = " ".join(cmd[1:])
                    ret = ctypes.windll.shell32.ShellExecuteW(
                        None, "runas", cmd[0], params, Ventoy.VENTOY_DIR, 0
                    )
                    if ret <= 32:
                        state.ventoy_status = "Failed"
                        state.ventoy_log = "Failed to get administrator privileges.\nPlease run the application as administrator."
                        state.ventoy_installing = False
                        return

                    timeout = 600
                    start = time.time()
                    while state.ventoy_installing and (time.time() - start) < timeout:
                        time.sleep(1)

                    if state.ventoy_installing:
                        state.ventoy_status = "Failed"
                        state.ventoy_log = "Installation timed out (10 minutes)."
                        state.ventoy_installing = False

            except Exception as e:
                state.ventoy_status = "Failed"
                state.ventoy_log = f"Error: {str(e)}"
                state.ventoy_installing = False

        install_thread = threading.Thread(target=_run, daemon=True)
        install_thread.start()

    @staticmethod
    def _prepare_disk(drive_letter, phy_drive):
        try:
            letter = drive_letter.rstrip(":\\")
            # Dismount the volume to release all handles
            # This prevents Explorer, antivirus, etc. from interfering
            ps_script = f"""
                $letter = '{letter}'
                # Dismount volume
                $vol = Get-Volume -DriveLetter $letter -ErrorAction SilentlyContinue
                if ($vol) {{
                    $partition = Get-Partition -DriveLetter $letter -ErrorAction SilentlyContinue
                    if ($partition) {{
                        $partition | Remove-PartitionAccessPath -AccessPath "${{letter}}:\\" -ErrorAction SilentlyContinue
                    }}
                }}
                # Also set disk offline then online to force release
                $diskNum = {phy_drive if phy_drive is not None else "'unknown'"}
                if ($diskNum -ne 'unknown') {{
                    Set-Disk -Number $diskNum -IsOffline $true -ErrorAction SilentlyContinue
                    Start-Sleep -Milliseconds 500
                    Set-Disk -Number $diskNum -IsOffline $false -ErrorAction SilentlyContinue
                }}
                """
            if Ventoy._is_admin():
                subprocess.run(
                    ["powershell", "-Command", ps_script],
                    capture_output=True, text=True, timeout=15,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                pass
            time.sleep(1)
        except Exception:
            pass

    @staticmethod
    def _is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    @staticmethod
    def list_raw_usb_disks():
        raw_disks = []
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-Disk | Where-Object { $_.BusType -eq 'USB' } | Select-Object Number, FriendlyName, Size, NumberOfPartitions | ConvertTo-Json"],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0 and result.stdout.strip():
                import json
                data = json.loads(result.stdout.strip())
                if isinstance(data, dict):
                    data = [data]
                for disk in data:
                    size_gb = round(disk.get("Size", 0) / (1024**3), 2)
                    raw_disks.append({
                        "number": disk["Number"],
                        "name": disk.get("FriendlyName", "Unknown"),
                        "size_gb": size_gb,
                        "partitions": disk.get("NumberOfPartitions", 0),
                        "label": f"Disk {disk['Number']} - {disk.get('FriendlyName', 'Unknown')} ({size_gb} GB)"
                    })
        except Exception:
            pass
        return raw_disks

    @staticmethod
    def recover_usb(disk_number):
        state.ventoy_installing = True
        state.ventoy_progress = 0.0
        state.ventoy_status = "Recovering..."
        state.ventoy_log = ""

        def _run():
            try:
                ps_cmd = (
                    f"New-Partition -DiskNumber {disk_number} -UseMaximumSize -AssignDriveLetter "
                    f"| Format-Volume -FileSystem exFAT -NewFileSystemLabel 'USB' -Confirm:$false"
                )

                if Ventoy._is_admin():
                    result = subprocess.run(
                        ["powershell", "-Command", ps_cmd],
                        capture_output=True, text=True, timeout=60,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    if result.returncode == 0:
                        state.ventoy_status = "Success"
                        state.ventoy_log = "USB recovered successfully!"
                        state.ventoy_progress = 1.0
                    else:
                        state.ventoy_status = "Failed"
                        state.ventoy_log = result.stderr[:300] if result.stderr else "Recovery failed"
                else:
                    escaped_cmd = ps_cmd.replace("'", "''").replace('"', '\\"')
                    ret = ctypes.windll.shell32.ShellExecuteW(
                        None, "runas", "powershell",
                        f'-Command "{escaped_cmd}"',
                        None, 0
                    )
                    if ret <= 32:
                        state.ventoy_status = "Failed"
                        state.ventoy_log = "Failed to get admin privileges."
                    else:
                        time.sleep(5)
                        state.ventoy_status = "Success"
                        state.ventoy_log = "USB recovery command sent. Check if drive appeared."
                        state.ventoy_progress = 1.0

                state.ventoy_installing = False
            except Exception as e:
                state.ventoy_status = "Failed"
                state.ventoy_log = f"Error: {str(e)}"
                state.ventoy_installing = False

        threading.Thread(target=_run, daemon=True).start()