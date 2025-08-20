from typing import TYPE_CHECKING, Optional

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QStyle, QSizePolicy, QSpacerItem
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QSize

from .widgets.button_box import ButtonBox

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

__all__ = ('DialogInfo', )


class DialogInfo(QDialog):
    def __init__(self, title: str, message: str, parent: Optional['QWidget'], check_box: bool = True, decline_button: bool = True,
                 accept_button_text: str = 'Да', decline_button_text: str = 'Нет'):
        super().__init__(parent)
        self.setMinimumSize(347, 111)
        self.setWindowTitle(title)

        font = QFont()
        font.setPointSize(10)

        label_message = QLabel(message, parent=self)
        label_message.setFont(font)
        label_message.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        ico = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion)
        ico_label = QLabel()
        ico_label.setPixmap(ico.pixmap(32, 32))
        ico_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self._label_checkbox_layout = QVBoxLayout()
        self._label_checkbox_layout.setSpacing(10)
        self._label_checkbox_layout.addWidget(label_message)
        if check_box:
            self.check_box_dont_ask_again = QCheckBox('Больше не спрашивать', parent=self)
            self.check_box_dont_ask_again.setFont(font)
            self._label_checkbox_layout.addWidget(self.check_box_dont_ask_again)

        ico_label_checkbox_layout = QHBoxLayout()
        ico_label_checkbox_layout.setSpacing(20)
        ico_label_checkbox_layout.addWidget(ico_label)
        ico_label_checkbox_layout.addLayout(self._label_checkbox_layout)

        self._button_box = ButtonBox(self, decline_button, Qt.AlignRight, accept_button_text, decline_button_text)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(ico_label_checkbox_layout)
        main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        main_layout.addWidget(self._button_box)

        self._button_box.accepted.connect(self.accept)
        self._button_box.declined.connect(self.reject)