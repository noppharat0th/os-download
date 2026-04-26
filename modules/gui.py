
from gettext import install
import time

import cv2
from glm import pos
from imgui_bundle import ImColor, imgui as ImGui, icons_fontawesome_6, immvision, imspinner
import threading
from modules.config import state, Config, format_time, resource_path
from modules.downloads import Dowloads
from modules.ventoy import Ventoy
from modules.overlay import Particle
from modules.ui import UI

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
    selected_usb_index = 0
    search_query = ""
    os_filter = "All"

    @staticmethod
    def render_home_controls():
        ImGui.push_style_var(ImGui.StyleVar_.window_padding, ImGui.ImVec2(0, 0))
        ImGui.push_style_var(ImGui.StyleVar_.item_spacing, ImGui.ImVec2(10, 10))
        ImGui.push_style_color(ImGui.Col_.child_bg, ImGui.ImColor(0, 0, 0, 0).value)
        ImGui.push_style_color(ImGui.Col_.border, ImGui.ImColor(0, 0, 0, 0).value)

        content_avail = ImGui.get_content_region_avail()
        if ImGui.begin_child("home_controls", ImGui.ImVec2(content_avail.x, 40), ImGui.ChildFlags_.borders):
            ImGui.set_cursor_pos_y(5)
            
            # Filter Buttons
            filters = ["All", "Window", "Linux"]
            for f in filters:
                if Gui.os_filter == f:
                    ImGui.push_style_color(ImGui.Col_.button, ImGui.ImColor(*Config.color_primary).value)
                    ImGui.push_style_color(ImGui.Col_.button_hovered, ImGui.ImColor(*Config.color_primary).value)
                    ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(255, 255, 255, 255).value)
                else:
                    ImGui.push_style_color(ImGui.Col_.button, ImGui.ImColor(30, 30, 40, 255).value)
                    ImGui.push_style_color(ImGui.Col_.button_hovered, ImGui.ImColor(45, 45, 55, 255).value)
                    ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(150, 150, 150, 255).value)
                
                if ImGui.button(f, ImGui.ImVec2(80, 30)):
                    Gui.os_filter = f
                    
                ImGui.pop_style_color(3)
                ImGui.same_line()

            # Search bar
            ImGui.same_line(ImGui.get_window_width() - 260)
            ImGui.set_next_item_width(230)
            ImGui.push_style_color(ImGui.Col_.frame_bg, ImGui.ImColor(25, 25, 35, 255).value)
            ImGui.push_style_color(ImGui.Col_.border, ImGui.ImColor(*Config.color_border).value)
            ImGui.push_style_var(ImGui.StyleVar_.frame_padding, ImGui.ImVec2(10, 10))
            changed, Gui.search_query = ImGui.input_text_with_hint("##search", f"{icons_fontawesome_6.ICON_FA_MAGNIFYING_GLASS} Search OS...", Gui.search_query)
            ImGui.pop_style_var()
            ImGui.pop_style_color(2)

        ImGui.end_child()
        ImGui.pop_style_color(2)
        ImGui.pop_style_var(2)

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

    @staticmethod
    def load_assets(windows_list, linux_list):
        immvision.use_rgb_color_order() 

        all_os = windows_list + linux_list

        for os in all_os:
            img_path = os.get('img', 'assets/linux.jpg')
            img = cv2.imread(resource_path(img_path))
            
            # Additional fallback check if OpenCV fails to read the first path
            if img is None:
                img = cv2.imread(resource_path('assets/linux.jpg'))
                
            if img is not None:
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
                if UI.glow_icon_button(item['icon'], item['name'], is_active):
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
            Gui.render_home_controls()
            
            filtered_windows = [os for os in windows_list if Gui.search_query.lower() in os['display_name'].lower()]
            filtered_linux = [os for os in linux_list if Gui.search_query.lower() in os['display_name'].lower()]

            if Gui.os_filter in ["All", "Window"] and filtered_windows:
                Gui.card_show_os("Window", filtered_windows)
            if Gui.os_filter in ["All", "Linux"] and filtered_linux:
                Gui.card_show_os("Linux", filtered_linux)
                
            if not filtered_windows and not filtered_linux:
                ImGui.spacing()
                ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(150, 150, 150, 255).value)
                ImGui.text(f"{icons_fontawesome_6.ICON_FA_MAGNIFYING_GLASS} No OS found for '{Gui.search_query}'")
                ImGui.pop_style_color()

        elif Gui.current_page == "Settings":
            Gui.render_ventoy_page()

        ImGui.end_group()
        ImGui.pop_style_var()
    
        
    # draw_tab_menu is replaced by UI.glow_icon_button

    def navbar():
        avail = ImGui.get_content_region_avail()

        ImGui.push_style_color(ImGui.Col_.border, ImGui.ImColor(*Config.color_border).value) 
        ImGui.push_style_color(ImGui.Col_.child_bg, ImGui.ImColor(*Config.color_secondary).value)
        
        ImGui.push_style_var(ImGui.StyleVar_.child_rounding, 5.0)
        if ImGui.begin_child("navbar", ImGui.ImVec2(avail.x, 50), ImGui.ChildFlags_.borders):
            # Auto-scan USB
            if not state.ventoy_usb_list:
                Ventoy.refresh_usb_list()

            # Page title (left)
            ImGui.set_cursor_pos_y(15)
            ImGui.set_cursor_pos_x(15)
            ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(220, 220, 220, 255).value)
            ImGui.text(Gui.current_page)
            ImGui.pop_style_color()

            # ── Right side: Save to dropdown + refresh ──
            dropdown_width = 260
            refresh_width = 28
            right_padding = 12
            total_right = dropdown_width + refresh_width + 8 + right_padding

            navbar_width = avail.x
            start_x = navbar_width - total_right

            ImGui.set_cursor_pos(ImGui.ImVec2(start_x, 11))

            # Build items for dropdown: "Local" + USB drives
            combo_labels = [f"{icons_fontawesome_6.ICON_FA_FOLDER_OPEN}  Local (downloads/)"]
            for usb in state.ventoy_usb_list:
                combo_labels.append(f"{icons_fontawesome_6.ICON_FA_HARD_DRIVE}  {usb['label']}")

            # combo index: 0 = local, 1+ = usb
            combo_idx = state.download_selected_usb + 1
            if combo_idx >= len(combo_labels):
                combo_idx = 0
                state.download_selected_usb = -1

            changed, new_idx = UI.dropdown("dl_dest", combo_labels, combo_idx, width=dropdown_width)
            if changed:
                state.download_selected_usb = new_idx - 1

            ImGui.same_line()
            ImGui.set_cursor_pos_y(11)

            # Refresh button
            if UI.icon_button(icons_fontawesome_6.ICON_FA_ARROWS_ROTATE, "refresh_dl_usb", size=refresh_width):
                Ventoy.refresh_usb_list()
                state.download_selected_usb = -1
            
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

                        if state.is_downloading and state.current_download_id == item['id']:
                            time_str = format_time(state.elapsed_time_download)
                            ImGui.text("time :")
                            ImGui.same_line()
                            ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(*Config.color_primary).value)
                            ImGui.text(time_str)
                        else :
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

                        if state.is_downloading :
                            ImGui.begin_disabled()
                            ImGui.button("Loading", ImGui.ImVec2(button_width, 30))
                            ImGui.end_disabled()
                        else:
                            if ImGui.button("DownLoad", ImGui.ImVec2(button_width, 30)):
                                state.current_download_id = item['id']
                                clean_filename = f"{item['display_name'].replace(' ', '_')}.iso"
                                # Determine save directory
                                save_dir = None
                                if state.download_selected_usb >= 0 and state.download_selected_usb < len(state.ventoy_usb_list):
                                    usb = state.ventoy_usb_list[state.download_selected_usb]
                                    save_dir = usb["mountpoint"]
                                threading.Thread(target=Dowloads.download_iso, args=(item['url'], clean_filename, save_dir), daemon=True).start()
                        
                        if state.is_downloading and state.current_download_id == item['id'] :
                            download_percent = state.download_progress
                            Gui.progress(f"dl_{item['id']}", download_percent)
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
        anim_val += (fraction - anim_val) * (7.0 * dt)
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

    def render_ventoy_page():
        content_avail = ImGui.get_content_region_avail()

        ImGui.push_style_var(ImGui.StyleVar_.window_padding, ImGui.ImVec2(20, 20))
        ImGui.push_style_var(ImGui.StyleVar_.item_spacing, ImGui.ImVec2(10, 10))
        ImGui.push_style_color(ImGui.Col_.child_bg, ImGui.ImColor(0, 0, 0, 0).value)
        ImGui.push_style_color(ImGui.Col_.border, ImGui.ImColor(*Config.color_border).value)

        if ImGui.begin_child("ventoy_page", ImGui.ImVec2(content_avail.x - 20, content_avail.y - 10), ImGui.ChildFlags_.borders):

            # ── Title ──
            Gui.title_os("Ventoy Installer", "Install Ventoy to USB Drive")
            ImGui.spacing()
            ImGui.spacing()

            # ── USB Drive Selection Section ──
            Gui._section_header(icons_fontawesome_6.ICON_FA_DIAMOND, "Select USB Drive")
            ImGui.spacing()

            # Refresh USB list if empty
            if not state.ventoy_usb_list:
                Ventoy.refresh_usb_list()

            # Build items list for custom dropdown
            usb_labels = [usb["label"] for usb in state.ventoy_usb_list]
            if not usb_labels:
                usb_labels = ["No USB Found"]

            dropdown_width = ImGui.get_content_region_avail().x - 120
            changed, state.ventoy_selected_usb = UI.dropdown(
                "ventoy_usb_select", 
                usb_labels, 
                state.ventoy_selected_usb, 
                width=dropdown_width
            )

            ImGui.same_line()

            # Refresh button
            ImGui.push_style_color(ImGui.Col_.button, ImGui.ImColor(30, 30, 40, 255).value)
            ImGui.push_style_color(ImGui.Col_.button_hovered, ImGui.ImColor(45, 45, 55, 255).value)
            ImGui.push_style_color(ImGui.Col_.button_active, ImGui.ImColor(55, 55, 65, 255).value)
            if ImGui.button(f"{icons_fontawesome_6.ICON_FA_ARROWS_ROTATE}  Refresh##refresh_usb", ImGui.ImVec2(105, 0)):
                Ventoy.refresh_usb_list()
            ImGui.pop_style_color(3)

            ImGui.spacing()
            ImGui.separator()
            ImGui.spacing()

            # ── Options Section ──
            Gui._section_header(icons_fontawesome_6.ICON_FA_SLIDERS, "Installation Options")
            ImGui.spacing()

            # Mode (Install / Update)
            ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(180, 180, 180, 255).value)
            ImGui.text("Mode")
            ImGui.pop_style_color()
            ImGui.same_line(160)
            ImGui.push_style_color(ImGui.Col_.frame_bg, ImGui.ImColor(20, 20, 25, 255).value)
            ImGui.push_style_color(ImGui.Col_.check_mark, ImGui.ImColor(*Config.color_primary).value)
            if ImGui.radio_button("Install##mode", state.ventoy_mode == 0):
                state.ventoy_mode = 0
            ImGui.same_line()
            if ImGui.radio_button("Update##mode", state.ventoy_mode == 1):
                state.ventoy_mode = 1
            ImGui.pop_style_color(2)

            ImGui.spacing()

            # Partition style
            ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(180, 180, 180, 255).value)
            ImGui.text("Partition Style")
            ImGui.pop_style_color()
            ImGui.same_line(160)
            ImGui.push_style_color(ImGui.Col_.frame_bg, ImGui.ImColor(20, 20, 25, 255).value)
            ImGui.push_style_color(ImGui.Col_.check_mark, ImGui.ImColor(*Config.color_primary).value)
            if ImGui.radio_button("MBR##part", state.ventoy_partition_style == 0):
                state.ventoy_partition_style = 0
            ImGui.same_line()
            if ImGui.radio_button("GPT##part", state.ventoy_partition_style == 1):
                state.ventoy_partition_style = 1
            ImGui.pop_style_color(2)

            ImGui.spacing()

            # File System
            ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(180, 180, 180, 255).value)
            ImGui.text("File System")
            ImGui.pop_style_color()
            ImGui.same_line(160)
            ImGui.set_next_item_width(200)
            ImGui.push_style_color(ImGui.Col_.frame_bg, ImGui.ImColor(20, 20, 25, 255).value)
            ImGui.push_style_color(ImGui.Col_.frame_bg_hovered, ImGui.ImColor(30, 30, 40, 255).value)
            ImGui.push_style_color(ImGui.Col_.popup_bg, ImGui.ImColor(15, 15, 20, 255).value)
            fs_items = "exFAT\0NTFS\0FAT32\0"
            _, state.ventoy_fs = ImGui.combo("##fs_select", state.ventoy_fs, fs_items)
            ImGui.pop_style_color(3)

            ImGui.spacing()

            # Secure Boot
            ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(180, 180, 180, 255).value)
            ImGui.text("Secure Boot")
            ImGui.pop_style_color()
            ImGui.same_line(160)
            ImGui.push_style_color(ImGui.Col_.check_mark, ImGui.ImColor(*Config.color_primary).value)
            ImGui.push_style_color(ImGui.Col_.frame_bg, ImGui.ImColor(20, 20, 25, 255).value)
            _, state.ventoy_secure_boot = ImGui.checkbox("Enable##secboot", state.ventoy_secure_boot)
            ImGui.pop_style_color(2)

            ImGui.spacing()
            ImGui.separator()
            ImGui.spacing()

            # ── Install Button ──
            if state.ventoy_installing:
                # Show progress
                Gui._section_header(icons_fontawesome_6.ICON_FA_SPINNER, "Installing...")
                ImGui.spacing()

                percent_text = f"{state.ventoy_progress * 100:.0f}%"
                ImGui.text(percent_text)
                Gui.progress("ventoy_install", state.ventoy_progress)

            elif state.ventoy_status == "Success":
                # Success state
                ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(0, 220, 100, 255).value)
                ImGui.text(f"{icons_fontawesome_6.ICON_FA_CIRCLE_CHECK}  Ventoy installed successfully!")
                ImGui.pop_style_color()

                ImGui.spacing()
                ImGui.push_style_color(ImGui.Col_.button, ImGui.ImColor(30, 30, 40, 255).value)
                ImGui.push_style_color(ImGui.Col_.button_hovered, ImGui.ImColor(45, 45, 55, 255).value)
                if ImGui.button("Install Again##reset", ImGui.ImVec2(150, 35)):
                    state.ventoy_status = "Ready"
                    state.ventoy_progress = 0.0
                ImGui.pop_style_color(2)

            elif state.ventoy_status == "Failed":
                # Failed state
                ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(255, 80, 80, 255).value)
                ImGui.text(f"{icons_fontawesome_6.ICON_FA_CIRCLE_XMARK}  Installation failed!")
                ImGui.pop_style_color()

                if state.ventoy_log:
                    ImGui.spacing()
                    ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(150, 150, 150, 255).value)
                    ImGui.text_wrapped(state.ventoy_log[:300])
                    ImGui.pop_style_color()

                ImGui.spacing()
                ImGui.push_style_color(ImGui.Col_.button, ImGui.ImColor(30, 30, 40, 255).value)
                ImGui.push_style_color(ImGui.Col_.button_hovered, ImGui.ImColor(45, 45, 55, 255).value)
                if ImGui.button("Try Again##retry", ImGui.ImVec2(150, 35)):
                    state.ventoy_status = "Ready"
                    state.ventoy_progress = 0.0
                    state.ventoy_log = ""
                ImGui.pop_style_color(2)

                # ── Recover USB Section ──
                ImGui.spacing()
                ImGui.separator()
                ImGui.spacing()
                Gui._section_header(icons_fontawesome_6.ICON_FA_SCREWDRIVER_WRENCH, "Recover USB Drive")
                ImGui.spacing()

                ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(180, 180, 180, 255).value)
                ImGui.text_wrapped("USB disappeared? Click Scan to find it, then Recover to create a new partition.")
                ImGui.pop_style_color()
                ImGui.spacing()

                # Scan button
                ImGui.push_style_color(ImGui.Col_.button, ImGui.ImColor(30, 30, 40, 255).value)
                ImGui.push_style_color(ImGui.Col_.button_hovered, ImGui.ImColor(45, 45, 55, 255).value)
                ImGui.push_style_color(ImGui.Col_.button_active, ImGui.ImColor(55, 55, 65, 255).value)
                if ImGui.button(f"{icons_fontawesome_6.ICON_FA_MAGNIFYING_GLASS}  Scan USB Disks##scan_raw", ImGui.ImVec2(200, 30)):
                    state.ventoy_raw_disks = Ventoy.list_raw_usb_disks()
                    state.ventoy_selected_raw_disk = 0
                ImGui.pop_style_color(3)

                if state.ventoy_raw_disks:
                    ImGui.spacing()
                    raw_labels = [d["label"] for d in state.ventoy_raw_disks]
                    raw_combo = "\0".join(raw_labels) + "\0"

                    ImGui.set_next_item_width(ImGui.get_content_region_avail().x - 120)
                    ImGui.push_style_color(ImGui.Col_.frame_bg, ImGui.ImColor(20, 20, 25, 255).value)
                    ImGui.push_style_color(ImGui.Col_.popup_bg, ImGui.ImColor(15, 15, 20, 255).value)
                    _, state.ventoy_selected_raw_disk = ImGui.combo("##raw_disk_select", state.ventoy_selected_raw_disk, raw_combo)
                    ImGui.pop_style_color(2)

                    ImGui.same_line()

                    # Recover button (orange)
                    ImGui.push_style_color(ImGui.Col_.button, ImGui.ImColor(200, 120, 0, 255).value)
                    ImGui.push_style_color(ImGui.Col_.button_hovered, ImGui.ImColor(230, 150, 30, 255).value)
                    ImGui.push_style_color(ImGui.Col_.button_active, ImGui.ImColor(170, 100, 0, 255).value)
                    if ImGui.button(f"{icons_fontawesome_6.ICON_FA_WRENCH}  Recover##recover_btn", ImGui.ImVec2(110, 0)):
                        if 0 <= state.ventoy_selected_raw_disk < len(state.ventoy_raw_disks):
                            disk_num = state.ventoy_raw_disks[state.ventoy_selected_raw_disk]["number"]
                            Ventoy.recover_usb(disk_num)
                    ImGui.pop_style_color(3)
                else:
                    ImGui.spacing()
                    ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(100, 100, 100, 255).value)
                    ImGui.text("Click 'Scan USB Disks' to find your USB drive.")
                    ImGui.pop_style_color()

            else:
                # Ready — show install button
                has_usb = len(state.ventoy_usb_list) > 0

                if not has_usb:
                    ImGui.begin_disabled()

                # Styled install button (primary color)
                ImGui.push_style_color(ImGui.Col_.button, ImGui.ImColor(0, 160, 220, 255).value)
                ImGui.push_style_color(ImGui.Col_.button_hovered, ImGui.ImColor(0, 189, 253, 255).value)
                ImGui.push_style_color(ImGui.Col_.button_active, ImGui.ImColor(0, 130, 180, 255).value)
                ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(255, 255, 255, 255).value)

                btn_width = ImGui.get_content_region_avail().x
                if ImGui.button(f"{icons_fontawesome_6.ICON_FA_DOWNLOAD}   Install Ventoy##install_btn", ImGui.ImVec2(btn_width, 42)):
                    if state.ventoy_usb_list and 0 <= state.ventoy_selected_usb < len(state.ventoy_usb_list):
                        selected_usb = state.ventoy_usb_list[state.ventoy_selected_usb]
                        Ventoy.install_ventoy(selected_usb["drive_letter"], selected_usb.get("phy_drive"))

                ImGui.pop_style_color(4)

                if not has_usb:
                    ImGui.end_disabled()
                    ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(255, 180, 50, 255).value)
                    ImGui.text(f"{icons_fontawesome_6.ICON_FA_TRIANGLE_EXCLAMATION}  No USB drive detected. Please insert a USB drive and click Refresh.")
                    ImGui.pop_style_color()

        ImGui.end_child()
        ImGui.pop_style_color(2)
        ImGui.pop_style_var(2)

    def _section_header(icon, text):
        UI.section_header(icon, text)