import json
import threading
import os
from imgui_bundle import imgui as ImGui, immapp
from modules.downloads import Dowloads

class AppState:
    download_progress = 0.0
    is_downloading = False
    status_msg = "Ready"
    current_file = ""
state = AppState()

with open('os.json', 'r', encoding='utf-8') as file:
    os_data = json.load(file)

windows_list = os_data['window']
linux_list = os_data['linux']

def download_iso(url, filename):
    state.is_downloading = True
    state.status_msg = f"Downloading {filename}..."
    state.current_file = filename
    state.download_progress = 0.0
    
    def on_progress(p):
        state.download_progress = p 

    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    save_path = f"downloads/{filename}"
    success = Dowloads.start_download(url, save_path, on_progress)
    
    if success:
        state.status_msg = f"{filename} Downloaded"
    else:
        state.status_msg = "download failed"
    
    state.is_downloading = False
    state.current_file = ""

def gui():
    style = ImGui.get_style()
    ImGui.style_colors_dark()
    style.window_rounding = 15.0
    style.frame_rounding = 5.0

    ImGui.set_next_window_size(ImGui.ImVec2(500, 400), ImGui.Cond_.always)
    ImGui.set_next_window_pos(ImGui.ImVec2(0, 0))
    
    ImGui.begin("ISO Downloader", None, ImGui.WindowFlags_.no_title_bar | ImGui.WindowFlags_.no_resize) 
    ImGui.spacing()

    if state.is_downloading:
        ImGui.begin_disabled()
        ImGui.button("Downloading in progress...", ImGui.ImVec2(-1, 45))
        ImGui.end_disabled()
    else:
        os_list("Window", windows_list)
        os_list("Linux", linux_list)

    if state.is_downloading:
        ImGui.text_disabled("Please wait until the process is finished...")

    ImGui.spacing()
    ImGui.progress_bar(state.download_progress, ImGui.ImVec2(-1, 25), f"{state.download_progress*100:.1f}%")
    ImGui.end()

def os_list(label, os_list):
    ImGui.text_disabled(label)
    for item in os_list:
        clean_filename = f"{item['display_name'].replace(' ', '_')}.iso"
        ImGui.text(item['display_name'])
        disble_button = state.is_downloading

        if disble_button:
            ImGui.begin_disabled()

        if ImGui.button(f"Download##{item['id']}", ImGui.ImVec2(-1, 45)):
            threading.Thread(target=download_iso, args=(item['url'], clean_filename), daemon=True).start()
            
        if disble_button:
            ImGui.end_disabled()

def render():
    immapp.run(gui_function=gui, window_title="OS Downloader", window_size=(500, 400))

if __name__ == "__main__":
    render()