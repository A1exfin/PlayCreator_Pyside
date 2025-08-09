from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QFormLayout, QVBoxLayout, QLayout, QPushButton
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

__all__ = ('DialogSignUp', )


class DialogSignUp(QDialog):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle('Вход')
        self.setFixedSize(339, 132)

        font = QFont()
        font.setPointSize(14)
        font.setBold(True)

        label_sign_up_title = QLabel('Регистрация', parent=self)
        label_sign_up_title.setFont(font)
        label_sign_up_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # label_sign_up_title.setStyleSheet('color: #27c727')

        label_login = QLabel('Логин: ', parent=self)
        label_login.setFont(font)
        # label_login.setStyleSheet('color: #27c727')

        label_email = QLabel('Email: ', parent=self)
        label_email.setFont(font)
        # label_email.setStyleSheet('color: #27c727')

        label_password = QLabel('Пароль: ', parent=self)
        label_password.setFont(font)
        # label_password.setStyleSheet('color: #27c727')

        self.line_edit_login = QLineEdit()
        self.line_edit_login.setFont(font)

        self.line_edit_email = QLineEdit()
        self.line_edit_email.setFont(font)

        self.line_edit_password = QLineEdit()
        self.line_edit_password.setFont(font)

        self.button_sign_up = QPushButton('Зарегистрироваться')
        self.button_sign_up.setFont(font)
        self.button_sign_up.setStyleSheet('min-width: 150px; min-height: 25px;')

        form_layout = QFormLayout()
        form_layout.setWidget(0, QFormLayout.LabelRole, label_login)
        form_layout.setWidget(0, QFormLayout.FieldRole, self.line_edit_login)
        form_layout.setWidget(1, QFormLayout.LabelRole, label_email)
        form_layout.setWidget(1, QFormLayout.FieldRole, self.line_edit_email)
        form_layout.setWidget(2, QFormLayout.LabelRole, label_password)
        form_layout.setWidget(2, QFormLayout.FieldRole, self.line_edit_password)
        form_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        form_layout.setRowWrapPolicy(QFormLayout.WrapLongRows)

        vertical_layout_main = QVBoxLayout(self)
        vertical_layout_main.addWidget(label_sign_up_title)
        vertical_layout_main.addLayout(form_layout)
        vertical_layout_main.addWidget(self.button_sign_up)




