import math
import time
from imgui_bundle import ImColor, imgui as ImGui, icons_fontawesome_6
from modules.config import Config


class UI:
    _dropdown_open = {}

    @staticmethod
    def glow_icon_button(icon, label_id, is_active=False, btn_width=60, btn_height=60, sidebar_width=90):
        ImGui.set_cursor_pos_x((sidebar_width - btn_width) / 2)

        if is_active:
            cursor_pos = ImGui.get_cursor_screen_pos()
            draw_list = ImGui.get_window_draw_list()
            
            icon_size = ImGui.calc_text_size(icon)
            ix = cursor_pos.x + (btn_width - icon_size.x) / 2
            iy = cursor_pos.y + (btn_height - icon_size.y) / 2

            r, g, b = Config.color_primary[0], Config.color_primary[1], Config.color_primary[2]
        
            col_outer = ImGui.get_color_u32(ImGui.ImColor(r, g, b, 30).value)

            ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(*Config.color_primary).value)
        else:
            ImGui.push_style_color(ImGui.Col_.text, ImGui.ImVec4(0.5, 0.5, 0.5, 1.0))

        ImGui.push_style_color(ImGui.Col_.button, ImGui.ImVec4(0, 0, 0, 0))
        ImGui.push_style_color(ImGui.Col_.border, ImGui.ImVec4(0, 0, 0, 0))
        ImGui.push_style_color(ImGui.Col_.button_hovered, ImGui.ImVec4(0, 0, 0, 0))
        ImGui.push_style_color(ImGui.Col_.button_active, ImGui.ImVec4(0, 0, 0, 0))

        clicked = ImGui.button(f"{icon}##{label_id}", ImGui.ImVec2(btn_width, btn_height))
        ImGui.pop_style_color(5)

        return clicked

    @staticmethod
    def dropdown(dropdown_id, items, selected_index, width=280, icon=None):
        changed = False
        new_index = selected_index

        current_label = items[selected_index] if 0 <= selected_index < len(items) else "Select..."
        max_chars = int(width / 7)
        display_label = current_label if len(current_label) <= max_chars else current_label[:max_chars - 2] + ".."

        btn_height = 28
        cursor_pos = ImGui.get_cursor_screen_pos()
        fg = ImGui.get_foreground_draw_list()

        is_open = UI._dropdown_open.get(dropdown_id, False)

        ImGui.invisible_button(f"##dropdown_btn_{dropdown_id}", ImGui.ImVec2(width, btn_height))
        is_hovered = ImGui.is_item_hovered()
        just_clicked = ImGui.is_item_clicked()

        if just_clicked:
            is_open = not is_open
            UI._dropdown_open[dropdown_id] = is_open

        if is_open:
            bg_color = ImGui.ImColor(35, 35, 45, 255)
        elif is_hovered:
            bg_color = ImGui.ImColor(25, 25, 35, 255)
        else:
            bg_color = ImGui.ImColor(18, 18, 24, 255)

        border_color = ImGui.ImColor(*Config.color_border)
        p_min = cursor_pos
        p_max = ImGui.ImVec2(cursor_pos.x + width, cursor_pos.y + btn_height)

        fg.add_rect_filled(p_min, p_max, ImGui.get_color_u32(bg_color.value), 6.0)
        fg.add_rect(p_min, p_max, ImGui.get_color_u32(border_color.value), 6.0, 0, 1.0)

        text_x = cursor_pos.x + 10
        text_y = cursor_pos.y + (btn_height - ImGui.get_text_line_height()) / 2

        if icon:
            fg.add_text(
                ImGui.ImVec2(text_x, text_y),
                ImGui.get_color_u32(ImGui.ImColor(*Config.color_primary).value), icon
            )
            text_x += 22

        fg.add_text(
            ImGui.ImVec2(text_x, text_y),
            ImGui.get_color_u32(ImGui.ImColor(200, 200, 200, 255).value), display_label
        )

        arrow_icon = icons_fontawesome_6.ICON_FA_CHEVRON_UP if is_open else icons_fontawesome_6.ICON_FA_CHEVRON_DOWN
        arrow_size = ImGui.calc_text_size(arrow_icon)
        fg.add_text(
            ImGui.ImVec2(cursor_pos.x + width - arrow_size.x - 10, text_y),
            ImGui.get_color_u32(ImGui.ImColor(120, 120, 120, 255).value), arrow_icon
        )

        if is_open:
            mouse_pos = ImGui.get_mouse_pos()
            mouse_clicked = ImGui.is_mouse_clicked(0)

            item_height = 30
            popup_height = len(items) * item_height + 8
            popup_y = cursor_pos.y + btn_height + 4

            popup_min = ImGui.ImVec2(cursor_pos.x, popup_y)
            popup_max = ImGui.ImVec2(cursor_pos.x + width, popup_y + popup_height)

            fg.add_rect_filled(
                ImGui.ImVec2(popup_min.x + 2, popup_min.y + 2),
                ImGui.ImVec2(popup_max.x + 2, popup_max.y + 2),
                ImGui.get_color_u32(ImGui.ImColor(0, 0, 0, 80).value), 8.0
            )
            fg.add_rect_filled(popup_min, popup_max, ImGui.get_color_u32(ImGui.ImColor(12, 12, 18, 245).value), 8.0)
            fg.add_rect(popup_min, popup_max, ImGui.get_color_u32(ImGui.ImColor(*Config.color_border).value), 8.0, 0, 1.0)

            for i, item_label in enumerate(items):
                item_y = popup_y + 4 + i * item_height
                item_min = ImGui.ImVec2(cursor_pos.x + 4, item_y)
                item_max = ImGui.ImVec2(cursor_pos.x + width - 4, item_y + item_height)

                item_hovered = (item_min.x <= mouse_pos.x <= item_max.x and item_min.y <= mouse_pos.y <= item_max.y)

                if i == selected_index:
                    fg.add_rect_filled(
                        item_min, item_max,
                        ImGui.get_color_u32(ImGui.ImColor(
                            Config.color_primary[0], Config.color_primary[1], Config.color_primary[2], 30
                        ).value), 5.0
                    )
                elif item_hovered:
                    fg.add_rect_filled(
                        item_min, item_max,
                        ImGui.get_color_u32(ImGui.ImColor(40, 40, 50, 255).value), 5.0
                    )

                if i == selected_index:
                    fg.add_circle_filled(
                        ImGui.ImVec2(item_min.x + 12, item_min.y + item_height / 2),
                        3.0, ImGui.get_color_u32(ImGui.ImColor(*Config.color_primary).value)
                    )

                truncated = item_label if len(item_label) <= max_chars - 4 else item_label[:max_chars - 6] + ".."
                text_color = ImGui.ImColor(*Config.color_primary) if i == selected_index else ImGui.ImColor(180, 180, 180, 255)
                fg.add_text(
                    ImGui.ImVec2(item_min.x + 24, item_min.y + (item_height - ImGui.get_text_line_height()) / 2),
                    ImGui.get_color_u32(text_color.value), truncated
                )

                if item_hovered and mouse_clicked:
                    new_index = i
                    changed = True
                    UI._dropdown_open[dropdown_id] = False

            if mouse_clicked and not is_hovered:
                in_popup = (popup_min.x <= mouse_pos.x <= popup_max.x and popup_min.y <= mouse_pos.y <= popup_max.y)
                if not in_popup:
                    UI._dropdown_open[dropdown_id] = False

        return changed, new_index


    @staticmethod
    def icon_button(icon, btn_id, size=28):
        ImGui.push_style_color(ImGui.Col_.button, ImGui.ImVec4(0, 0, 0, 0))
        ImGui.push_style_color(ImGui.Col_.button_hovered, ImGui.ImColor(30, 30, 40, 255).value)
        ImGui.push_style_color(ImGui.Col_.button_active, ImGui.ImColor(55, 55, 65, 255).value)
        ImGui.push_style_var(ImGui.StyleVar_.frame_rounding, 5.0)

        clicked = ImGui.button(f"{icon}##{btn_id}", ImGui.ImVec2(size, size))

        ImGui.pop_style_var()
        ImGui.pop_style_color(3)
        return clicked

    @staticmethod
    def section_header(icon, text):
        ImGui.push_style_color(ImGui.Col_.text, ImGui.ImColor(*Config.color_primary).value)
        ImGui.text(icon)
        ImGui.pop_style_color()
        ImGui.same_line()
        ImGui.text(text)
