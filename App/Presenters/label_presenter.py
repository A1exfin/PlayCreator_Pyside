from typing import TYPE_CHECKING

from Commands import MoveLabelCommand, ChangeLabelTextAttributesCommand, ChangeLabelSizeCommand

if TYPE_CHECKING:
    from PySide6.QtCore import QPointF
    from PlayCreator_main import PlayCreatorApp
    from Views import Graphics
    from Models import LabelModel


__all__ = ('LabelPresenter', )


class LabelPresenter:
    def __init__(self, execute_command_func: callable, label_model: 'LabelModel', view: 'PlayCreatorApp',
                 label_view: 'Graphics.ProxyWidgetLabel'):
        self._execute_command_func = execute_command_func
        self._view = view
        self._label_view = label_view
        self._model = label_model
        self._connect_signals()

    def _connect_signals(self) -> None:
        self._label_view.widget().signals.itemMoved.connect(self._handle_label_item_moved)
        self._model.coordsChanged.connect(self._move_label_item)
        self._label_view.widget().signals.itemEdited.connect(self._handle_label_item_edited)
        self._model.textAttributesChanged.connect(self._change_label_item_text_attributes)
        self._label_view.widget().signals.itemResized.connect(self._handle_label_item_resized)
        self._model.sizeChanged.connect(self._change_label_item_size)

    def _handle_label_item_moved(self, new_pos: 'QPointF') -> None:
        if self._model.x != new_pos.x() or self._model.y != new_pos.y():
            move_label_command = MoveLabelCommand(self._model, new_pos.x(), new_pos.y())
            self._execute_command_func(move_label_command)

    def _move_label_item(self, new_pos: 'QPointF') -> None:
        self._label_view.set_pos(new_pos)

    def _handle_label_item_edited(self, new_text: str, new_font_type: str, new_font_size: int, new_font_bold: bool,
                                  new_font_italic: bool, new_font_underline: bool, new_font_color: str,
                                  new_y: float, new_height: float) -> None:
        if self._model.text != new_text or self._model.font_type != new_font_type \
                or self._model.font_size != new_font_size or self._model.font_bold != new_font_bold \
                or self._model.font_italic != new_font_italic or self._model.font_underline != new_font_underline \
                or self._model.font_color != new_font_color:
            change_label_text_attributes_command = ChangeLabelTextAttributesCommand(self._model, new_text,
                                                                                    new_font_type, new_font_size,
                                                                                    new_font_bold, new_font_italic,
                                                                                    new_font_underline, new_font_color,
                                                                                    new_y, new_height)
            self._execute_command_func(change_label_text_attributes_command)

    def _change_label_item_text_attributes(self, new_text: str, new_font_type: str, new_font_size: int,
                                           new_font_bold: bool, new_font_italic: bool, new_font_underline: bool,
                                           new_font_color: str, new_y: float, new_height: float) -> None:
        self._label_view.set_text_attributes(new_text, new_font_type, new_font_size, new_font_bold, new_font_italic,
                                             new_font_underline, new_font_color, new_y, new_height)

    def _handle_label_item_resized(self, new_x: float, new_y: float, new_width: float, new_height: float) -> None:
        if self._model.x != new_x or self._model.y != new_y or self._model.width != new_width \
                or self._model.height != new_height:
            change_label_size_command = ChangeLabelSizeCommand(self._model, new_x, new_y, new_width, new_height)
            self._execute_command_func(change_label_size_command)

    def _change_label_item_size(self, new_x: float, new_y: float, new_width: float, new_height: float) -> None:
        self._label_view.set_rect(new_x, new_y, new_width, new_height)
