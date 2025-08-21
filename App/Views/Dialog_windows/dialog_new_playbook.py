from collections import namedtuple

from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QRadioButton, QFormLayout, QVBoxLayout, QHBoxLayout, QLayout
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from Core.settings import PLAYBOOK_NAME_MAX_LENGTH
from Core.Enums import PlaybookType
from .widgets.button_box import ButtonBox

__all__ = ('DialogNewPlaybook', )

new_playbook_data = namedtuple('NewPlaybookData', 'name playbook_type')


class DialogNewPlaybook(QDialog):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle('Новый плейбук')
        self.setFixedSize(339, 132)

        font = QFont()
        font.setPointSize(10)

        label_scheme_name = QLabel('Название плейбука:', parent=self)
        label_scheme_name.setFont(font)

        label_scheme_type = QLabel('Тип плейбука:', parent=self)
        label_scheme_type.setFont(font)

        self.line_edit = QLineEdit(parent=self)
        self.line_edit.setFont(font)
        self.line_edit.setMaxLength(PLAYBOOK_NAME_MAX_LENGTH)

        self.radio_button_football = QRadioButton('Футбол', parent=self)
        self.radio_button_football.setFont(font)
        self.radio_button_football.setChecked(True)
        self.radio_button_flag = QRadioButton('Флаг-футбол', parent=self)
        self.radio_button_flag.setFont(font)
        self.radio_button_flag.setChecked(False)

        button_box = ButtonBox(self, True, Qt.AlignmentFlag.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setWidget(0, QFormLayout.LabelRole, label_scheme_name)
        form_layout.setWidget(0, QFormLayout.FieldRole, self.line_edit)
        form_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        form_layout.setRowWrapPolicy(QFormLayout.WrapLongRows)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(label_scheme_type)
        horizontal_layout.addWidget(self.radio_button_football)
        horizontal_layout.addWidget(self.radio_button_flag)
        horizontal_layout.setContentsMargins(0, 10, 0, 10)

        vertical_layout = QVBoxLayout(self)
        vertical_layout.addLayout(form_layout)
        vertical_layout.addLayout(horizontal_layout)
        vertical_layout.addWidget(button_box)
        self.line_edit.setFocus()

        button_box.accepted.connect(self.accept)
        button_box.declined.connect(self.reject)

    def get_data(self) -> 'new_playbook_data':
        name = self.line_edit.text().strip()
        if self.radio_button_football.isChecked():
            playbook_type = PlaybookType.FOOTBALL
        elif self.radio_button_flag.isChecked():
            playbook_type = PlaybookType.FLAG
        return new_playbook_data(name, playbook_type)
