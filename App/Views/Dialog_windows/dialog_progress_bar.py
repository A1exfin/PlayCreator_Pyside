from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QDialog, QProgressBar, QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtGui import QFont

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget
    from PySide6.QtGui import QKeyEvent

__all__ =('DialogProgressBar', )


class DialogProgressBar(QDialog):
    def __init__(self, parent: 'QWidget', operation_name: str, start_value: int = 0, final_value: int = 100):
        super().__init__(parent=parent)
        self.overrideWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setFixedSize(400, 140)

        frame = QFrame(parent=self)
        frame.setFixedSize(self.width(), self.height())
        frame.setFrameShadow(QFrame.Shadow.Raised)
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setLineWidth(0)
        frame.setMidLineWidth(1)

        font = QFont()
        font.setPointSize(15)
        self._label_operation_name = QLabel(operation_name, parent=self)
        self._label_operation_name.setFont(font)

        font.setPointSize(10)
        self._label_progress = QLabel(parent=self)
        self._label_progress.setFont(font)

        self._progress_bar = QProgressBar(parent=self)
        self._progress_bar.setMinimum(start_value)
        self._progress_bar.setMaximum(final_value)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.valueChanged.connect(self._set_label_progress_text)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 10, 20, 30)
        main_layout.addWidget(self._label_operation_name)
        main_layout.addWidget(self._label_progress)
        main_layout.addWidget(self._progress_bar)
        self.set_progress_value(start_value)

        self.timer = QTimer(parent=self)
        self.timer.timeout.connect(self._close_window)

    def set_progress_value(self, value: int) -> None:
        self._progress_bar.setValue(value)
        if value >= self._progress_bar.maximum():
            self.timer.start(600)

    def finish(self) -> None:
        self.set_progress_value(self._progress_bar.maximum())

    def _close_window(self) -> None:
        self.timer.stop()
        self._progress_bar.reset()
        self._set_label_progress_text(self._progress_bar.minimum())
        self.close()

    def _set_label_progress_text(self, value: int) -> None:
        self._label_progress.setText(f'Прогресс: {self._get_percents(value)}%')

    def _get_percents(self, value: int) -> str:
        return str(int(100 / self._progress_bar.maximum() * value))

    def keyPressEvent(self, event: 'QKeyEvent') -> None:
        event.ignore()

