from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from Models import LabelModel


__all__ = ('MoveLabelCommand', 'ChangeLabelTextAttributesCommand', 'ChangeLabelSizeCommand')


class MoveLabelCommand(QUndoCommand):
    def __init__(self, label_model: 'LabelModel', new_pos_x: float, new_pos_y: float):
        super().__init__('Перемещение надписи.')
        self._label_model = label_model
        self._last_pos_x = self._label_model.x
        self._last_pos_y = self._label_model.y
        self._new_pos_x = new_pos_x
        self._new_pos_y = new_pos_y

    def redo(self) -> None:
        self._label_model.set_pos(self._new_pos_x, self._new_pos_y)

    def undo(self) -> None:
        self._label_model.set_pos(self._last_pos_x, self._last_pos_y)

    def id(self) -> int:
        return 1

    def mergeWith(self, other: 'QUndoCommand') -> bool:
        if not isinstance(other, MoveLabelCommand):
            return False
        if other._label_model is not self._label_model:
            return False
        self._new_pos_x, self._new_pos_y = other._new_pos_x, other._new_pos_y
        return True


class ChangeLabelTextAttributesCommand(QUndoCommand):
    def __init__(self, label_model: 'LabelModel', new_text: str, new_font_type: str, new_font_size: int,
                 new_font_bold: bool, new_font_italic: bool, new_font_underline: bool, new_font_color: str,
                 new_y: float, new_height: float):
        super().__init__()
        self._label_model = label_model
        self._last_text = self._label_model.text
        self._last_font_type = self._label_model.font_type
        self._last_font_size = self._label_model.font_size
        self._last_font_bold = self._label_model.font_bold
        self._last_font_italic = self._label_model.font_italic
        self._last_font_underline = self._label_model.font_underline
        self._last_font_color = self._label_model.font_color
        self._last_y = self._label_model.y
        self._last_height = self._label_model.height
        self._new_text = new_text
        self._new_font_type = new_font_type
        self._new_font_size = new_font_size
        self._new_font_bold = new_font_bold
        self._new_font_italic = new_font_italic
        self._new_font_underline = new_font_underline
        self._new_font_color = new_font_color
        self._new_y = new_y
        self._new_height = new_height

    def redo(self) -> None:
        self._label_model.set_text_attributes(self._new_text, self._new_font_type, self._new_font_size,
                                              self._new_font_bold, self._new_font_italic, self._new_font_underline,
                                              self._new_font_color, self._new_y, self._new_height)

    def undo(self) -> None:
        self._label_model.set_text_attributes(self._last_text, self._last_font_type, self._last_font_size,
                                              self._last_font_bold, self._last_font_italic, self._last_font_underline,
                                              self._last_font_color, self._last_y, self._last_height)

    def id(self) -> int:
        return 1

    def mergeWith(self, other: 'QUndoCommand') -> bool:
        if not isinstance(other, ChangeLabelTextAttributesCommand):
            return False
        if other._label_model is not self._label_model:
            return False
        self._new_text, self._new_font_type, self._new_font_size, self._new_font_color = \
            other._new_text, other._new_font_type, other._new_font_size, other._new_font_color
        self._new_font_bold, self._new_font_italic, self._new_font_underline = \
            other._new_font_bold, other._new_font_italic, other._new_font_underline
        self._new_y, self._new_height = \
            other._new_y, other._new_height
        return True


class ChangeLabelSizeCommand(QUndoCommand):
    def __init__(self, label_model: 'LabelModel', new_x: float, new_y: float, new_width: float, new_height: float):
        super().__init__()
        self._label_model = label_model
        self._last_pos_x = self._label_model.x
        self._last_pos_y = self._label_model.y
        self._last_width = self._label_model.width
        self._last_height = self._label_model.height
        self._new_pos_x = new_x
        self._new_pos_y = new_y
        self._new_width = new_width
        self._new_height = new_height

    def redo(self) -> None:
        self._label_model.set_size(self._new_pos_x, self._new_pos_y, self._new_width, self._new_height)

    def undo(self) -> None:
        self._label_model.set_size(self._last_pos_x, self._last_pos_y, self._last_width, self._last_height)

    def id(self) -> int:
        return 1

    def mergeWith(self, other: 'QUndoCommand') -> bool:
        if not isinstance(other, ChangeLabelSizeCommand):
            return False
        if other._label_model is not self._label_model:
            return False
        self._new_pos_x, self._new_pos_y, self._new_width, self._new_height = \
            other._new_pos_x, other._new_pos_y, other._new_width, other._new_height
        return True
