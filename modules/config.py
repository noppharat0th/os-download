import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class state:
    download_progress = 0.0
    is_downloading = False
    status_msg = "Ready"
    current_file = ""
    current_download_id = ""
    start_time_download = 0.0
    elapsed_time_download = 0.0

    # Ventoy installer state
    ventoy_installing = False
    ventoy_progress = 0.0
    ventoy_status = "Ready"          # "Ready", "Installing...", "Success", "Failed"
    ventoy_log = ""
    ventoy_usb_list = []
    ventoy_selected_usb = 0
    ventoy_partition_style = 0       # 0 = MBR, 1 = GPT
    ventoy_secure_boot = False
    ventoy_fs = 0                    # 0 = exFAT, 1 = NTFS, 2 = FAT32
    ventoy_mode = 0                  # 0 = Install, 1 = Update
    ventoy_raw_disks = []
    ventoy_selected_raw_disk = 0

class Config:
    color_background = (4, 4, 4, 255)
    color_secondary = (7, 7, 7, 255)
    color_border = (50, 50, 50, 80)
    color_primary = (0, 189, 253, 255)

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"