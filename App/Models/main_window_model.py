from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QObject, Signal, QSettings, Qt, QSize, QPoint

import Config
from Config.Enums import AppTheme

if TYPE_CHECKING:
    from Models import PlaybookModel


__all__ = ('MainWindowModel', )


class MainWindowModel(QObject):
    modelChanged = Signal(object)
    playbookInstalled = Signal(object)  # PlaybookModel

    def __init__(self, screen_rect_center: 'QPoint', main_window_minimum_size: 'QSize'):
        super().__init__()
        self._playbook: Optional['PlaybookModel'] = None
        self._restore_window_state(screen_rect_center, main_window_minimum_size)

    @property
    def playbook(self) -> 'PlaybookModel':
        return self._playbook

    @playbook.setter
    def playbook(self, value: 'PlaybookModel') -> None:
        self._playbook = value
        self.playbookInstalled.emit(self._playbook)

    @property
    def version(self) -> str:
        return self._version

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int) -> None:
        self._x = value

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int) -> None:
        self._y = value

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, value: int) -> None:
        self._width = value

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, value: int) -> None:
        self._height = value

    @property
    def is_maximized(self) -> bool:
        return self._is_maximized

    @is_maximized.setter
    def is_maximized(self, value: bool) -> None:
        self._is_maximized = value

    @property
    def theme(self) -> 'AppTheme':
        return self._theme

    @theme.setter
    def theme(self, value: 'AppTheme') -> None:
        self._theme = value
        self.modelChanged.emit(self)

    @property
    def about_ico_path(self) -> str:
        return self._about_ico_path

    @about_ico_path.setter
    def about_ico_path(self, value: str) -> None:
        self._about_ico_path = value

    @property
    def show_remove_scheme_dialog(self) -> bool:
        return self._show_remove_scheme_dialog

    @show_remove_scheme_dialog.setter
    def show_remove_scheme_dialog(self, value: bool) -> None:
        self._show_remove_scheme_dialog = value
        self.modelChanged.emit(self)

    @property
    def show_close_app_dialog(self) -> bool:
        return self._show_close_app_dialog

    @show_close_app_dialog.setter
    def show_close_app_dialog(self, value: bool) -> None:
        self._show_close_app_dialog = value
        self.modelChanged.emit(self)

    @property
    def tool_bar_visible(self) -> bool:
        return self._tool_bar_visible

    @tool_bar_visible.setter
    def tool_bar_visible(self, value: bool) -> None:
        self._tool_bar_visible = value
        self.modelChanged.emit(self)

    @property
    def tool_bar_area(self) -> 'Qt.ToolBarArea':
        return self._tool_bar_area

    @tool_bar_area.setter
    def tool_bar_area(self, value: 'Qt.ToolBarArea') -> None:
        self._tool_bar_area = value
        self.modelChanged.emit(self)

    @property
    def presentation_mode(self) -> bool:
        return self._presentation_mode

    @presentation_mode.setter
    def presentation_mode(self, value: bool) -> None:
        self._presentation_mode = value
        self.modelChanged.emit(self)

    def _restore_window_state(self, screen_rect_center: 'QPoint', main_window_minimum_size: 'QSize'):
        if Config.DEBUG:
            settings = QSettings('settings.ini', QSettings.Format.IniFormat)
        else:
            settings = QSettings(Config.ORGANIZATION, Config.APP_NAME)
        self._x = settings.value('window/x',
                                 defaultValue=screen_rect_center.x() - main_window_minimum_size.width() // 2,
                                 type=int)
        self._y = settings.value('window/y',
                                 defaultValue=screen_rect_center.y() - main_window_minimum_size.height() // 2,
                                 type=int)
        self._width = settings.value('window/width', defaultValue=main_window_minimum_size.width(), type=int)
        self._height = settings.value('window/height', defaultValue=main_window_minimum_size.height(), type=int)
        self._is_maximized = settings.value('window/is_maximized', defaultValue=False, type=bool)
        self._theme = AppTheme(settings.value('app/theme', defaultValue=0, type=int))
        self._tool_bar_visible = settings.value('toolBar/visible', defaultValue=True, type=bool)
        self._tool_bar_area = Qt.ToolBarArea(settings.value('toolBar/area', defaultValue=4, type=int))
        self._show_remove_scheme_dialog = settings.value('app/show_remove_scheme_dialog', defaultValue=True, type=bool)
        self._show_close_app_dialog = settings.value('app/show_close_app_dialog', defaultValue=True, type=bool)
        self._presentation_mode = False
        self._about_ico_path = f'://themes/{self._theme.name}_theme/tactic.png'.lower()
        self._version = Config.VERSION

    def save_window_state(self):
        if Config.DEBUG:
            settings = QSettings('settings.ini', QSettings.Format.IniFormat)
        else:
            settings = QSettings(Config.ORGANIZATION, Config.APP_NAME)
        if not self._is_maximized:
            settings.setValue('window/x', self._x)
            settings.setValue('window/y', self._y)
        settings.setValue('window/width', self._width)
        settings.setValue('window/height', self._height)
        settings.setValue('window/is_maximized', self._is_maximized)
        settings.setValue('app/theme', self._theme.value)
        settings.setValue('toolBar/visible', self._tool_bar_visible)
        settings.setValue('toolBar/area', self._tool_bar_area.value)
        settings.setValue('app/show_remove_scheme_dialog', self._show_remove_scheme_dialog)
        settings.setValue('app/show_close_app_dialog', self._show_close_app_dialog)


