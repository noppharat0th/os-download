from imgui_bundle import imgui as ImGui, icons_fontawesome_6
import threading
from modules.state import state
from modules.downloads import Dowloads

tab_bar_width = 90
tab_menu = [
    {
        "id": 1,
        "name": "Home",
        "icon": icons_fontawesome_6.ICON_FA_HOUSE
    },
    {
        "id": 2,
        "name": "Settings",
        "icon": icons_fontawesome_6.ICON_FA_GEAR
    },
]

class Gui():
                
    def render_screen(windows_list, linux_list):
        p = ImGui.get_cursor_screen_pos()
        draw_list = ImGui.get_window_draw_list()
        rounding = 15.0

        draw_list.add_rect_filled(
            p, 
            ImGui.ImVec2(p.x + tab_bar_width, p.y + 470), 
            ImGui.get_color_u32(ImGui.ImColor(19, 19, 19, 255).value), 
            rounding,
            ImGui.ImDrawFlags_.round_corners_left
        )

        ImGui.push_style_color(ImGui.Col_.child_bg, ImGui.ImColor(0, 0, 0, 0).value)
        ImGui.push_style_var(ImGui.StyleVar_.window_padding, ImGui.ImVec2(0, 0))

        if ImGui.begin_child("tabbar", ImGui.ImVec2(tab_bar_width, 470)):
            for item in tab_menu:
                Gui.drwa_tab_menu(item['icon'], item['name'])

        ImGui.end_child()
        ImGui.pop_style_var()
        ImGui.pop_style_color()


        # if state.is_downloading:
        #     ImGui.begin_disabled()
        #     ImGui.button("Downloading in progress...", ImGui.ImVec2(-1, 45))
        #     ImGui.end_disabled()
        # else:
        #     Gui.os_list("Window", windows_list)
        #     Gui.os_list("Linux", linux_list)

        # if state.is_downloading:
        #     ImGui.text_disabled("Please wait until the process is finished...")
    
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
        
    def drwa_tab_menu(icon, label_id):
        btn_width = 60
        ImGui.set_cursor_pos_x((tab_bar_width - btn_width) / 2)

        ImGui.push_style_color(ImGui.Col_.button, ImGui.ImVec4(0, 0, 0, 0))
        ImGui.push_style_color(ImGui.Col_.border, ImGui.ImVec4(0, 0, 0, 0))
        ImGui.push_style_color(ImGui.Col_.button_hovered, ImGui.ImVec4(0, 0, 0, 0))
        ImGui.push_style_color(ImGui.Col_.button_active, ImGui.ImVec4(0, 0, 0, 0))
        
        if ImGui.button(f"{icon}##{label_id}", ImGui.ImVec2(btn_width, 60)):
            print(f"Clicked {label_id}")

        ImGui.pop_style_color(4)