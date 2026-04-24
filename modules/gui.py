from imgui_bundle import imgui as ImGui, icons_fontawesome_6
import threading
from modules.state import state
from modules.downloads import Dowloads

class Gui():
                
    def render_screen(windows_list, linux_list):
        if state.is_downloading:
            ImGui.begin_disabled()
            ImGui.button("Downloading in progress...", ImGui.ImVec2(-1, 45))
            ImGui.end_disabled()
        else:
            Gui.os_list("Window", windows_list)
            Gui.os_list("Linux", linux_list)

        if state.is_downloading:
            ImGui.text_disabled("Please wait until the process is finished...")
    
    def os_list(label, os_list):
        ImGui.text_disabled(label)
        for item in os_list:
            clean_filename = f"{item['display_name'].replace(' ', '_')}.iso"
            ImGui.text(item['display_name'])
            disble_button = state.is_downloading

            if disble_button:
                ImGui.begin_disabled()

            if ImGui.button(f"Download##{item['id']}", ImGui.ImVec2(-1, 45)):
                threading.Thread(target=Dowloads.download_iso, args=(item['url'], clean_filename), daemon=True).start()
                
            if disble_button:
                ImGui.end_disabled()