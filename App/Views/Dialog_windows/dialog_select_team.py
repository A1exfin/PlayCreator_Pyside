from typing import TYPE_CHECKING, Optional
from collections import namedtuple

from PySide6.QtWidgets import QDialog, QLabel, QComboBox, QVBoxLayout
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from .widgets.button_box import ButtonBox

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

__all__ = ('DialogSelectTeam', )

team_data = namedtuple('TeamData', 'id name')


class DialogSelectTeam(QDialog):
    def __init__(self, parent: 'QWidget', teams_lst: list[tuple]):
        super().__init__(parent)
        self.setWindowTitle('Выберите команду')
        self.setFixedSize(280, 122)

        font = QFont()
        font.setPointSize(10)
        label = QLabel('Для какой команды сохранить плейбук:', parent=self)
        label.setFont(font)

        self._teams_combo_box = QComboBox(parent=self)
        self._teams_combo_box.setFont(font)
        for team_id, team_name in teams_lst:
            self._teams_combo_box.addItem(team_name, team_id)

        button_box = ButtonBox(parent=self, cancel_button=True, buttons_align=Qt.AlignmentFlag.AlignCenter)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(self._teams_combo_box)
        main_layout.addWidget(button_box)

        button_box.accepted.connect(self.accept)
        button_box.declined.connect(self.reject)

    def get_data(self) -> 'team_data':
        team_name = self._teams_combo_box.currentText()
        team_id = self._teams_combo_box.currentData()
        return team_data(team_id, team_name)