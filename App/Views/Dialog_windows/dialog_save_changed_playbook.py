from typing import TYPE_CHECKING

from PySide6.QtWidgets import QCheckBox, QComboBox, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from .dialog_info import DialogInfo

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


class DialogSaveChangedPlaybook(DialogInfo):
    def __init__(self, parent: 'QWidget', ask_save_remote: bool = False):
        super().__init__('Сохранить плейбук?', 'Изменения в текущем плейбуке не были сохранены. Хотите сохранить их?',
                         parent=parent, check_box=True, decline_button=True)
        if ask_save_remote:
            font = QFont()
            font.setPointSize(10)
            self.check_box_save_local = QCheckBox('Сохранить на компьютере', parent=self)
            self.check_box_save_remote = QCheckBox('Сохранить на сервере', parent=self)
            save_type_layout = QVBoxLayout()
            save_type_layout.setSpacing(2)
            save_type_layout.addWidget(self.check_box_save_local)
            save_type_layout.addWidget(self.check_box_save_remote)
            self._label_checkbox_layout.insertLayout(1, save_type_layout)

            self.check_box_save_local.stateChanged.connect(self._set_enable_ok_btn)
            self.check_box_save_remote.stateChanged.connect(self._set_enable_ok_btn)
            self._set_enable_ok_btn()

    def _set_enable_ok_btn(self) -> None:
        if self.check_box_save_local.checkState() == Qt.CheckState.Checked or \
                self.check_box_save_remote.checkState() == Qt.CheckState.Checked:
            self._button_box.accept_btn_set_enabled(True)
        else:
            self._button_box.accept_btn_set_enabled(False)