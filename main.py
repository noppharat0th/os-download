import json
import os
from imgui_bundle import imgui as ImGui, immapp, hello_imgui, icons_fontawesome_6
from modules.downloads import Dowloads
from modules.gui import Gui
from modules.state import state

font_with_icons = None

def load_fonts():
    global font_with_icons
    font_config = ImGui.ImFontConfig()
    font_config.merge_mode = True
    font_config.pixel_snap_h = True

    io = ImGui.get_io()
    font_with_icons = io.fonts.add_font_default() 

    font_size = 16.0
    io.fonts.add_font_from_file_ttf(
        hello_imgui.asset_file_path("fonts/fontawesome-webfont.ttf"),
        font_size,
        font_config,
        icons_fontawesome_6.get_glyph_ranges_font_awesome_6()
    )

with open('os.json', 'r', encoding='utf-8') as file:
    os_data = json.load(file)

windows_list = os_data['window']
linux_list = os_data['linux']

def gui():
    if font_with_icons is not None:
        ImGui.push_font(font_with_icons)

    style = ImGui.get_style()
    ImGui.style_colors_dark()
    style.window_rounding = 15.0
    style.frame_rounding = 5.0

    ImGui.set_next_window_size(ImGui.ImVec2(750, 500), ImGui.Cond_.always)
    ImGui.push_style_var(ImGui.StyleVar_.window_padding, ImGui.ImVec2(0, 0))
    ImGui.push_style_color(ImGui.Col_.window_bg, ImGui.ImColor(4, 4, 4, 255).value)
    ImGui.push_style_color(ImGui.Col_.border, ImGui.ImColor(0, 0, 0, 255).value)
    ImGui.begin("ISO Downloader", None, ImGui.WindowFlags_.no_title_bar | ImGui.WindowFlags_.no_resize) 

    Gui.render_screen(windows_list, linux_list)

    # ImGui.spacing()
    # ImGui.progress_bar(state.download_progress, ImGui.ImVec2(-1, 25), f"{state.download_progress*100:.1f}%")
    ImGui.end()
    ImGui.pop_style_color(2)
    ImGui.pop_style_var()

    if font_with_icons is not None:
        ImGui.pop_font()

def render():
    immapp.run(gui_function=gui, window_title="OS Downloader", window_size=(500, 400))

if __name__ == "__main__":
    render()