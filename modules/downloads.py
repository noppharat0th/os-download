import stat
import time

import requests
import os
from modules.config import state

class Dowloads:
    @staticmethod
    def start_download(url, save_path, progress_callback):
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            response = requests.get(url, stream=True, allow_redirects=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(save_path, 'wb') as f:
                if total_size == 0:
                    f.write(response.content)
                else:
                    downloaded = 0
                    for data in response.iter_content(chunk_size=4096):
                        downloaded += len(data)
                        f.write(data)
                    
                        progress = downloaded / total_size
                        progress_callback(progress)
            return True
        except Exception as e:
            print(e)
            return False
        
    def download_iso(url, filename, save_dir=None):
        state.is_downloading = True
        state.status_msg = f"Downloading {filename}..."
        state.current_file = filename
        state.download_progress = 0.0
        state.start_time = time.time()
        
        def on_progress(p):
            state.download_progress = p 
            state.elapsed_time_download = time.time() - state.start_time

        if save_dir is None:
            save_dir = "downloads"
        
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        save_path = os.path.join(save_dir, filename)
        success = Dowloads.start_download(url, save_path, on_progress)
        
        if success:
            state.status_msg = f"{filename} Downloaded"
        else:
            state.status_msg = "download failed"
        
        state.is_downloading = False
        state.current_file = ""