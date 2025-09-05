import os
import sys
from time import sleep
from typing import TYPE_CHECKING, Optional, Union
from datetime import datetime

from PySide6.QtWidgets import QApplication, QMainWindow, QButtonGroup, QColorDialog, QMessageBox, QSplashScreen, QFrame
from PySide6.QtGui import QActionGroup, QPixmap, QIcon, QScreen
from PySide6.QtCore import Qt, Signal, QFile, QTextStream, QPoint, QEvent

from PlayCreator_ui import Ui_MainWindow

import Core
import Config
from Core import logger, log_method
from Core.Enums import AppTheme, PlaybookType, Mode, TeamType, SymbolType
from Core.settings import FIRST_TEAM_MAX_POSITION, LINE_THICKNESS_RANGE, SCENE_LABELS_FONT_SIZE_RANGE
from View_Models import MainWindowModel
from Presenters import MainWindowPresenter
from Views import Graphics, CustomGraphicsView, SchemeWidget
from Views.Dialog_windows import DialogSignUp, DialogLogIn
from Services.Local_DB import session_factory

if TYPE_CHECKING:
    from uuid import UUID
    from PySide6.QtGui import QMoveEvent, QResizeEvent, QCloseEvent
    from Config import DarkThemeStyle, LightThemeStyle


