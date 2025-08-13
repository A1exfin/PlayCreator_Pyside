from typing import TYPE_CHECKING, Optional
from collections import namedtuple
from datetime import datetime

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,  QTableWidgetItem, QAbstractItemView, \
    QSpacerItem, QSizePolicy, QPushButton, QHeaderView, QMessageBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from .widgets.button_box import ButtonBox
from .dialog_info import DialogInfo
from Config.Enums import PlaybookType
# from Local_DB.queryes import delete_playbook

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

__all__ = ('DialogOpenPlaybook', )

open_playbook_data = namedtuple('OpenPlaybookData', 'selected_playbook_id deleted_playbook_ids')


class DialogOpenPlaybook(QDialog):
    def __init__(self, playbook_info: list[tuple], delete_playbook_by_id_func: callable, parent: 'QWidget' = None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self._deleted_playbooks_ids = []
        self._delete_playbook_by_id_func = delete_playbook_by_id_func
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle('Выбор плейбука')
        self.setFixedSize(600, 400)
        # self.setMinimumWidth(600)

        font = QFont()
        font.setPointSize(10)

        font.setBold(False)
        self._button_box = ButtonBox(self, True, Qt.AlignRight)
        self._button_box.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._button_remove = QPushButton('Удалить', parent=self)
        self._button_remove.setFont(font)
        self._button_remove.setFixedSize(100, 25)
        self._button_remove.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._table_playbooks = QTableWidget(len(playbook_info), 5)
        self._table_playbooks.setFont(font)
        self._table_playbooks.setHorizontalHeaderLabels(['id', 'Название плейбука', 'Тип плейбука', 'Дата обновления', 'Дата создания'])
        self._table_playbooks.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        self._table_playbooks.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table_playbooks.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._table_playbooks.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self._table_playbooks.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self._table_playbooks.horizontalHeader().setSectionsClickable(False)
        font.setBold(True)
        self._table_playbooks.horizontalHeader().setFont(font)
        self._table_playbooks.verticalHeader().hide()
        self._table_playbooks.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table_playbooks.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table_playbooks.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._table_playbooks.setShowGrid(False)
        self._table_playbooks.setCornerButtonEnabled(False)
        self._table_playbooks.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._table_playbooks.hideColumn(0)
        for i, playbook in enumerate(playbook_info):
            item = QTableWidgetItem(str(playbook[0]))
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self._table_playbooks.setItem(i, 0, item)

            item = QTableWidgetItem(playbook[1])
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self._table_playbooks.setItem(i, 1, item)

            item = QTableWidgetItem(PlaybookType(playbook[2]).name.capitalize())
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self._table_playbooks.setItem(i, 2, item)

            item = QTableWidgetItem(self._get_formated_date(playbook[3]))
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self._table_playbooks.setItem(i, 3, item)

            item = QTableWidgetItem(self._get_formated_date(playbook[4]))
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self._table_playbooks.setItem(i, 4, item)
        # self.table_playbooks.sortItems(0, Qt.SortOrder.DescendingOrder)
        self._table_playbooks.itemDoubleClicked.connect(self._playbook_selected)

        horizontal_layout_buttons = QHBoxLayout()
        horizontal_layout_buttons.addWidget(self._button_remove)
        horizontal_layout_buttons.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
        horizontal_layout_buttons.addWidget(self._button_box)
        # horizontal_layout_buttons.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))

        vertical_layout = QVBoxLayout(self)
        vertical_layout.addWidget(self._table_playbooks)
        vertical_layout.addLayout(horizontal_layout_buttons)
        vertical_layout.addLayout(horizontal_layout_buttons)

        # self.table_playbooks.setFocus()
        if self._table_playbooks.rowCount() <= 0:
            self._button_box.accept_btn_set_enabled(False)
            self._button_remove.setEnabled(False)
        self._table_playbooks.setCurrentCell(0, 1)

        self._button_box.accepted.connect(self._playbook_selected)
        self._button_box.declined.connect(self.reject)
        self._button_remove.clicked.connect(self._remove_playbook)

    def _get_formated_date(self, date: str) -> str:
        d = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        return d.strftime('%d.%m.%y %H:%M')

    def _playbook_selected(self):
        if self._table_playbooks.rowCount() > 0:
            self.accept()

    def get_data(self) -> 'open_playbook_data':
        return open_playbook_data(
            int(self._table_playbooks.item(self._table_playbooks.currentRow(), 0).text()),
            tuple(self._deleted_playbooks_ids)
        )

    def _remove_playbook(self):
        playbook_id = int(self._table_playbooks.item(self._table_playbooks.currentRow(), 0).text())
        playbook_name = self._table_playbooks.item(self._table_playbooks.currentRow(), 1).text()

        dialog_deleted_playbook = DialogInfo('Удаление плейбука',
                                             f'Вы уверены что хотите удалить плейбук: "{playbook_name}"?',
                                             check_box=False, parent=self)
        dialog_deleted_playbook.exec()
        if dialog_deleted_playbook.result():
            self._delete_playbook_by_id_func(playbook_id)
            self._table_playbooks.removeRow(self._table_playbooks.currentRow())
            self._deleted_playbooks_ids.append(playbook_id)
        if self._table_playbooks.rowCount() <= 0:
            self._button_box.accept_btn_set_enabled(False)
            self._button_remove.setEnabled(False)

