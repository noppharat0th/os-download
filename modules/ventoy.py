import psutil
import subprocess
import os
import threading

class Ventoy:
    def start_install(drive):
        pass

    def list_usb_driver():
        usb_drivers = []
        for disk in psutil.disk_partitions():
            if 'removable' in disk.opts or disk.fstype == '':
                usb_drivers.append({
                    "device": disk.device,
                    "mountpoint": disk.mountpoint,
                    "fstype": disk.fstype
                })
        return usb_drivers
    
    def install_ventoy(physical_drive, install_path="bin/Ventoy2Disk.exe"):

        if not os.path.exists(install_path):
            return False
        
        try:
            command = [install_path, "-i", "-f", physical_drive]
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                return True
            else:
                return False
        except Exception as e:
            return False