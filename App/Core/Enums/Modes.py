from enum import Enum


class Mode(Enum):
    MOVE = 0
    ERASE = 1
    ROUTE = 2
    BLOCK = 3
    MOTION = 4
    RECTANGLE = 5
    ELLIPSE = 6
    PENCIL = 7
    LABEL = 8