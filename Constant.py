from enum import Enum, auto

class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()

class AreaColor(Enum):
    GREEN = auto()
    BLACK = auto()

class LineColor(Enum):
    GREEN = auto()
    BLACK = auto()
    YELLOW = auto()

class LineColor(Enum):
    GREEN = auto()
    BLACK = auto()
    YELLOW = auto()

class WalkInfo(Enum):
    CORNER_LEFT = auto()
    CORNER_RIGHT = auto()
    STRAIGHT = auto()
    LEFT = auto()
    RIGHT = auto()
    V_LEFT = auto()
    V_RIGHT = auto()
    MODIFY_LEFT = auto()
    MODIFY_RIGHT = auto()
    BACKWARD = auto()
