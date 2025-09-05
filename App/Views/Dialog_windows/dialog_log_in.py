from typing import TYPE_CHECKING, Optional
from collections import namedtuple
import webbrowser

from PySide6.QtCore import Qt, QObject
from PySide6.QtGui import QFont, QDesktopServices
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QGridLayout, QSpacerItem, QSizePolicy, QPushButton, QStyle

from Core.settings import WebAppUrls
from .widgets.button_box import ButtonBox

if TYPE_CHECKING:
    pass

__all__ = ('DialogLogIn', )

user_data = namedtuple('UserData', 'username password')


class DialogLogIn(QDialog):
    def __init__(self, parent: Optional['QObject'] = None, flags: 'Qt.WindowType' = Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.setWindowTitle('Вход')
        self.setFixedSize(480, 580)

        font = QFont()
        font.setPointSize(12)

        self._label_form_errors = QLabel()
        self._label_form_errors.setFont(font)
        self._label_form_errors.setText('Невозможно войти с предоставленными учетными данными.')
        self._label_form_errors.setStyleSheet('color: #ff0000;'
                                              # ' border: 1px solid red;'
                                              )
        self._label_form_errors.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label_form_errors.setWordWrap(True)

        self._label_login_errors = QLabel()
        self._label_login_errors.setFont(font)
        self._label_login_errors.setText('Имя пользователя неверно.')
        self._label_login_errors.setStyleSheet('color: #ff0000; '
                                               # 'border: 1px solid red;'
                                               )
        self._label_login_errors.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._label_login_errors.setWordWrap(True)

        self._label_password_errors = QLabel()
        self._label_password_errors.setFont(font)
        self._label_password_errors.setText('Пароль неверен.')
        self._label_password_errors.setStyleSheet('color: #ff0000;'
                                                  # ' border: 1px solid red;'
                                                  )
        self._label_password_errors.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._label_password_errors.setWordWrap(True)

        label_login = QLabel('Логин: ', parent=self)
        label_login.setFont(font)
        label_login.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        label_login.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # label_login.setStyleSheet('border: 1px solid green;')

        label_password = QLabel('Пароль: ', parent=self)
        label_password.setFont(font)
        label_password.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        label_password.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # label_password.setStyleSheet('border: 1px solid green;')

        self._line_edit_username = QLineEdit(parent=self)
        self._line_edit_username.setFont(font)

        self._line_edit_password = QLineEdit(parent=self)
        self._line_edit_password.setFont(font)
        self._line_edit_password.setEchoMode(QLineEdit.Password)

        button_box = ButtonBox(parent=self, cancel_button=True, buttons_align=Qt.AlignmentFlag.AlignCenter,
                               accept_button_text='Войти', decline_button_text='Оффлайн')

        font.setPointSize(10)
        button_sign_up = QPushButton('Регистрация', parent=self)
        button_sign_up.setFont(font)
        button_sign_up.setFixedSize(206, 25)

        main_layout = QGridLayout(self)
        main_layout.setColumnMinimumWidth(0, 20)
        main_layout.setColumnMinimumWidth(3, 20)
        main_layout.setColumnStretch(0, 50)
        main_layout.setColumnStretch(3, 50)
        main_layout.setRowMinimumHeight(0, 20)
        main_layout.setRowMinimumHeight(5, 50)
        main_layout.setRowStretch(0, 20)
        main_layout.setRowStretch(5, 50)
        main_layout.setSpacing(20)

        # main_layout = QVBoxLayout(self)

        login_layout = QVBoxLayout()
        login_layout.addWidget(label_login)
        login_layout.addWidget(self._line_edit_username)
        login_layout.addWidget(self._label_login_errors)
        login_layout.setSpacing(5)

        password_layout = QVBoxLayout()
        password_layout.addWidget(label_password)
        password_layout.addWidget(self._line_edit_password)
        password_layout.addWidget(self._label_password_errors)
        password_layout.setSpacing(5)

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(button_box)
        buttons_layout.addWidget(button_sign_up)
        buttons_layout.setSpacing(5)

        main_layout.addWidget(self._label_form_errors, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(login_layout, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(password_layout, 3, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(buttons_layout, 4, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        # main_layout.addWidget(self._label_form_errors, alignment=Qt.AlignmentFlag.AlignVCenter)
        # main_layout.addLayout(login_layout)
        # main_layout.addLayout(password_layout)
        # main_layout.addLayout(buttons_layout)

        button_box.accepted.connect(self.accept)
        button_box.declined.connect(self.reject)
        button_sign_up.clicked.connect(self._open_signup_url)

    def get_data(self) -> 'user_data':
        return user_data(self._line_edit_username.text(), self._line_edit_password.text())

    def _open_signup_url(self) -> None:
        try:
            QDesktopServices.openUrl(WebAppUrls.signup)
        except:
            webbrowser.open(WebAppUrls.signup)
