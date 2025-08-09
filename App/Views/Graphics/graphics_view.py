from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGraphicsView, QFrame, QSizePolicy
from PySide6.QtCore import Signal, Qt

if TYPE_CHECKING:
    from PySide6.QtGui import QWheelEvent

__all__ = ('CustomGraphicsView', )


class CustomGraphicsView(QGraphicsView):
    zoomChanged = Signal(int)
    viewPointChanged = Signal(int, int)

    def __init__(self, parent):
        super().__init__(parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.verticalScrollBar().setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.horizontalScrollBar().setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(1000, 600)
        self.zoom_factor = 1.2
        self.current_zoom = 60
        self.verticalScrollBar().actionTriggered.connect(self.scene_set_current_view_point)
        self.horizontalScrollBar().actionTriggered.connect(self.scene_set_current_view_point)

    def wheelEvent(self, event: 'QWheelEvent') -> None:
        """Увеличение или уменьшение масштаба."""
        if event.angleDelta().y() < 0 and event.modifiers() == Qt.ShiftModifier:
            self.horizontalScrollBar().setSliderPosition(self.horizontalScrollBar().sliderPosition() + self.horizontalScrollBar().singleStep())
        elif event.angleDelta().y() > 0 and event.modifiers() == Qt.ShiftModifier:
            self.horizontalScrollBar().setSliderPosition(self.horizontalScrollBar().sliderPosition() - self.horizontalScrollBar().singleStep())
        elif event.angleDelta().y() > 0 and event.modifiers() == Qt.ControlModifier:
            zoom_in_value = self.current_zoom + 20
            self.scene_set_current_view_point()
            self.zoomChanged.emit(zoom_in_value)
        elif event.angleDelta().y() < 0 and event.modifiers() == Qt.ControlModifier:
            zoom_out_value = self.current_zoom - 20
            self.scene_set_current_view_point()
            self.zoomChanged.emit(zoom_out_value)
        else:
            super().wheelEvent(event)
            self.scene_set_current_view_point()

    def scene_set_current_view_point(self) -> None:
        if self.scene():  # Установка текущей точки обзора на сцене
            view_point = self.mapToScene(int(self.width() / 2), int(self.height() / 2))
            self.viewPointChanged.emit(view_point.x(), view_point.y())

    def set_current_zoom(self, zoom_value: int) -> None:
        zoom_index = (zoom_value - self.current_zoom) / 20
        self.scale(self.zoom_factor ** zoom_index, self.zoom_factor ** zoom_index)
        self.current_zoom = zoom_value

