
import time

import cv2
from glm import pos
from imgui_bundle import ImColor, imgui as ImGui, icons_fontawesome_6, immvision
import threading
from modules.config import state, Config
from modules.downloads import Dowloads
from modules.overlay import Particle

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
    current_page = "Home"
    particles = []
    progress_states = {}
    last_time = time.time()
    os_images = {}
    logo = None

    # overlay
    def render_particles():
        draw_list = ImGui.get_window_draw_list()
        window_pos = ImGui.get_window_pos()
        window_size = ImGui.get_window_size()
        
        if not Gui.particles:
            for _ in range(50):
                Gui.particles.append(Particle(window_size.x, window_size.y))

        for p in Gui.particles:
            p.update(window_size.x, window_size.y)
            draw_pos = ImGui.ImVec2(window_pos.x + p.pos[0], window_pos.y + p.pos[1])
            
            draw_list.add_circle_filled(
                draw_pos, 
                p.size, 
                p.color
            )

    # load image from assets
    def load_assets(windows_list, linux_list):
        immvision.use_rgb_color_order() 
        # img = cv2.imread("assets/arch-linux.png")
        # logo = cv2.imread("assets/logo.png")

        all_os = windows_list + linux_list

        for os in all_os:
            img_path = os.get('img', 'assets/linux.jpg')
            img = cv2.imread(img_path)
            Gui.os_images[os['id']] = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # render screen main
    def render_screen(windows_list, linux_list):
        if not Gui.os_images:
            Gui.load_assets(windows_list, linux_list)

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
                is_active = (Gui.current_page == item['name'])
                if Gui.draw_tab_menu(item['icon'], item['name'], is_active):
                    Gui.current_page = item['name']
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
        if Gui.current_page == "Home":
            Gui.card_show_os("Window", windows_list)
            Gui.card_show_os("Linux", linux_list)

        ImGui.end_group()
        ImGui.pop_style_var()
    
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
        
    def draw_tab_menu(icon, label_id, is_active=False):
        btn_width = 60
        ImGui.set_cursor_pos_x((90 - btn_width) / 2)

        if is_active:
            ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(*Config.color_primary).value)
        else:
            ImGui.push_style_color(ImGui.Col_.text, ImGui.ImVec4(0.5, 0.5, 0.5, 1.0))

        ImGui.push_style_color(ImGui.Col_.button, ImGui.ImVec4(0, 0, 0, 0))
        ImGui.push_style_color(ImGui.Col_.border, ImGui.ImVec4(0, 0, 0, 0))
        ImGui.push_style_color(ImGui.Col_.button_hovered, ImGui.ImVec4(0, 0, 0, 0))
        ImGui.push_style_color(ImGui.Col_.button_active, ImGui.ImVec4(0, 0, 0, 0))
        
        clicked = ImGui.button(f"{icon}##{label_id}", ImGui.ImVec2(btn_width, 60))
        ImGui.pop_style_color(5)
        
        return clicked

    def navbar():
        avail = ImGui.get_content_region_avail()

        ImGui.push_style_color(ImGui.Col_.border, ImGui.ImColor(*Config.color_border).value) 
        ImGui.push_style_color(ImGui.Col_.child_bg, ImGui.ImColor(*Config.color_secondary).value)
        
        ImGui.push_style_var(ImGui.StyleVar_.child_rounding, 5.0)
        if ImGui.begin_child("navbar", ImGui.ImVec2(avail.x, 50), ImGui.ChildFlags_.borders):
            ImGui.set_cursor_pos_y(15) 
            ImGui.set_cursor_pos_x(15)
            ImGui.text_disabled("")
            
        ImGui.end_child()

        ImGui.pop_style_var()
        ImGui.pop_style_color(2)

    def card_show_os(label, os_list):
        content_avail = ImGui.get_content_region_avail()
        ImGui.push_style_var(ImGui.StyleVar_.window_padding, ImGui.ImVec2(15, 15))
        ImGui.push_style_var(ImGui.StyleVar_.item_spacing, ImGui.ImVec2(10, 10))
        
        if ImGui.begin_child("content", ImGui.ImVec2(content_avail.x, content_avail.y), ImGui.ChildFlags_.borders, ImGui.WindowFlags_.no_scrollbar):
            

            # ImGui.text_colored(ImGui.ImVec4(0.6, 0.6, 0.6, 1.0), label)
            Gui.title_os(label, "hello download os from me")
            ImGui.spacing()

            for item in os_list:
                ImGui.push_style_var(ImGui.StyleVar_.child_rounding, 5.0)                
                ImGui.push_style_var(ImGui.StyleVar_.window_padding, ImGui.ImVec2(25, 25))                
                ImGui.push_style_color(ImGui.Col_.border, ImGui.ImColor(*Config.color_border).value)
                ImGui.push_style_color(ImGui.Col_.child_bg, ImGui.ImColor(*Config.color_secondary).value)
                if ImGui.begin_child(f"card_{item['id']}", ImGui.ImVec2(-15, 180), ImGui.ChildFlags_.borders, ImGui.WindowFlags_.no_scrollbar | ImGui.WindowFlags_.no_scroll_with_mouse):

                    # Card image
                    current_img = Gui.os_images.get(item['id'])

                    if current_img is not None:
                        params = immvision.ImageParams()
                        params.show_image_info = False
                        params.show_zoom_buttons = False
                        params.show_pixel_info = False
                        params.show_options_button = False
                        params.show_options_panel = False
                        params.can_resize = False
                        scale = 0.5
                        width = int(440 * scale)
                        height = int(272 * scale)
                        
                        params.image_display_size = (width, height) 
                        immvision.image(f"##img_{item['id']}", current_img, params)

                        ImGui.same_line()

                        # Card info
                        pos = ImGui.get_cursor_pos()
                        ImGui.set_cursor_pos_x(pos.x + 17)
                        ImGui.begin_group()
                        ImGui.text(item['display_name'])
    
                        ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(150, 150, 150, 255).value)
                        ImGui.push_text_wrap_pos(ImGui.get_cursor_pos().x + 300)
                        
                        ImGui.text("Lorem Ipsum is simply dummy text of the printing and typesetting")
                        ImGui.pop_style_color()
                        ImGui.pop_text_wrap_pos()

                        ImGui.spacing()
                        ImGui.text("status :")
                        ImGui.same_line()
                        ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(*Config.color_primary).value)
                        ImGui.text("active")
                        ImGui.pop_style_color()
                        ImGui.same_line()

                        button_width = 100
                        right_padding = 10

                        target_x = ImGui.get_window_width() - button_width - right_padding
                        ImGui.set_cursor_pos_x(target_x)
                        if ImGui.button("DownLoad", ImGui.ImVec2(button_width, 30)):
                            pass
                        
                        download_percent = 0.65 
                        Gui.progress("download_id_1", download_percent)
                        ImGui.end_group()

                        
                ImGui.end_child()
                ImGui.pop_style_color(2)
                ImGui.pop_style_var(2)

        ImGui.end_child()
        ImGui.pop_style_var(2)


    def progress(id, fraction, width=-1, height=12):
        if width == -1:
            width = ImGui.get_content_region_avail().x
        
        p_min = ImGui.get_cursor_screen_pos()
        p_max = ImGui.ImVec2(p_min.x + width, p_min.y + height)
        draw_list = ImGui.get_window_draw_list()

        current_time = time.time()
        dt = current_time - Gui.last_time
        Gui.last_time = current_time
        
        anim_val = Gui.progress_states.get(id, 0.0)
        anim_val += (fraction - anim_val) * (5.0 * dt)
        Gui.progress_states[id] = anim_val

        bg_color = ImGui.get_color_u32(ImGui.ImColor(30, 30, 35, 255).value)
        draw_list.add_rect_filled(p_min, p_max, bg_color, 10.0)

        if anim_val > 0.01:
            bar_max_x = p_min.x + (width * anim_val)
            bar_p_max = ImGui.ImVec2(bar_max_x, p_max.y)

            primary_col = ImGui.ImColor(*Config.color_primary).value

            glow_col = ImGui.get_color_u32(ImGui.ImColor(
                Config.color_primary[0], 
                Config.color_primary[1], 
                Config.color_primary[2], 0.3).value)
            
            draw_list.add_rect_filled(p_min, bar_p_max, ImGui.get_color_u32(primary_col), 10.0)
            
            draw_list.add_line(
                ImGui.ImVec2(p_min.x + 5, p_min.y + 3),
                ImGui.ImVec2(bar_max_x - 5, p_min.y + 3),
                ImGui.get_color_u32(ImGui.ImColor(255, 255, 255, 50).value), 1.0
            )
            
        ImGui.set_cursor_screen_pos(ImGui.ImVec2(p_min.x, p_max.y + 5))
        ImGui.dummy(ImGui.ImVec2(width, height))

    def title_os(title_text="ass", desc_text="ss"):
        draw = ImGui.get_window_draw_list()
        pos = ImGui.get_cursor_screen_pos()
        
        box_size = 45.0
        rounding = 8.0

        draw.add_rect_filled(
            pos,
            ImGui.ImVec2(pos.x + box_size, pos.y + box_size),
            ImGui.get_color_u32(ImColor(*Config.color_secondary).value),
            rounding
        )
        draw.add_rect(
            pos,
            ImGui.ImVec2(pos.x + box_size, pos.y + box_size),
            ImGui.get_color_u32(ImColor(*Config.color_border).value),
            rounding, 0, 1.2
        )

        icon_text = "OS"
        text_size = ImGui.calc_text_size(icon_text)
        draw.add_text(
            ImGui.ImVec2(pos.x + (box_size - text_size.x)/2, pos.y + (box_size - text_size.y)/2), 
            ImGui.get_color_u32(ImColor(*Config.color_primary).value), 
            icon_text
        )

        title_size = ImGui.calc_text_size(title_text)
        desc_size = ImGui.calc_text_size(desc_text)
        
        item_spacing_y = 2.0
        
        total_text_height = title_size.y + desc_size.y + item_spacing_y
        
        start_y_offset = (box_size - total_text_height) / 2.0

        ImGui.set_cursor_screen_pos(ImGui.ImVec2(pos.x + box_size + 15, pos.y + start_y_offset))
        
        ImGui.begin_group()
        
        ImGui.text(title_text)

        ImGui.set_cursor_pos_y(ImGui.get_cursor_pos_y() - 5)
        
        ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(150, 150, 150, 255).value)
        ImGui.text(desc_text)
        ImGui.pop_style_color()
        
        ImGui.end_group()