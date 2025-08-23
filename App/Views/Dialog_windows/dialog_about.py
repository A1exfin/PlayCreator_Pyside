from typing import TYPE_CHECKING, Union

from PySide6.QtWidgets import QDialog, QLabel, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt

import Config
from .widgets.button_box import ButtonBox

if TYPE_CHECKING:
    from Core.Enums import AppTheme
    from Config import DarkThemeStyle, LightThemeStyle

__all__ = ('DialogAbout', )


class DialogAbout(QDialog):
    def __init__(self, version: str, theme: 'AppTheme', parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.setWindowTitle('PlayCreator')
        self.setFixedSize(639, 191)

        style: Union['DarkThemeStyle', 'LightThemeStyle'] = getattr(Config, f'{theme.name.title()}ThemeStyle')
        label_ico = QLabel(parent=self)
        label_ico.setPixmap(QPixmap(style.tactic_ico_path))

        font = QFont()
        font.setPointSize(14)
        font.setBold(True)

        label_text_pc = QLabel('PlayCreator', parent=self)
        label_text_pc.setFont(font)
        label_text_pc.setStyleSheet(f'margin-bottom: 20px')

        font = QFont()
        font.setPointSize(12)

        label_text_version = QLabel(f'Версия: {version}', parent=self)
        label_text_version.setFont(font)
        label_text_version.setStyleSheet('margin-bottom: 20px')

        label_text_developer = QLabel('Разработчик: Халеев Александр', parent=self)
        label_text_developer.setFont(font)
        label_text_developer.setStyleSheet('margin-bottom: 5px')

        text = 'Обратная связь. Email: alexfin16@gmail.com;\tVK: <a href=https://vk.com/alexn11>Халеев Александр</a>'
        label_text_feedback = QLabel(text, parent=self)
        label_text_feedback.setFont(font)
        label_text_feedback.setTextFormat(Qt.RichText)
        label_text_feedback.setTextInteractionFlags(Qt.TextBrowserInteraction)
        label_text_feedback.setOpenExternalLinks(True)
        label_text_feedback.setStyleSheet('margin-bottom: 5px')

        button_box = ButtonBox(self, False, Qt.AlignCenter)

        vertical_layout_ico = QVBoxLayout()
        vertical_layout_ico.addWidget(label_ico)
        vertical_layout_ico.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))

        horizontal_layout_pc_version = QHBoxLayout()
        horizontal_layout_pc_version.addWidget(label_text_pc)
        horizontal_layout_pc_version.addWidget(label_text_version)
        horizontal_layout_pc_version.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))

        vertical_layout_text = QVBoxLayout()
        vertical_layout_text.addLayout(horizontal_layout_pc_version)
        vertical_layout_text.addWidget(label_text_developer)
        vertical_layout_text.addWidget(label_text_feedback)
        vertical_layout_text.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addLayout(vertical_layout_ico)
        horizontal_layout.addLayout(vertical_layout_text)

        vertical_layout_3 = QVBoxLayout(self)
        vertical_layout_3.addLayout(horizontal_layout)
        vertical_layout_3.addWidget(button_box)

        button_box.accepted.connect(self.accept)