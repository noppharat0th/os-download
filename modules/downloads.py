import requests
import os

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