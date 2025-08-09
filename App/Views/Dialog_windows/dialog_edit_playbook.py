from typing import TYPE_CHECKING, Optional
from collections import namedtuple

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QComboBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from Config.Enums import PlaybookAccessOptions
from .widgets.button_box import ButtonBox

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


__all__ = ('DialogEditPlaybook', )

playbook_data = namedtuple('PlaybookData', 'name info who_can_edit who_can_see')


class DialogEditPlaybook(QDialog):
    def __init__(self, playbook_name: str, playbook_info: str,
                 who_can_edit: 'PlaybookAccessOptions',
                 who_can_see: 'PlaybookAccessOptions',
                 parent: Optional['QWidget'] = None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setFixedSize(572, 500)
        self.setWindowTitle('Информация о плейбуке')
        font = QFont()
        font.setPointSize(12)
        vertical_layout = QVBoxLayout(self)

        label_playbook_name = QLabel('Название плейбука:', parent=self)
        label_playbook_name.setFont(font)

        label_who_can_edit = QLabel('Кто может редактировать:', parent=self)
        label_who_can_edit.setFont(font)

        label_who_can_see = QLabel('Кто может просматривать:', parent=self)
        label_who_can_see.setFont(font)

        label_playbook_info = QLabel('Информация о плейбуке:', parent=self)
        label_playbook_info.setFont(font)

        self.line_edit_playbook_name = QLineEdit()
        self.line_edit_playbook_name.setText(playbook_name)

        self.combo_who_can_edit = QComboBox(parent=self)
        self.combo_who_can_edit.addItems(
            ['Глава команды', 'Правление команды (глава и тренеры)',
             'Постоянные игроки команды (все, кроме приглашённых)',
             'Все игроки команды (в том числе приглашённые игроки)', 'Все']
        )
        self.combo_who_can_edit.setCurrentIndex(who_can_edit.value)

        self.combo_who_can_see = QComboBox(parent=self)
        self.combo_who_can_see.addItems(
            ['Глава команды', 'Правление команды (глава и тренеры)',
             'Постоянные игроки команды (все, кроме приглашённых)',
             'Все игроки команды (в том числе приглашённые игроки)', 'Все']
        )
        self.combo_who_can_see.setCurrentIndex(who_can_see.value)

        self.text_edit_playbook_info = QTextEdit()
        self.text_edit_playbook_info.setText(playbook_info)

        vertical_layout.addWidget(label_playbook_name)
        vertical_layout.addWidget(self.line_edit_playbook_name)
        vertical_layout.addWidget(label_who_can_edit)
        vertical_layout.addWidget(self.combo_who_can_edit)
        vertical_layout.addWidget(label_who_can_see)
        vertical_layout.addWidget(self.combo_who_can_see)
        vertical_layout.addWidget(label_playbook_info)
        vertical_layout.addWidget(self.text_edit_playbook_info)

        button_box = ButtonBox(self, True, Qt.AlignmentFlag.AlignCenter, 'ОК', 'Отмена')
        vertical_layout.addWidget(button_box)
        self.line_edit_playbook_name.setFocus()

        button_box.accepted.connect(self.accept)
        button_box.declined.connect(self.reject)

    def get_data(self) -> 'playbook_data':
        return playbook_data(
            self.line_edit_playbook_name.text().strip(), self.text_edit_playbook_info.toPlainText(),
            PlaybookAccessOptions(self.combo_who_can_edit.currentIndex()),
            PlaybookAccessOptions(self.combo_who_can_see.currentIndex())
        )
