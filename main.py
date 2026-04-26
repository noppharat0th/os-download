import json
import os
from imgui_bundle import imgui as ImGui, immapp, hello_imgui, icons_fontawesome_6
from modules import config
from modules.downloads import Dowloads
from modules.gui import Gui
from modules.config import state, Config, resource_path
from modules.ventoy import Ventoy

font_with_icons = None
font_with_icons = None

with open(resource_path('os.json'), 'r', encoding='utf-8') as file:
    os_data = json.load(file)

windows_list = os_data['window']
linux_list = os_data['linux']

def gui():

    style = ImGui.get_style()
    ImGui.style_colors_dark()
    style.window_rounding = 15.0
    style.frame_rounding = 5.0

    ImGui.set_next_window_pos(ImGui.ImVec2(0, 0), ImGui.Cond_.always)
    ImGui.set_next_window_size(ImGui.ImVec2(900, 600), ImGui.Cond_.always)
    ImGui.push_style_var(ImGui.StyleVar_.window_padding, ImGui.ImVec2(0, 0))
    ImGui.push_style_color(ImGui.Col_.window_bg, ImGui.ImColor(*Config.color_background).value)
    ImGui.push_style_color(ImGui.Col_.border, ImGui.ImColor(0, 0, 0, 0).value) # Remove border line
    ImGui.begin("ISO Downloader", None, ImGui.WindowFlags_.no_title_bar | ImGui.WindowFlags_.no_resize | ImGui.WindowFlags_.no_move | ImGui.WindowFlags_.no_collapse | ImGui.WindowFlags_.no_bring_to_front_on_focus) 

    Gui.render_screen(windows_list, linux_list)
    Gui.render_particles()

    # ImGui.spacing()
    # ImGui.progress_bar(state.download_progress, ImGui.ImVec2(-1, 25), f"{state.download_progress*100:.1f}%")
    ImGui.end()
    ImGui.pop_style_color(2)
    ImGui.pop_style_var()

def render():
    runner_params = immapp.RunnerParams()
    runner_params.app_window_params.window_title = "OS Downloader"
    runner_params.app_window_params.window_geometry.size = (900, 600)
    runner_params.app_window_params.resizable = False
    runner_params.imgui_window_params.default_imgui_window_type = hello_imgui.DefaultImGuiWindowType.no_default_window
    runner_params.callbacks.show_gui = gui
    runner_params.callbacks.default_icon_font = hello_imgui.DefaultIconFont.font_awesome6
    
    immapp.run(runner_params=runner_params)

if __name__ == "__main__":
    render()