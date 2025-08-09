from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QPushButton
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

__all__ = ('DialogLogIn', )


class DialogLogIn(QDialog):
    def __init__(self, parent=None, flags=Qt.WindowFlags(), wrong_login_pass=False):
        super().__init__(parent, flags)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle('Вход')
        self.setFixedSize(480, 580)

        font = QFont()
        font.setPointSize(10)
        font.setBold(True)

        label_login = QLabel('Логин: ', parent=self)
        label_login.setFont(font)
        label_login.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        label_password = QLabel('Пароль: ', parent=self)
        label_password.setFont(font)
        label_password.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.button_login = QPushButton('Войти', parent=self)
        self.button_login.setFont(font)
        self.button_login.setFixedSize(130, 30)

        self.button_sign_up = QPushButton('Зарегистрироваться', parent=self)
        self.button_sign_up.setFont(font)
        self.button_sign_up.setFixedSize(266, 30)

        self.button_offline = QPushButton('Оффлайн', parent=self)
        self.button_offline.setFont(font)
        self.button_offline.setFixedSize(130, 30)

        font.setPointSize(14)
        label_wrong_login_or_password = QLabel(parent=self)
        label_wrong_login_or_password.setFont(font)
        label_wrong_login_or_password.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if wrong_login_pass:
            label_wrong_login_or_password.setText('Неверный логин или пароль')
        # label_wrong_login_or_password.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        font.setBold(False)
        self.line_edit_login = QLineEdit(parent=self)
        self.line_edit_login.setMinimumSize(250, 30)
        self.line_edit_login.setFont(font)

        self.line_edit_password = QLineEdit(parent=self)
        self.line_edit_password.setMinimumSize(250, 30)
        self.line_edit_password.setFont(font)
        self.line_edit_password.setEchoMode(QLineEdit.Password)

        horizontal_layout_buttons = QHBoxLayout()
        horizontal_layout_buttons.addWidget(self.button_login)
        horizontal_layout_buttons.addWidget(self.button_offline)

        vertical_layout_all = QVBoxLayout()
        # vertical_layout_all.addWidget(label_wrong_login_or_password)
        vertical_layout_all.addWidget(label_login)
        vertical_layout_all.addWidget(self.line_edit_login)
        vertical_layout_all.addWidget(label_password)
        vertical_layout_all.addWidget(self.line_edit_password)
        vertical_layout_all.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))  # отступ кнопок от полей ввода
        vertical_layout_all.addLayout(horizontal_layout_buttons)
        vertical_layout_all.addWidget(self.button_sign_up, 0, Qt.AlignmentFlag.AlignHCenter)

        horizontal_layout_main = QHBoxLayout()
        horizontal_layout_main.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))
        horizontal_layout_main.addLayout(vertical_layout_all)
        horizontal_layout_main.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))

        vertical_layout_main = QVBoxLayout(self)
        vertical_layout_main.addWidget(label_wrong_login_or_password)
        vertical_layout_main.addSpacerItem(QSpacerItem(40, 80, QSizePolicy.Expanding, QSizePolicy.Fixed))  # отступ сверху окна
        vertical_layout_main.addLayout(horizontal_layout_main)
        vertical_layout_main.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.button_login.clicked.connect(self.accept)
        self.button_offline.clicked.connect(self.reject)
        self.button_sign_up.clicked.connect(lambda: self.done(2))

        self.button_sign_up.setEnabled(False)#############
        self.button_login.setEnabled(False)##############
        self.line_edit_login.setEnabled(False)##################
        self.line_edit_password.setEnabled(False)##############################
        # self.line_edit_password.setText('admin')
        # self.line_edit_login.setText('admin')