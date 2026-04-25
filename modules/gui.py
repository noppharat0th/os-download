import cv2
from glm import pos
from imgui_bundle import imgui as ImGui, icons_fontawesome_6, immvision
import threading
from modules.config import state, Config
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
    window_img = None

    def load_assets():
        immvision.use_rgb_color_order() 
        img = cv2.imread("assets/linux.jpg")
        if img is not None:
            Gui.window_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            print("not found image")

    def render_screen(windows_list, linux_list):
        if Gui.window_img is None:
            Gui.load_assets()

        p = ImGui.get_cursor_screen_pos()
        draw_list = ImGui.get_window_draw_list()
        tab_bar_width = 90
        full_height = ImGui.get_content_region_avail().y 

        # SIDEBAR
        draw_list.add_rect_filled(
            p, 
            ImGui.ImVec2(p.x + tab_bar_width, p.y + full_height), 
            ImGui.get_color_u32(ImGui.ImColor(*Config.color_secondary).value), 
            15.0,
            ImGui.ImDrawFlags_.round_corners_left
        )

        draw_list.add_rect(
            p, 
            ImGui.ImVec2(p.x + tab_bar_width, p.y + full_height), 
            ImGui.get_color_u32(ImGui.ImColor(*Config.color_border).value),
            15.0,
            ImGui.ImDrawFlags_.round_corners_left,
            1.0
        )

        ImGui.push_style_color(ImGui.Col_.child_bg, ImGui.ImColor(0, 0, 0, 0).value)
        if ImGui.begin_child("sidebar", ImGui.ImVec2(tab_bar_width, full_height)):
            for item in tab_menu:
                Gui.draw_tab_menu(item['icon'], item['name'])
        ImGui.end_child()
        ImGui.pop_style_color()   

        ImGui.push_style_var(ImGui.StyleVar_.item_spacing, ImGui.ImVec2(0, 20))

        ImGui.same_line() 

        ImGui.begin_group()

        # NAVBAR
        Gui.navbar()
        
        # CONTENT
        margin_x = 20.0
        margin_y = 20.0
        current_pos = ImGui.get_cursor_pos()
        ImGui.set_cursor_pos(ImGui.ImVec2(current_pos.x + margin_x, current_pos.y + margin_y))
        Gui.card_show_os("Window", windows_list)
        Gui.card_show_os("Linux", linux_list)

        ImGui.end_group()
        ImGui.pop_style_var(1)
    
    # def os_list(label, os_list):
    #     ImGui.text_disabled(label)
    #     for item in os_list:
    #         clean_filename = f"{item['display_name'].replace(' ', '_')}.iso"
    #         ImGui.text(item['display_name'])
    #         disble_button = state.is_downloading

    #         if disble_button:
    #             ImGui.begin_disabled()

    #         if ImGui.button(f"Download##{item['id']}", ImGui.ImVec2(-1, 45)):
    #             threading.Thread(target=Dowloads.download_iso, args=(item['url'], clean_filename), daemon=True).start()
                
    #         if disble_button:
    #             ImGui.end_disabled()
        
    def draw_tab_menu(icon, label_id):
        btn_width = 60
        ImGui.set_cursor_pos_x((tab_bar_width - btn_width) / 2)

        ImGui.push_style_color(ImGui.Col_.button, ImGui.ImVec4(0, 0, 0, 0))
        ImGui.push_style_color(ImGui.Col_.border, ImGui.ImVec4(0, 0, 0, 0))
        ImGui.push_style_color(ImGui.Col_.button_hovered, ImGui.ImVec4(0, 0, 0, 0))
        ImGui.push_style_color(ImGui.Col_.button_active, ImGui.ImVec4(0, 0, 0, 0))
        
        if ImGui.button(f"{icon}##{label_id}", ImGui.ImVec2(btn_width, 60)):
            print(f"Clicked {label_id}")

        ImGui.pop_style_color(4)

    def navbar():
        avail = ImGui.get_content_region_avail()

        ImGui.push_style_color(ImGui.Col_.border, ImGui.ImColor(*Config.color_border).value) 
        ImGui.push_style_color(ImGui.Col_.child_bg, ImGui.ImColor(*Config.color_secondary).value)
        
        ImGui.push_style_var(ImGui.StyleVar_.child_rounding, 5.0)
        if ImGui.begin_child("navbar", ImGui.ImVec2(avail.x, 50), ImGui.ChildFlags_.borders):
            ImGui.set_cursor_pos_y(15) 
            ImGui.set_cursor_pos_x(15)
            ImGui.text_disabled("OS DOWNLOADER > WINDOWS")
            
        ImGui.end_child()

        ImGui.pop_style_var()
        ImGui.pop_style_color(2)

    def card_show_os(label, os_list):
        content_avail = ImGui.get_content_region_avail()
        ImGui.push_style_var(ImGui.StyleVar_.window_padding, ImGui.ImVec2(15, 15))
        ImGui.push_style_var(ImGui.StyleVar_.item_spacing, ImGui.ImVec2(10, 10))
        
        if ImGui.begin_child("content", ImGui.ImVec2(content_avail.x, content_avail.y)):
                
            ImGui.text_colored(ImGui.ImVec4(0.6, 0.6, 0.6, 1.0), label)
            ImGui.spacing()

            for item in os_list:
                ImGui.push_style_color(ImGui.Col_.child_bg, ImGui.ImColor(20, 20, 20, 255).value)
                if ImGui.begin_child(f"card_{item['id']}", ImGui.ImVec2(-15, 180), ImGui.ChildFlags_.borders):
                    if Gui.window_img is not None:
                        params = immvision.ImageParams()
                        params.show_image_info = False
                        params.show_zoom_buttons = False
                        params.show_pixel_info = False
                        params.show_options_button = False
                        params.show_options_panel = False
                        params.image_display_size = (60, 60)
                        immvision.image(f"##{label}", Gui.window_img, params)
                ImGui.end_child()
                ImGui.pop_style_color()

        ImGui.end_child()
        ImGui.pop_style_var(2)
