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

# ---------- 대회 ---------- ##
## COLOR SETTING ###
const.RED_ALPHABET_RANGE1 = [[166, 77, 30], [180, 255, 189]]#
const.RED_ALPHABET_RANGE2 = [[0, 77, 30], [36, 255, 189]] #
const.BLUE_ALPHABET_RANGE = [[92, 87, 30], [170, 255, 120]] #
## BOX
const.RED_BOX_RANGE1 = [[166, 77, 30], [180, 255, 189]]#
const.RED_BOX_RANGE2 = [[0, 77, 30], [36, 255, 189]] #
const.BLUE_BOX_RANGE = [[92, 87, 30], [170, 255, 120]] #
## AREA ###
const.GREEN_RANGE = [[38, 54, 0], [91, 255, 98]] #
const.BLACK_RANGE = [[0, 0, 0], [180, 255, 80]] #
# LINE
const.YELLOW_RANGE = [[11, 83, 36], [48, 255, 255]]
#


### DOOR SETTING ###
const.IN_DOOR_WALK = 8
const.DEFAULT_WALK_AFTER_DETECT_DIRECTION = 4
const.DEFAULT_TURN_AFTER_DETECT_DIRECTION = 4
const.DEFAULT_DIRECTION = Direction.LEFT
const.OUT_DOOR_WALK = 8
const.DOOR_THRESH_VALUE = 66

## DIRECTION ##
const.DIRECTION_THRESH_VALUE = 30

### CORNER FILTERING ###
const.CORNER_FILTER_DISTANCE = 40

## AREA ##
const.CHECK_AREA_GREEN_RATE_THRESH = 10

### GREEN ROOM ###
## 1) BOX -> AREA
const.GREEN_ROOM_TURN_FIND_BOX = 3
const.GREEN_ROOM_DEFAULT_TURN_FIND_AREA = 1
const.GREEN_ROOM_DEFAULT_WALK_BEFORE_DROP_BOX = 1
const.GREEN_ROOM_AREA_IN_LIMIT = 460
## 2) AREA -> CORNER
const.GREEN_ROOM_DEFAULT_TURN_FIND_CORNER = 2
const.GREEN_ROOM_TURN_FIND_CORNER = 1

### BLACK ROOM ###
const.BLACK_ROOM_ALPHABET = "B"
const.BLACK_ROOM_DEFAULT_TURN_FIND_BOX = 3
const.BLACK_ROOM_DEFAULT_TURN_FIND_CORNER = 3
const.BLACK_ROOM_DEFAULT_OUT_ROOM_WALK = 2


### DEBUG MODE ###
debug_mode = Constant()
debug_mode.IS_ON = False
Room = namedtuple('Room', 'area_color room_name name_color')
first_room = Room(AreaColor.GREEN, "B", "RED")
second_room = Room(AreaColor.BLACK, "B", "BLUE")
third_room = Room(AreaColor.GREEN, "D", "BLUE")
debug_mode.DOOR_ALPHABET = "S"
debug_mode.DIRECTION = "LEFT"
debug_mode.ROOMS = [first_room, second_room, third_room]
