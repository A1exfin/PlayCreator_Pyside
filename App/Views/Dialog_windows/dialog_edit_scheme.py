from collections import namedtuple

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from .widgets.button_box import ButtonBox

__all__ = ('DialogEditScheme', )

scheme_data = namedtuple('SchemeData', 'name note')


class DialogEditScheme(QDialog):
    def __init__(self, scheme_name: str, scheme_note: str, parent, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setFixedSize(572, 322)
        self.setWindowTitle('Информация о схеме')
        font = QFont()
        font.setPointSize(12)
        vertical_layout = QVBoxLayout(self)

        label_playbook_name = QLabel('Название схемы:', parent=self)
        label_playbook_name.setFont(font)

        label_playbook_info = QLabel('Заметки к схеме:', parent=self)
        label_playbook_info.setFont(font)

        font.setPointSize(10)
        self.line_edit_playbook_name = QLineEdit()
        self.line_edit_playbook_name.setText(scheme_name)

        self.text_edit_playbook_info = QTextEdit()
        self.text_edit_playbook_info.setText(scheme_note)

        vertical_layout.addWidget(label_playbook_name)
        vertical_layout.addWidget(self.line_edit_playbook_name)
        vertical_layout.addWidget(label_playbook_info)
        vertical_layout.addWidget(self.text_edit_playbook_info)

        confirmation_button_box = ButtonBox(self, True, Qt.AlignmentFlag.AlignCenter, 'ОК', 'Отмена')
        vertical_layout.addWidget(confirmation_button_box)
        self.line_edit_playbook_name.setFocus()

        confirmation_button_box.accepted.connect(self.accept)
        confirmation_button_box.declined.connect(self.reject)

    def get_data(self) -> 'scheme_data':
        return scheme_data(
            self.line_edit_playbook_name.text().strip(),
            self.text_edit_playbook_info.toPlainText()
        )
