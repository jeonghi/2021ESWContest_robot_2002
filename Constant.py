from enum import Enum, auto

class Constant:
    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise Exception('변수에 값을 할당할 수 없습니다.')
        self.__dict__[name] = value

    def __delattr__(self, name):
        if name in self.__dict__:
            raise Exception('변수를 삭제할 수 없습니다.')


const = Constant()
const.RED_RANGE1 = [[0, 33, 40], [30, 201, 142]]
const.RED_RANGE2 = [[121, 20, 85], [180, 255, 145]]
const.GREEN_RANGE = [[29, 80, 68], [76, 255, 134]]
const.BLUE_RANGE = [[73, 52, 53], [124, 170, 156]]
const.BLACK_RANGE = [[0, 0, 0], [180, 255, 81]]
const.YELLOW_RANGE = [[11, 68, 126], [44, 230, 235]]

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

class WalkInfo(Enum):
    DIRECTION_LINE = auto()
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
