from typing import TYPE_CHECKING
from collections import namedtuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QLabel
from PySide6.QtGui import QFont


from .widgets.button_box import ButtonBox

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

__all__ = ('DialogInput', )

dialog_input_data = namedtuple('DialogInputData', 'text')


class DialogInput(QDialog):
    def __init__(self, title: str, label_text: str, parent: 'QWidget' = None):
        super().__init__(parent=parent)
        self.setWindowTitle(title)
        self.setFixedSize(226, 113)

        font = QFont()
        font.setPointSize(10)
        label = QLabel()
        label.setFont(font)
        label.setText(label_text)

        self._line_edit_input = QLineEdit()
        self._line_edit_input.setFont(font)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        button_box = ButtonBox(self, True, Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(label)
        main_layout.addWidget(self._line_edit_input)
        main_layout.addWidget(button_box)

        button_box.accepted.connect(self.accept)
        button_box.declined.connect(self.reject)

    def get_data(self) -> 'dialog_input_data':
        return dialog_input_data(self._line_edit_input.text().strip())
