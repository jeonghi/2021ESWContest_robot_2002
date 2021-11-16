from enum import Enum, auto
from collections import namedtuple

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

class Constant:
    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise Exception('변수에 값을 할당할 수 없습니다.')
        self.__dict__[name] = value

    def __delattr__(self, name):
        if name in self.__dict__:
            raise Exception('변수를 삭제할 수 없습니다.')


const = Constant()
### COLOR SETTING ###
const.RED_ALPHABET_RANGE1 = [[0, 53, 36], [30, 144, 99]]
const.RED_ALPHABET_RANGE2 = [[156, 53, 36], [180, 144, 99]]
const.BLUE_ALPHABET_RANGE = [[92, 100, 48], [128, 220, 112]]

### BOX
const.RED_BOX_RANGE1 = [[166, 138, 0], [180, 255, 186]]
const.RED_BOX_RANGE2 = [[0, 77, 0], [36, 255, 189]]
const.BLUE_BOX_RANGE = [[92, 106, 41], [128, 255, 172]]

### AREA ###
const.GREEN_RANGE = [[39, 55, 0], [91, 255, 150]]
const.BLACK_RANGE = [[0, 0, 0], [180, 255, 112]]

## LINE
const.YELLOW_RANGE = [[11, 62, 112], [44, 255, 237]]

### DOOR SETTING ###
const.IN_DOOR_WALK = 7
const.DEFAULT_WALK_AFTER_DETECT_DIRECTION = 4
const.DEFAULT_TURN_AFTER_DETECT_DIRECTION = 4
const.OUT_DOOR_WALK = 8
const.DOOR_THRESH_VALUE = 66

## DIRECTION ##
const.DIRECTION_THRESH_VALUE = 66

### CORNER FILTERING ###
const.CORNER_FILTER_DISTANCE = 40

## AREA ##
CHECK_AREA_GREEN_RATE_THRESH = 40

### GREEN ROOM ###
## 1) BOX -> AREA
const.GREEN_ROOM_TURN_FIND_BOX = 3
const.GREEN_ROOM_DEFAULT_TURN_FIND_AREA = 2
const.GREEN_ROOM_DEFAULT_WALK_BEFORE_DROP_BOX = 3
const.GREEN_ROOM_AREA_IN_LIMIT = 460
## 2) AREA -> CORNER
const.GREEN_ROOM_DEFAULT_TURN_FIND_CORNER = 2
const.GREEN_ROOM_TURN_FIND_CORNER = 1

### BLACK ROOM ###
const.BLACK_ROOM_DEFAULT_TURN_FIND_BOX = 3
const.BLACK_ROOM_DEFAULT_TURN_FIND_CORNER = 1
const.BLACK_ROOM_DEFAULT_OUT_ROOM_WALK = 3


### DEBUG MODE ###
debug_mode = Constant()
debug_mode.IS_ON = False
Room = namedtuple('Room', 'area_color room_name name_color')
first_room = Room(AreaColor.GREEN, "B", "RED")
second_room = Room(AreaColor.BLACK, "B", "BLUE")
third_room = Room(AreaColor.GREEN, "D", "BLUE")
debug_mode.DOOR_ALPHABET = "N"
debug_mode.DIRECTION = "RIGHT"
debug_mode.ROOMS = [first_room, second_room, third_room]
