from enum import Enum, auto
from collections import namedtuple
import csv



f = open('Cts5_v1.csv', 'r', encoding='utf-8')
rdr = csv.reader(f)

for line in rdr:
    h_max = line[1]
    h_min = line[2]
    
    s_max = line[3]
    s_min = line[4]
    
    v_max = line[5]
    v_min = line[6]
    
    lower_range = [h_min, s_min, v_min]
    upper_range = [h_max, s_max, v_max]
    
    #print("color: ", line[0])
    #print(lower_range)
    #print(upper_range)



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

### COLOR SETTING ###
const = Constant()
const.RED_RANGE1 = [[0, 33, 40], [30, 201, 142]]
const.RED_RANGE2 = [[121, 20, 85], [180, 255, 145]]
const.GREEN_RANGE = [[29, 80, 30], [76, 255, 255]]
const.BLUE_RANGE = [[73, 52, 53], [124, 170, 156]]
const.BLACK_RANGE = [[0, 0, 0], [180, 255, 81]]
const.YELLOW_RANGE = [[11, 80, 129], [44, 255, 255]]

### DOOR SETTING ###
const.GRAB_IR = 70
const.IN_DOOR_WALK = 5
const.IN_DOOR_TURN = 4

### CORNER FILTERING ###
const.CORNER_FILTER_DISTANCE = 80

### GREEN ROOM ###
const.GREEN_ROOM_TURN_FIND_BOX = 3
const.GREEN_ROOM_DEFAULT_TURN_FIND_AREA = 2
const.GREEN_ROOM_DEFAULT_TURN_FIND_CORNER = 4
const.GREEN_ROOM_TURN_FIND_CORNER = 1
const.GREEN_ROOM_AREA_LEFT_LIMIT = 200
const.GREEN_ROOM_AREA_RIGHT_LIMIT = 440
const.GREEN_ROOM_AREA_IN_LIMIT = 460


### BLACK ROOM ###
const.BLACK_ROOM_DEFAULT_TURN_FIND_BOX = 3
const.BLACK_ROOM_DEFAULT_TURN_FIND_CORNER = 4
const.BLACK_ROOM_DEFAULT_OUT_ROOM_WALK = 4
const.ROOM_MISSION_DEBUG = False
const.DEBUG = False



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