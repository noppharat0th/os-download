class state:
    download_progress = 0.0
    is_downloading = False
    status_msg = "Ready"
    current_file = ""
    current_download_id = ""
    start_time_download = 0.0
    elapsed_time_download = 0.0

class Config:
    color_background = (4, 4, 4, 255)
    color_secondary = (7, 7, 7, 255)
    color_border = (50, 50, 50, 80)
    color_primary = (0, 189, 253, 255)

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"