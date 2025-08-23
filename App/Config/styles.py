from typing import Final
from dataclasses import dataclass

from PySide6.QtCore import QFile
from PySide6.QtGui import QColor, QIcon, QPixmap

from Core.Enums import Mode


__all__ = ('DEFAULT_COLORS', 'HOVER_SCENE_ITEM_COLOR', 'ERASER_CURSOR_PATH',
           'DarkThemeStyle', 'LightThemeStyle')

DEFAULT_COLORS = ('#000000', '#800000', '#400080', '#0004ff', '#8d8b9a', '#22b14c',
                  '#ff0000', '#ff00ea', '#ff80ff', '#ff8000', '#dcdc00', '#00ff00')

HOVER_SCENE_ITEM_COLOR: Final[QColor] = QColor('#ffcb30')

ERASER_CURSOR_PATH: Final[str] = '://cursors/cursors/eraser.cur'


@dataclass(frozen=True)
class DarkThemeStyle:
    style_file_path = f'://themes/dark_theme/playcreator_style.css'
    new_playbook_ico_path = '://themes/dark_theme/new_playbook.png'
    open_local_ico_path = '://themes/dark_theme/open_local.png'
    save_local_ico_path = '://themes/dark_theme/save_local.png'
    save_local_as_ico_path = '://themes/dark_theme/save_local_as.png'
    open_remote_ico_path = '://themes/dark_theme/open_remote.png'
    save_remote_ico_path = '://themes/dark_theme/save_remote.png'
    # save_remote_as_ico_path = '://themes/dark_theme/save_remote_as.png'
    save_like_picture_ico_path = ':/themes/dark_theme/save_like_picture.png'
    save_all_like_picture_ico_path = ':/themes/dark_theme/save_all_like_picture.png'
    presentation_mode_ico_path = ':/themes/dark_theme/presentation_mode.png'
    remove_actions_ico_path = ':/themes/dark_theme/remove_actions.png'
    remove_figures_ico_path = ':/themes/dark_theme/remove_figures.png'
    remove_labels_ico_path = ':/themes/dark_theme/remove_labels.png'
    remove_pencil_ico_path = ':/themes/dark_theme/remove_pencil.png'
    check_box_0_ico_path = ':/themes/dark_theme/check_box-0.png'
    check_box_1_ico_path = ':/themes/dark_theme/check_box-1.png'
    radio_btn_0_ico_path = ':/themes/dark_theme/radio_button-0.png'
    radio_btn_1_ico_path = ':/themes/dark_theme/radio_button-1.png'
    info_ico_path = ':/themes/dark_theme/info.png'
    tactic_ico_path = ':/themes/dark_theme/tactic.png'
    btn_move_ico_path = ':/themes/dark_theme/move.png'
    btn_erase_ico_path = ':/themes/dark_theme/erase.png'
    btn_route_ico_path = ':/themes/dark_theme/route.png'
    btn_block_ico_path = ':/themes/dark_theme/block.png'
    btn_motion_ico_path = ':/themes/dark_theme/motion.png'
    btn_rectangle_ico_path = ':/themes/dark_theme/rectangle.png'
    btn_ellipse_ico_path = ':/themes/dark_theme/ellipse.png'
    btn_pencil_ico_path = ':/themes/dark_theme/pencil.png'
    btn_label_ico_path = ':/themes/dark_theme/label.png'
    list_widget_item_default_color = QColor('#b1b1b1')
    list_widget_item_selected_color = QColor('#27c727')


@dataclass(frozen=True)
class LightThemeStyle:
    style_file_path = f'://themes/light_theme/playcreator_style.css'
    new_playbook_ico_path = '://themes/light_theme/new_playbook.png'
    open_local_ico_path = '://themes/light_theme/open_local.png'
    save_local_ico_path = '://themes/light_theme/save_local.png'
    open_remote_ico_path = '://themes/light_theme/open_remote.png'
    save_local_as_ico_path = '://themes/light_theme/save_local_as.png'
    save_remote_ico_path = '://themes/light_theme/save_remote.png'
    # save_remote_as_ico_path = '://themes/light_theme/save_remote_as.png'
    save_like_picture_ico_path = ':/themes/light_theme/save_like_picture.png'
    save_all_like_picture_ico_path = ':/themes/light_theme/save_all_like_picture.png'
    presentation_mode_ico_path = ':/themes/light_theme/presentation_mode.png'
    remove_actions_ico_path = ':/themes/light_theme/remove_actions.png'
    remove_figures_ico_path = ':/themes/light_theme/remove_figures.png'
    remove_labels_ico_path = ':/themes/light_theme/remove_labels.png'
    remove_pencil_ico_path = ':/themes/light_theme/remove_pencil.png'
    check_box_0_ico_path = ':/themes/light_theme/check_box-0.png'
    check_box_1_ico_path = ':/themes/light_theme/check_box-1.png'
    radio_btn_0_ico_path = ':/themes/light_theme/radio_button-0.png'
    radio_btn_1_ico_path = ':/themes/light_theme/radio_button-1.png'
    info_ico_path = ':/themes/light_theme/info.png'
    tactic_ico_path = ':/themes/light_theme/tactic.png'
    btn_move_ico_path = ':/themes/light_theme/move.png'
    btn_erase_ico_path = ':/themes/light_theme/erase.png'
    btn_route_ico_path = ':/themes/light_theme/route.png'
    btn_block_ico_path = ':/themes/light_theme/block.png'
    btn_motion_ico_path = ':/themes/light_theme/motion.png'
    btn_rectangle_ico_path = ':/themes/light_theme/rectangle.png'
    btn_ellipse_ico_path = ':/themes/light_theme/ellipse.png'
    btn_pencil_ico_path = ':/themes/light_theme/pencil.png'
    btn_label_ico_path = ':/themes/light_theme/label.png'
    list_widget_item_default_color = QColor('#000000')
    list_widget_item_selected_color = QColor('#1a6aa7')