class PlayCreatorApp(QMainWindow, Ui_MainWindow):
    toolBarAreaChanged = Signal(object)  # Qt.ToolBarArea
    editSchemeClicked = Signal(object)  # .model_uuid
    schemeItemDoubleClicked = Signal(object)  # .model_uuid
    removeSchemeBtnClicked = Signal(object, str)  # .model_uuid, list_widget_current_item_text
    moveUpSchemeBtnClicked = Signal(object, int)  # .model_uuid, list_widget_current_item_index
    moveDownSchemeBtnClicked = Signal(object, int)  # .model_uuid, list_widget_current_item_index
    placeFirstTeamClicked = Signal(object, int)  # TeamType, int(lineEdit_yards.text())
    placeSecondTeamClicked = Signal(object)  # TeamType
    placeAdditionalPlayerClicked = Signal()
    secondTeamSymbolChanged = Signal(object)  # SymbolType

    render_signal = Signal()

    @log_method()
    def __init__(self, main_presenter: 'MainWindowPresenter'):
        super().__init__()
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setupUi(self)
        self.main_presenter = main_presenter
        self.theme: Optional['AppTheme'] = None
        self.playbook_type: Optional['PlaybookType'] = None
        self.selected_scheme: Optional['SchemeWidget'] = None
        self.selected_scene: Optional['Graphics.Field'] = None
        self.edited_label: Optional['Graphics.ProxyTextEdit'] = None

        self.user = None

        self.graphics_view = CustomGraphicsView(parent=self)
        self.gridLayout_6.addWidget(self.graphics_view, 0, 0, 2, 1)

        action_theme_group = QActionGroup(self)
        action_theme_group.addAction(self.action_dark_theme)
        action_theme_group.addAction(self.action_light_theme)
        action_theme_group.setExclusive(True)

        mode_group = QButtonGroup(parent=self)
        mode_group.setExclusive(True)
        for mode in Mode:
            button = getattr(self, f'pushButton_{mode.name.lower()}')
            button.pressed.connect(
                lambda m=mode: self.selected_scene.set_config('mode', m)
                if self.selected_scene else ...
            )
            mode_group.addButton(button)
        for i, color in enumerate(Config.DEFAULT_COLORS):
            button = getattr(self, f'pushButton_color_{i}')
            button.setStyleSheet(f'background-color: {color};')
            button.pressed.connect(lambda c=color: self._set_color(c))

        self.comboBox_line_thickness.addItems(
            list(map(str, range(LINE_THICKNESS_RANGE.min, LINE_THICKNESS_RANGE.max + 1, 1)))
        )
        self.comboBox_font_size.addItems(
            list(map(str, range(SCENE_LABELS_FONT_SIZE_RANGE.min, SCENE_LABELS_FONT_SIZE_RANGE.max + 1, 1)))
        )

        self.toolBar_main.topLevelChanged.connect(
            lambda top_level: self.toolBarAreaChanged.emit(self.toolBarArea(self.toolBar_main))
            if not top_level else ...
        )
        self.lineEdit_yards.textChanged.connect(
            lambda text: getattr(self, f'_check_max_yards_{self.playbook_type.name}'.lower())(text)
        )
        self.pushButton_color_current.clicked.connect(
            self._get_user_color
        )

        self.listWidget_schemes.itemDoubleClicked.connect(
            lambda scheme_widget: self.schemeItemDoubleClicked.emit(scheme_widget.model_uuid)
        )
        self.pushButton_remove_scheme.clicked.connect(
            lambda: self.removeSchemeBtnClicked.emit(self.listWidget_schemes.currentItem().model_uuid, self.listWidget_schemes.currentItem().text())
        )
        self.pushButton_move_up_scheme.clicked.connect(
            lambda: self.moveUpSchemeBtnClicked.emit(
                self.listWidget_schemes.currentItem().model_uuid, self.listWidget_schemes.currentRow()
            )
        )
        self.pushButton_move_down_scheme.clicked.connect(
            lambda: self.moveDownSchemeBtnClicked.emit(
                self.listWidget_schemes.currentItem().model_uuid, self.listWidget_schemes.currentRow()
            )
        )
        self.pushButton_edit_scheme.clicked.connect(
            lambda: self.editSchemeClicked.emit(self.listWidget_schemes.currentItem().model_uuid)
        )

        self.pushButton_place_first_team.clicked.connect(
            self._on_place_first_team_btn_click
        )
        self.pushButton_place_second_team.clicked.connect(
            lambda: self.placeSecondTeamClicked.emit(TeamType(self.comboBox_team_type.currentIndex() + 4))
        )
        self.pushButton_add_additional_off_player.clicked.connect(
            lambda: self.placeAdditionalPlayerClicked.emit()
        )
        self.comboBox_second_players_symbol.currentIndexChanged.connect(
            lambda: self.secondTeamSymbolChanged.emit(SymbolType(self.comboBox_second_players_symbol.currentIndex()))
        )

        self.comboBox_line_thickness.currentTextChanged.connect(
            lambda thickness: self.selected_scene.set_config('line_thickness', int(thickness))
            if self.selected_scene else ...
        )
        self.comboBox_font_type.currentFontChanged.connect(
            lambda font: self._combobox_font_changed(self.selected_scene, font.family())
            if self.selected_scene else ...
        )
        self.comboBox_font_size.currentTextChanged.connect(
            lambda font_size: self._font_size_changed(self.selected_scene, font_size)
            if self.selected_scene else ...
        )
        self.pushButton_font_bold.toggled.connect(
            lambda bold_condition: self._bold_changed(self.selected_scene, bold_condition)
            if self.selected_scene else ...
        )
        self.pushButton_font_italic.toggled.connect(
            lambda italic_condition: self._italic_changed(self.selected_scene, italic_condition)
            if self.selected_scene else ...
        )
        self.pushButton_font_underline.toggled.connect(
            lambda underline_condition: self._underline_changed(self.selected_scene, underline_condition)
            if self.selected_scene else ...
        )

        self.set_initial_gui_state()



        # self.action_user_login.triggered.connect(self.user_log_in)
        # self.action_user_logout.triggered.connect(self.user_log_out)

        if Core.DEBUG:
            self.debug_btn.clicked.connect(self._debug_method)  ############################## тестовая функция
        if not Core.DEBUG:
            self.debug_btn.setEnabled(False)
            self.debug_btn.setVisible(False)

        # self.user_log_in()    ##########################  Установить неактивным создание нового плейбука
        # self.sign_up()

    def _debug_method(self):
        ...
        from Core.settings import WebAppUrls
        # import requests
        # response = requests.post(WebAppUrls.api_login, json={'username': 'alexfin', 'password': 'Dgkfvtyb65733'})
        # print(f'{response.json() = }')
        # self.render_signal.emit()
        from Views.Dialog_windows import DialogLogIn
        dialog = DialogLogIn(parent=self)
        dialog.exec()

    def _check_max_yards_football(self, value: str) -> None:
        try:
            if int(value) > FIRST_TEAM_MAX_POSITION.football:
                self.lineEdit_yards.setText(str(FIRST_TEAM_MAX_POSITION.football))
        except ValueError:
            pass

    def _check_max_yards_flag(self, value: str) -> None:
        try:
            if int(value) > FIRST_TEAM_MAX_POSITION.flag:
                self.lineEdit_yards.setText(str(FIRST_TEAM_MAX_POSITION.flag))
        except ValueError:
            pass

    @log_method()
    def set_initial_gui_state(self):
        """Установка начального состояния GUI."""
        self.action_new_playbook.setEnabled(True)
        self.menu_local_save.setEnabled(False)
        self.action_save_playbook_local.setEnabled(False)
        self.action_save_playbook_local_as.setEnabled(False)
        self.menu_remote_save.setEnabled(False)
        self.action_save_to_remote_server.setEnabled(False)
        self.action_save_to_remote_server_as.setEnabled(False)
        self.menu_open.setEnabled(True)
        self.action_open_local_playbook.setEnabled(True)
        self.action_open_remote_playbook.setEnabled(False)
        self.action_save_like_picture.setEnabled(False)
        self.action_save_all_like_picture.setEnabled(False)
        self.action_close_app.setEnabled(True)
        self.action_undo.setEnabled(False)
        self.action_redo.setEnabled(False)
        self.action_presentation_mode.setEnabled(True)
        self.action_toolbar_visible.setEnabled(True)
        self.menu_dialog_windows.setEnabled(True)
        self.menu_theme.setEnabled(True)
        self.action_user_login.setEnabled(True)
        self.action_user_logout.setEnabled(False)
        self.action_about.setEnabled(True)
        self.widget_painting_tools.setEnabled(False)
        self.comboBox_team_type.setEnabled(False)
        self.lineEdit_yards.setEnabled(False)
        self.pushButton_place_first_team.setEnabled(False)
        self.pushButton_add_additional_off_player.setEnabled(False)
        self.pushButton_add_additional_off_player.setVisible(False)
        self.pushButton_del_additional_off_player.setEnabled(False)
        self.pushButton_del_additional_off_player.setVisible(False)
        self.pushButton_place_second_team.setEnabled(False)
        self.comboBox_second_players_symbol.setEnabled(False)
        self.comboBox_second_players_symbol.setVisible(False)
        self.pushButton_remove_second_team.setEnabled(False)
        self.pushButton_remove_all_players.setEnabled(False)
        self.pushButton_edit_playbook.setEnabled(False)
        self.pushButton_edit_playbook.setVisible(False)
        self.listWidget_schemes.setEnabled(False)
        self.pushButton_edit_scheme.setEnabled(False)
        self.pushButton_add_scheme.setEnabled(False)
        self.pushButton_remove_scheme.setEnabled(False)
        self.pushButton_move_up_scheme.setEnabled(False)
        self.pushButton_move_down_scheme.setEnabled(False)

    @log_method()
    def set_initial_window_state(self, x: int, y: int, width: int, height: int, theme: 'AppTheme', is_maximized: bool,
                                 tool_bar_visible: bool, tool_bar_area: 'Qt.ToolBarArea', presentation_mode: bool,
                                 show_remove_scheme_dialog: bool, show_close_app_dialog: bool,
                                 show_save_changed_playbook_dialog: bool) -> None:
        self.move(QPoint(x, y))
        self.resize(width, height)
        getattr(self, f'action_{theme.name}_theme'.lower()).setChecked(True)
        self.showMaximized() if is_maximized else self.showNormal()
        self.addToolBar(tool_bar_area, self.toolBar_main)
        self.update_window(theme, tool_bar_visible, presentation_mode, show_remove_scheme_dialog, show_close_app_dialog,
                           show_save_changed_playbook_dialog)

    def _get_current_screen(self) -> 'QScreen':
        screen = self.screen()
        if screen:
            screen = QApplication.primaryScreen()
        return screen

    @log_method()
    def moveEvent(self, event: 'QMoveEvent') -> None:
        super().moveEvent(event)
        current_screen_width = self._get_current_screen().availableSize().width()
        current_screen_height = self._get_current_screen().availableSize().height()
        if self.x() > 0 and self.y() > 0 and self.x() + self.rect().width() < current_screen_width \
                and self.y() + self.rect().height() < current_screen_height:
            self.main_presenter.handle_move(event.pos().x(), event.pos().y())

    @log_method()
    def resizeEvent(self, event: 'QResizeEvent') -> None:
        super().resizeEvent(event)
        current_screen_size = self._get_current_screen().availableSize()
        window_size = event.size()
        if window_size.width() < current_screen_size.width() - 10 \
                and window_size.height() < current_screen_size.height() - 10:
            self.main_presenter.handle_resize(window_size.width(), window_size.height())

    @log_method()
    def changeEvent(self, event: 'QEvent') -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self.main_presenter.handle_maximized_changed(self.isMaximized())

    @log_method()
    def update_window(self, theme: 'AppTheme', tool_bar_visible: bool, presentation_mode: bool,
                      show_remove_scheme_dialog: bool, show_close_app_dialog: bool,
                      show_save_changed_playbook_dialog: bool) -> None:
        self.action_toolbar_visible.setChecked(tool_bar_visible)
        self.toolBar_main.show() if tool_bar_visible else self.toolBar_main.hide()
        self.action_show_remove_scheme_dialog.setChecked(show_remove_scheme_dialog)
        self.action_show_close_app_dialog.setChecked(show_close_app_dialog)
        self.action_show_save_changed_playbook_dialog.setChecked(show_save_changed_playbook_dialog)
        self.action_presentation_mode.setChecked(presentation_mode)
        self.groupBox_team_playbook_settings.setVisible(not presentation_mode)
        self.label_current_zoom.setVisible(not presentation_mode)
        self.set_theme(theme)

    @log_method()
    def set_theme(self, theme: 'AppTheme') -> None:
        self.theme = theme
        style: Union['DarkThemeStyle', 'LightThemeStyle'] = getattr(Config, f'{theme.name.title()}ThemeStyle')
        style_file = QFile(style.style_file_path)
        style_file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(style_file)
        style_text = stream.readAll()
        style_file.close()
        self.setStyleSheet(str(style_text))
        self.action_new_playbook.setIcon(QIcon(QPixmap(style.new_playbook_ico_path)))
        self.action_open_local_playbook.setIcon(QIcon(QPixmap(style.open_local_ico_path)))
        self.action_save_playbook_local.setIcon(QIcon(QPixmap(style.save_local_ico_path)))
        self.action_open_remote_playbook.setIcon(QIcon(QPixmap(style.open_remote_ico_path)))
        self.action_save_playbook_local_as.setIcon(QIcon(QPixmap(style.save_local_as_ico_path)))
        self.action_save_to_remote_server.setIcon(QIcon(QPixmap(style.save_remote_ico_path)))
        # self.action_save_to_remote_server_as.setIcon(QIcon(QPixmap()))
        self.action_save_like_picture.setIcon(QIcon(QPixmap(style.save_like_picture_ico_path)))
        self.action_save_all_like_picture.setIcon(QIcon(QPixmap(style.save_all_like_picture_ico_path)))
        self.action_presentation_mode.setIcon(QIcon(QPixmap(style.presentation_mode_ico_path)))
        for mode in Mode:
            getattr(self, f'pushButton_{mode.name.lower()}').setIcon(QIcon(QPixmap(getattr(style, f'btn_{mode.name.lower()}_ico_path'))))
        self.pushButton_remove_actions.setIcon(QIcon(QPixmap(style.remove_actions_ico_path)))
        self.pushButton_remove_figures.setIcon(QIcon(QPixmap(style.remove_figures_ico_path)))
        self.pushButton_remove_pencil.setIcon(QIcon(QPixmap(style.remove_pencil_ico_path)))
        self.pushButton_remove_labels.setIcon(QIcon(QPixmap(style.remove_labels_ico_path)))
        for row in range(self.listWidget_schemes.count()):
            self.listWidget_schemes.item(row).setIcon(QIcon(QPixmap(style.check_box_0_ico_path)))
            self.listWidget_schemes.item(row).setForeground(style.list_widget_item_default_color)
        if self.selected_scheme:
            self.selected_scheme.setIcon(QIcon(QPixmap(style.check_box_1_ico_path)))
            self.selected_scheme.setForeground(style.list_widget_item_selected_color)
        self.pushButton_edit_playbook.setIcon(QIcon(QPixmap(style.info_ico_path)))

    @log_method()
    def closeEvent(self, event: 'QCloseEvent') -> None:
        if self.main_presenter.handle_close_app():
            event.accept()
        else:
            event.ignore()

    @log_method()
    def set_playbook(self, name: str, playbook_type: 'PlaybookType', info: str) -> None:
        self.set_initial_gui_state()
        self.listWidget_schemes.clear()
        if self.selected_scene:
            self.selected_scene.deleteLater()
        self.selected_scheme = None
        self.selected_scene = None
        self.playbook_type = playbook_type
        self.menu_local_save.setEnabled(True)
        self.action_save_playbook_local.setEnabled(True)
        self.action_save_playbook_local_as.setEnabled(True)
        self.listWidget_schemes.setEnabled(True)
        self.pushButton_edit_playbook.setVisible(True)
        self.pushButton_edit_playbook.setEnabled(True)
        self.pushButton_add_scheme.setEnabled(True)
        self.label_playbook_name.setText(name)
        self.label_playbook_name.setToolTip(info)
        if playbook_type is PlaybookType.FOOTBALL:
            self.lineEdit_yards.setMaxLength(3)
            self.lineEdit_yards.setInputMask('999')
            self.lineEdit_yards.setText('50')
            self.comboBox_team_type.setVisible(True)
            self.label_place_players.setVisible(True)
            self.pushButton_edit_playbook.setToolTip(f'Тип: Футбол')
        if playbook_type is PlaybookType.FLAG:
            self.lineEdit_yards.setMaxLength(2)
            self.lineEdit_yards.setInputMask('99')
            self.lineEdit_yards.setText('25')
            self.comboBox_team_type.setVisible(False)
            self.label_place_players.setVisible(False)
            self.pushButton_edit_playbook.setToolTip(f'Тип: Флаг-футбол')

    @log_method()
    def update_playbook_name(self, name: str) -> None:
        self.label_playbook_name.setText(name)

    @log_method()
    def update_playbook_info(self, info: str) -> None:
        self.label_playbook_name.setToolTip(info)

    @log_method()
    def add_scheme_widget(self, scheme_model_uuid: 'UUID', scheme_name: str, scheme_note: str) -> 'SchemeWidget':
        scheme_widget = SchemeWidget(scheme_model_uuid, scheme_name)
        scheme_widget.setToolTip(scheme_note)
        self.listWidget_schemes.addItem(scheme_widget)
        self.pushButton_remove_scheme.setEnabled(True)
        self.pushButton_edit_scheme.setEnabled(True)
        self.widget_painting_tools.setEnabled(True)
        if self.listWidget_schemes.count() > 1:
            self.pushButton_move_up_scheme.setEnabled(True)
            self.pushButton_move_down_scheme.setEnabled(True)
        self.action_save_like_picture.setEnabled(True)
        self.action_save_all_like_picture.setEnabled(True)
        return scheme_widget

    @log_method()
    def remove_scheme_widget(self, scheme_widget: 'SchemeWidget') -> None:
        self.listWidget_schemes.takeItem(self.listWidget_schemes.row(scheme_widget))
        if self.listWidget_schemes.count() == 1:
            self.pushButton_move_up_scheme.setEnabled(False)
            self.pushButton_move_down_scheme.setEnabled(False)
        if self.listWidget_schemes.count() == 0:
            self.action_undo.setEnabled(False)
            self.action_redo.setEnabled(False)
            self.pushButton_move_up_scheme.setEnabled(False)
            self.pushButton_move_down_scheme.setEnabled(False)
            self.pushButton_edit_scheme.setEnabled(False)
            self.pushButton_remove_scheme.setEnabled(False)
            self.action_save_like_picture.setEnabled(False)
            self.action_save_all_like_picture.setEnabled(False)
            self.widget_painting_tools.setEnabled(False)
            self.lineEdit_yards.setEnabled(False)
            self.comboBox_team_type.setEnabled(False)
            self.pushButton_place_first_team.setEnabled(False)
            self.pushButton_place_second_team.setEnabled(False)
            self.pushButton_remove_second_team.setEnabled(False)
            self.pushButton_add_additional_off_player.setEnabled(False)
            self.pushButton_del_additional_off_player.setEnabled(False)
            self.pushButton_add_additional_off_player.setVisible(False)
            self.pushButton_del_additional_off_player.setVisible(False)
            self.pushButton_remove_all_players.setEnabled(False)
            self.comboBox_second_players_symbol.setEnabled(False)
            self.comboBox_second_players_symbol.setVisible(False)
            self.selected_scene.deleteLater()
            self.selected_scheme = None
            self.selected_scene = None

    @log_method()
    def select_scheme(self, scheme_widget: 'SchemeWidget', scene: 'Graphics.Field',
                      view_point_x: int, view_point_y: int, zoom: int,
                      first_team: Optional['TeamType'], second_team: Optional['TeamType'],
                      additional_player: bool, first_team_position: int,
                      can_undo: bool, can_redo: bool) -> None:
        style: Union['DarkThemeStyle', 'LightThemeStyle'] = getattr(Config, f'{self.theme.name.title()}ThemeStyle')
        if self.selected_scheme:
            self.selected_scheme.setForeground(style.list_widget_item_default_color)
            self.selected_scheme.setIcon(QIcon(QPixmap(style.check_box_0_ico_path)))
        self.selected_scheme = scheme_widget
        self.selected_scene = scene
        self._connect_signals_from_scene(scene)
        self.listWidget_schemes.setCurrentItem(scheme_widget)
        self.graphics_view.setScene(scene)
        self.selected_scheme.setForeground(style.list_widget_item_selected_color)
        self.selected_scheme.setIcon(QIcon(QPixmap(style.check_box_1_ico_path)))
        if view_point_x and view_point_y:
            self.graphics_view.centerOn(view_point_x, view_point_y)
        if zoom is not None:
            self.set_current_zoom(zoom)
        self._set_gui_for_selected_scheme(scene, first_team, second_team, additional_player, first_team_position, can_undo, can_redo)

    def _set_gui_for_selected_scheme(self, scene: 'Graphics.Field', first_team: Optional['TeamType'],
                                     second_team: Optional['TeamType'], additional_player_state: bool,
                                     first_team_position: Optional[int], can_undo: bool, can_redo: bool) -> None:
        getattr(self, f'pushButton_{scene.mode.name.lower()}').setChecked(True)
        first_team_state = bool(first_team)
        second_team_state = bool(second_team)
        if first_team_position:
            self.lineEdit_yards.setText(str(first_team_position))
        self.action_undo.setEnabled(can_undo)
        self.action_redo.setEnabled(can_redo)
        self.comboBox_font_type.setCurrentFont(scene.font_type)
        self.comboBox_font_size.setCurrentText(str(scene.font_size))
        self.pushButton_font_bold.setChecked(scene.bold)
        self.pushButton_font_italic.setChecked(scene.italic)
        self.pushButton_font_underline.setChecked(scene.underline)
        self.comboBox_line_thickness.setCurrentText(str(scene.line_thickness))
        self.pushButton_color_current.setStyleSheet(f'background-color: {scene.color};')
        self.comboBox_team_type.setEnabled(not first_team_state)
        self.lineEdit_yards.setEnabled(not first_team_state)
        self.pushButton_place_first_team.setEnabled(not first_team_state)
        self.pushButton_remove_all_players.setEnabled(first_team_state)
        if first_team_state:
            self.comboBox_team_type.setCurrentIndex(first_team.value)
            self.pushButton_place_second_team.setEnabled(not second_team_state)
            self.pushButton_remove_second_team.setEnabled(second_team_state)
            self.comboBox_second_players_symbol.setEnabled(second_team_state)
            self.comboBox_second_players_symbol.setVisible(second_team_state)
            if first_team in (TeamType.KICKOFF, TeamType.PUNT, TeamType.FIELD_GOAL_OFF):
                self.pushButton_add_additional_off_player.setVisible(False)
                self.pushButton_del_additional_off_player.setVisible(False)
            else:
                self.pushButton_add_additional_off_player.setVisible(True)
                self.pushButton_del_additional_off_player.setVisible(True)
                self.pushButton_add_additional_off_player.setEnabled(not additional_player_state)
                self.pushButton_del_additional_off_player.setEnabled(additional_player_state)
        else:
            if self.playbook_type is PlaybookType.FOOTBALL:
                self.comboBox_team_type.setEnabled(True)
            self.pushButton_add_additional_off_player.setVisible(False)
            self.pushButton_del_additional_off_player.setVisible(False)
            self.pushButton_add_additional_off_player.setEnabled(False)
            self.pushButton_del_additional_off_player.setEnabled(False)
            self.pushButton_place_second_team.setEnabled(False)
            self.pushButton_remove_second_team.setEnabled(False)
            self.comboBox_second_players_symbol.setEnabled(False)
            self.comboBox_second_players_symbol.setVisible(False)

    @log_method()
    def set_current_zoom(self, zoom: int) -> None:
        self.label_current_zoom.setText(f'Приближение: {str(zoom)}%')
        self.graphics_view.set_current_zoom(zoom)

    def _connect_signals_from_scene(self, scene: 'Graphics.Field'):
        scene.modeChanged.connect(lambda mode: getattr(self, f'pushButton_{mode.name.lower()}').setChecked(True))
        scene.labelSelected.connect(self._set_gui_config_from_label)
        scene.labelDeselected.connect(self._set_gui_config_from_scene)

    @log_method()
    def move_scheme_widget(self, last_index: int, new_index: int) -> None:
        scheme_widget = self.listWidget_schemes.takeItem(last_index)
        self.listWidget_schemes.insertItem(new_index, scheme_widget)
        self.listWidget_schemes.setCurrentItem(scheme_widget)

    @log_method()
    def set_undo_action_state(self, is_enabled: bool) -> None:
        self.action_undo.setEnabled(is_enabled)

    @log_method()
    def set_redo_action_state(self, is_enabled: bool) -> None:
        self.action_redo.setEnabled(is_enabled)

    def _validate_yards_football(self, value: str) -> None:
        if not value.isdigit():  # Защита от пустого поля ввода ярдов
            value = '50'
            self.lineEdit_yards.setText('50')
        self._check_max_yards_football(value)
        if self.comboBox_team_type.currentIndex() == 1:  # Кикофф пробивается либо с 75 ярдов, либо с 65
            self.lineEdit_yards.setText('75') if int(value) >= 70 else self.lineEdit_yards.setText('65')
        elif self.comboBox_team_type.currentIndex() == 2:  # Пант нет смысла пробивать если до зачётной зоны меньше 20 ярдов
            if int(value) <= 20:
                self.lineEdit_yards.setText('20')

    def _validate_yards_flag(self, value: str) -> None:
        if not value.isdigit():
            self.lineEdit_yards.setText('25')

    def _on_place_first_team_btn_click(self) -> None:
        getattr(self, f'_validate_yards_{self.playbook_type.name}'.lower())(self.lineEdit_yards.text())
        self.placeFirstTeamClicked.emit(TeamType(self.comboBox_team_type.currentIndex()),
                                        int(self.lineEdit_yards.text()))

    @log_method()
    def set_gui_for_first_team(self, first_team_type: Optional['TeamType'], first_team_position: Optional[int]) -> None:
        first_team_state = bool(first_team_type)
        self.comboBox_team_type.setEnabled(not first_team_state)
        if first_team_type:
            self.comboBox_team_type.setCurrentIndex(first_team_type.value)
        self.lineEdit_yards.setEnabled(not first_team_state)
        if first_team_position is not None:
            self.lineEdit_yards.setText(str(first_team_position))
        self.pushButton_place_first_team.setEnabled(not first_team_state)
        self.pushButton_add_additional_off_player.setVisible(True if first_team_type is TeamType.OFFENCE else False)
        self.pushButton_del_additional_off_player.setVisible(True if first_team_type is TeamType.OFFENCE else False)
        self.pushButton_add_additional_off_player.setEnabled(True)
        self.pushButton_del_additional_off_player.setEnabled(False)
        self.pushButton_place_second_team.setEnabled(first_team_state)
        self.pushButton_remove_second_team.setEnabled(False)
        self.pushButton_remove_all_players.setEnabled(first_team_state)

    @log_method()
    def set_gui_for_second_team(self, second_team_type: 'TeamType') -> None:
        second_team_state = bool(second_team_type)
        self.pushButton_place_second_team.setEnabled(not second_team_state)
        self.pushButton_remove_second_team.setEnabled(second_team_state)
        self.comboBox_second_players_symbol.setVisible(second_team_state)
        self.comboBox_second_players_symbol.setEnabled(second_team_state)

    @log_method()
    def set_gui_for_additional_player(self, additional_player: bool) -> None:
        self.pushButton_add_additional_off_player.setEnabled(not additional_player)
        self.pushButton_del_additional_off_player.setEnabled(additional_player)

    def _set_color(self, color: str):
        self.pushButton_color_current.setStyleSheet(f'background-color: {color};')
        if self.selected_scene:
            self._color_changed(self.selected_scene, color)

    def _get_user_color(self):
        user_color_dialog = QColorDialog(parent=self)
        if user_color_dialog.exec():
            self._set_color(user_color_dialog.selectedColor().name())

    def _combobox_font_changed(self, scene: 'Graphics.Field', font: str):
        if self.edited_label:
            edited_label_font = self.edited_label.font()
            edited_label_font.setFamily(font)
            self.edited_label.setFont(edited_label_font)
            self.edited_label.update_height()
        else:
            scene.set_config('font_type', font)

    def _font_size_changed(self, scene: 'Graphics.Field', font_size: str):
        if self.edited_label:
            edited_label_font = self.edited_label.font()
            edited_label_font.setPointSize(int(font_size))
            self.edited_label.setFont(edited_label_font)
            self.edited_label.update_height()
        else:
            scene.set_config('font_size', int(font_size))

    def _bold_changed(self, scene: 'Graphics.Field', bold: bool):
        if self.edited_label:
            edited_label_font = self.edited_label.font()
            edited_label_font.setBold(bold)
            self.edited_label.setFont(edited_label_font)
            self.edited_label.update_height()
        else:
            scene.set_config('bold', bold)

    def _italic_changed(self, scene: 'Graphics.Field', italic: bool):
        if self.edited_label:
            edited_label_font = self.edited_label.font()
            edited_label_font.setItalic(italic)
            self.edited_label.setFont(edited_label_font)
            self.edited_label.update_height()
        else:
            scene.set_config('italic', italic)

    def _underline_changed(self, scene: 'Graphics.Field', underline: bool):
        if self.edited_label:
            edited_label_font = self.edited_label.font()
            edited_label_font.setUnderline(underline)
            self.edited_label.setFont(edited_label_font)
            self.edited_label.update_height()
        else:
            scene.set_config('underline', underline)

    def _color_changed(self, scene: 'Graphics.Field', color: str):
        if self.edited_label:
            text_cursor = self.edited_label.textCursor()
            self.edited_label.selectAll()
            self.edited_label.setTextColor(color)
            self.edited_label.setTextCursor(text_cursor)
            self.edited_label.update_height()
        elif scene:
            scene.set_config('color', color)

    def _set_gui_config_from_scene(self):
        self.edited_label = None
        self.comboBox_font_type.setCurrentFont(self.selected_scene.font_type)
        self.comboBox_font_size.setCurrentText(str(self.selected_scene.font_size))
        self.pushButton_font_bold.setChecked(self.selected_scene.bold)
        self.pushButton_font_italic.setChecked(self.selected_scene.italic)
        self.pushButton_font_underline.setChecked(self.selected_scene.underline)
        self.pushButton_color_current.setStyleSheet(f'background-color: {self.selected_scene.color};')

    def _set_gui_config_from_label(self, label: 'Graphics.ProxyTextEdit'):
        self.edited_label = label
        self.comboBox_font_type.setCurrentFont(label.font())
        self.comboBox_font_size.setCurrentText(str(label.font().pointSize()))
        self.pushButton_font_bold.setChecked(label.font().bold())
        self.pushButton_font_italic.setChecked(label.font().italic())
        self.pushButton_font_underline.setChecked(label.font().underline())
        self.pushButton_color_current.setStyleSheet(f'background-color: {label.textColor().name()};')














    # def set_gui_enter_offline(self):
    #     self.action_user_login.setEnabled(True)
    #     self.action_new_playbook.setEnabled(True)
    #     self.action_open_playbook_offline.setEnabled(True)
    #
    # def set_gui_enter_exit_online(self, condition: bool):
    #     self.action_user_login.setEnabled(not condition)
    #     self.action_user_logout.setEnabled(condition)
    #     self.action_open_playbook_online.setEnabled(condition)
    #     if self.playbook:
    #         self.action_save_playbook_online.setEnabled(condition)
    #     self.setWindowTitle(f'PlayCreator - {self.user}') if condition else self.setWindowTitle('PlayCreator')

    # def user_log_in(self, wrong_login_pass=False):
    #     dialog = DialogLogIn(wrong_login_pass=wrong_login_pass, parent=self)
    #     dialog.exec()
    #     result, login, password = dialog.result(), dialog.line_edit_login.text(), dialog.line_edit_password.text()
    #     if result == 1:
    #         if login == 'admin' and password == 'admin':
    #             self.user = login
    #             self.set_gui_enter_offline()
    #             self.set_gui_enter_exit_online(True)
    #         else:
    #             self.user_log_in(wrong_login_pass=True)
    #     elif result == 0:
    #         self.set_gui_enter_offline()
    #     elif result == 2:
    #         ...
    #         # print('Регистрация')

    # def user_log_out(self):
    #     if self.user and self.playbook:
    #         dialog_save_current_playbook_online = QMessageBox(QMessageBox.Question, 'Сохранение', 'Сохранить текущий плейбук на сервере?', parent=self)
    #         dialog_save_current_playbook_online.addButton("Да", QMessageBox.AcceptRole)  # результат устанавливается в 0
    #         dialog_save_current_playbook_online.addButton("Нет", QMessageBox.RejectRole)  # результат устанавливается в 1
    #         dialog_save_current_playbook_online.exec()
    #         if not dialog_save_current_playbook_online.result():
    #             ...
    #             # print('СОХРАНЕНИЕ НА СЕРВЕРЕ')
    #     self.user = None
    #     self.set_gui_enter_exit_online(False)

    # def sign_up(self):
    #     dialog = DialogSignUp(parent=self)
    #     dialog.exec()


