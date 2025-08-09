from typing import TYPE_CHECKING, Union

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy, QMessageBox, QDialogButtonBox
from PySide6.QtGui import QFont


class ButtonBox(QWidget):
    accepted = Signal()
    declined = Signal()

    def __init__(self, parent, cancel_button: bool,
                 buttons_align: Union['Qt.AlignLeft', 'Qt.AlignCenter', 'Qt.AlignRight'],
                 accept_button_text: str = 'ОК', decline_button_text: str = 'Отмена'):
        super().__init__(parent)
        font = QFont()
        font.setPointSize(10)
        self._accept_button = QPushButton(parent=self)
        self._accept_button.setText(accept_button_text)
        self._accept_button.setFont(font)
        self._accept_button.setFixedSize(100, 25)
        self._accept_button.clicked.connect(lambda: self.accepted.emit())
        if cancel_button:
            self._decline_button = QPushButton(parent=self)
            self._decline_button.setText(decline_button_text)
            self._decline_button.setFont(font)
            self._decline_button.setFixedSize(100, 25)
            self._decline_button.clicked.connect(lambda: self.declined.emit())

        layout = QHBoxLayout(self)
        layout.setAlignment(buttons_align)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.addWidget(self._accept_button)
        if cancel_button:
            layout.addWidget(self._decline_button)

    def accept_btn_set_enabled(self, state: bool) -> None:
        self._accept_button.setEnabled(state)

    def decline_btn_set_enabled(self, state: bool) -> None:
        self._decline_button.setEnabled(state)