if __name__ == '__main__':
    logger.info('=' * 60)
    logger.info('ЗАПУСК ПРИЛОЖЕНИЯ PlayCreator')
    logger.info('=' * 60)

    logger.debug('Создание таблиц базы данных')
    session_factory.create_tables()
    logger.debug('Таблицы базы данных созданы/проверены')

    app = QApplication(sys.argv)
    logger.debug('QApplication создан')

    main_window_presenter = MainWindowPresenter()
    logger.debug('MainWindowPresenter создан')
    if not Core.DEBUG:
        logger.debug('Режим production - показ splash screen')
        if os.path.exists(f'splash_screen.jpg'):
            splash = QSplashScreen(QPixmap('splash_screen.jpg').scaled(1000, 700, Qt.AspectRatioMode.KeepAspectRatio), f=Qt.WindowStaysOnTopHint)
        else:
            splash = QSplashScreen(QPixmap(':/splash/splash_screen.jpg').scaled(1000, 700, Qt.AspectRatioMode.KeepAspectRatio), f=Qt.WindowStaysOnTopHint)
        frame = QFrame(parent=splash)
        frame.setFixedSize(splash.width(), splash.height())
        frame.setFrameShadow(QFrame.Shadow.Raised)
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setLineWidth(0)
        frame.setMidLineWidth(3)
        splash.show()
        sleep(2)
        logger.debug('Splash screen показан')

    play_creator = PlayCreatorApp(main_window_presenter)
    logger.debug('Главное окно создано')

    screen_rect_center = app.primaryScreen().availableGeometry().center()
    main_window_minimum_size = play_creator.minimumSize()
    main_window_model = MainWindowModel(screen_rect_center, main_window_minimum_size)
    main_window_presenter.set_model_and_view(main_window_model, play_creator)

    play_creator.show()
    logger.info('Главное окно показано')

    if not Core.DEBUG:
        splash.finish(play_creator)
        logger.debug('Splash screen закрыт')
    logger.info('Приложение запущено успешно, вход в event loop')

    exit_code = app.exec()
    logger.info(f'Приложение завершено с кодом: {exit_code}')

    sys.exit(exit_code)


