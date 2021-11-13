from Brain.Robot import Robot
from Constant import Direction, AreaColor, LineColor, WalkInfo, const
from enum import Enum, auto
from collections import deque
import time
import math

DEBUG = const.ROOM_MISSION_DEBUG

class Mode(Enum):
    START = auto()
    DETECT_ALPHABET = auto()
    FIND_BOX = auto()
    TRACK_BOX = auto()
    TURN_TO_AREA = auto()
    DROP_BOX = auto()
    GO_TO_AREA = auto()
    FIND_YELLOW_LINE = auto()
    GO_OUT_AREA = auto()
    FIND_CONRER = auto()
    GO_TO_CORNER = auto()
    OUT_ROOM = auto()
    END = auto()

class BoxPos(Enum):
    RIGHT = auto()
    MIDDLE = auto()
    LEFT = auto()

def get_distance_from_baseline(pos: tuple, baseline: tuple = (320, 370)):
    """
    :param box_info: 우유팩 위치 정보를 tuple 형태로 받아온다. 우유팩 영역 중심 x좌표와 y좌표 순서
    :param baseline: 우유팩 위치 정보와 비교할 기준점이다.
    :return: 우유팩이 지정한 기준점으로부터 떨어진 상대적 거리를 tuple로 반환한다.
    """
    bx, by = baseline
    cx, cy = pos
    return bx - cx, by - cy

def corner_filtering(corner:tuple, line_info:dict):
    if corner is None:
        return False
    cx, cy = corner[0], corner[1]
    max_y = line_info["ALL_Y"][1]
    dy = abs(max_y-cy)
    return dy <= const.CORNER_FILTER_DISTANCE

def get_slope_from_baseline(pos: tuple, base: tuple=(320,480)) -> float :
    cx, cy = pos
    bx, by = base
    dx, dy = cx - bx, cy - by
    return math.atan(dx/dy)


class RoomMission:

    mode: Mode = Mode.START
    robot: Robot
    head: deque

    alphabet_color: str
    alphabet: str
    area_color: AreaColor
    
    @classmethod
    def reset(cls):
        cls.mode = Mode.START
        cls.set_robot(robot=cls.robot)

    @classmethod
    def set_robot(cls, robot:Robot):
        cls.robot = robot

        cls.robot.curr_head4room_alphabet = deque([85, 80])
        cls.robot.curr_head4box = deque([75, 60, 35])


    @classmethod
    def check_area_color(cls):
        cls.robot._motion.set_head(dir=cls.robot.direction.name, angle=45)
        cls.robot._motion.set_head(dir="DOWN", angle=45)
        time.sleep(0.2)
        cls.robot.color = LineColor.GREEN
        cls.robot.set_line_and_edge_info()
        
        print(cls.robot.edge_info)
        print(cls.robot.line_info)
        cls.area_color = AreaColor.GREEN if cls.robot.edge_info["EDGE_DOWN"] else AreaColor.BLACK
        
        cls.robot._motion.notice_area(area=cls.area_color.name)
        cls.robot._motion.set_head(dir="LEFTRIGHT_CENTER")
        cls.robot.color = LineColor.GREEN if cls.area_color == AreaColor.GREEN else LineColor.BLACK
        return True
    
    @classmethod
    def detect_alphabet(cls) -> bool:

        alphabet_info = cls.robot._image_processor.get_alphabet_info4room(visualization=DEBUG, edge_info=cls.robot.edge_info)
        if alphabet_info:
            cls.alphabet_color, cls.alphabet = alphabet_info
            return True
        else:
            cls.robot.curr_head4room_alphabet.rotate(-1)
            head_angle = cls.robot.curr_head4room_alphabet[0]
            cls.robot._motion.set_head("DOWN", angle=head_angle)
            return False

    @classmethod
    def find_box(cls) -> bool:
        pass
    
    @classmethod
    def track_box(cls) -> bool:
        """
        :return: if grab box return True else False
        """
        head_angle = cls.robot.curr_head4box[0]
        box_info = cls.robot._image_processor.get_milk_info(color=cls.alphabet_color)
        
        width = False if head_angle == 35 else True
        if box_info:
            (dx, dy) = get_distance_from_baseline(pos=box_info)

            if dy > 10:  # 기준선 보다 위에 있다면
                if -40 <= dx <= 40:
                    print("기준점에서 적정범위. 전진 전진")
                    cls.robot._motion.walk(dir='FORWARD', loop=1, width=width)
                elif dx <= -90:
                    cls.robot._motion.turn(dir='RIGHT', loop=1)
                elif -90 < dx <= -50:  # 오른쪽
                    print("기준점에서 오른쪽으로 많이 치우침. 조정한다")
                    cls.robot._motion.walk(dir='RIGHT', loop=2)
                elif -50 < dx < -40:
                    cls.robot._motion.walk(dir='RIGHT', loop=1)
                    print("기준점에서 오른쪽으로 치우침. 조정한다")
                elif 90 > dx >= 50:  # 왼쪽
                    print("기준점에서 왼쪽으로 많이 치우침. 조정한다")
                    cls.robot._motion.walk(dir='LEFT', loop=2)
                elif 50 > dx > 40:  # 왼쪽
                    print("기준점에서 왼쪽으로 치우침. 조정한다")
                    cls.robot._motion.walk(dir='LEFT', loop=2)

                elif dx >= 90:
                    cls.robot._motion.turn(dir='LEFT', loop=1)

            else:
                if head_angle == 35:
                    cls.robot._motion.grab(switch=True)
                    return True
                else:
                    cls.robot.curr_head4box.rotate(-1)
                    head_angle = cls.robot.curr_head4box[0]
                    cls.robot._motion.set_head("DOWN", angle=head_angle)

        else:
            cls.mode = Mode.FIND_BOX

        return False

    @classmethod
    def drop_box(cls) -> bool:
        cls.robot._motion.walk(dir='FORWARD', loop=2, grab=True)
        cls.robot._motion.grab(switch=False)
        cls.robot.color = LineColor.YELLOW
        return True

    @classmethod
    def turn_to_area(cls) -> bool:
        pass
    
    @classmethod
    def go_to_area(cls) -> bool:
        pass

    @classmethod
    def find_corner(cls) -> bool:
        pass
    
    @classmethod
    def go_to_corner(cls) -> bool:
        pass

    @classmethod
    def out_room(cls) -> bool:
        if cls.robot.line_info["V"]:
            if 300 < cls.robot.line_info["V_X"][0] < 340:
                cls.robot._motion.walk(dir='FORWARD', loop=2)
                return True
            elif cls.robot.line_info["V_X"][0] <= 300:
                cls.robot._motion.walk(dir='LEFT', loop=1)
            else:
                cls.robot._motion.walk(dir='RIGHT', loop=1)
        else:
            cls.robot._motion.turn(dir=cls.robot.direction.name, loop=1)
    
    @classmethod
    def run(cls) -> bool:
        pass
        

class GreenRoomMission(RoomMission):

    box_pos: BoxPos
    fast_turn : Direction

    @classmethod
    def find_box(cls) -> bool:

        head_angle = cls.robot.curr_head4box[0]
        box_info = cls.robot._image_processor.get_milk_info(color=cls.alphabet_color)

        if box_info:
            if cls.robot.direction == Direction.LEFT:
                cls.fast_turn = Direction.LEFT if cls.box_pos == BoxPos.RIGHT else Direction.RIGHT
            else:
                cls.fast_turn = Direction.RIGHT if cls.box_pos == BoxPos.LEFT else Direction.LEFT
            return True
        else:
            if head_angle == 35:
                cls.robot._motion.turn(dir=cls.robot.direction.name, loop=const.GREEN_ROOM_DEFAULT_TURN_FIND_BOX)
                cls.update_box_pos(box_info=box_info)
            cls.robot.curr_head4box.rotate(-1)
            head_angle = cls.robot.curr_head4box[0]
            cls.robot._motion.set_head("DOWN", angle=head_angle)
            return False

    @classmethod
    def update_box_pos(cls, box_info: tuple):
        cls.box_pos = BoxPos.LEFT if cls.robot.direction == Direction.LEFT else BoxPos.RIGHT

    @classmethod
    def turn_to_area(cls) -> bool:

        is_horizon: bool = cls.robot.line_info["H"] and cls.robot.line_info["len(H)"] >= 300
        is_in_area: bool
        if cls.box_pos == "RIGHT":
            is_in_area = cls.robot.line_info["H_X"][0] < const.GREEN_ROOM_AREA_LEFT_LIMIT
        else:
            is_in_area = cls.robot.line_info["H_X"][1] > const.GREEN_ROOM_AREA_RIGHT_LIMIT
        
        found_area: bool = is_horizon and is_in_area
        
        if found_area :
            cls.robot._motion.move_arm(dir='HIGH')
            return True
        else:
            if is_horizon:
                cls.robot._motion.turn(dir=cls.fast_turn.name, grab=True, loop=1)
            else:
                if cls.box_pos == "LEFT":
                    cls.robot._motion.walk(dir="LEFT", grab=True, loop=1)
                else:
                    cls.robot._motion.walk(dir="RIGHT", grab=True, loop=1)
        return False

    @classmethod
    def go_to_area(cls) -> bool:
        in_area: bool = cls.robot.line_info['ALL_Y'][1] > const.GREEN_ROOM_AREA_IN_LIMIT
        if in_area:
            return True
        cls.robot._motion.walk(dir="FORWARD", loop=1, grab=True)
        return False


    @classmethod
    def find_corner(cls) -> bool:
        head_angle = cls.robot.curr_head4find_corner[0]
        corner = cls.robot._image_processor.get_yellow_line_corner(visualization=DEBUG)
        corner = corner if corner_filtering(corner=corner, line_info=cls.robot.line_info) else None
        if corner :
            return True
        else:
            if head_angle == 35:
                if cls.box_pos == BoxPos.RIGHT:
                    cls.robot._motion.turn(dir=Direction.LEFT.name, loop=2)
                else:
                    cls.robot._motion.turn(dir=Direction.RIGHT.name, loop=2)
            cls.robot.curr_head4find_corner.rotate(-1)
            head_angle = cls.robot.curr_head4find_corner[0]
            cls.robot._motion.set_head("DOWN", angle=head_angle)
        return False

    @classmethod
    def go_to_corner(cls) -> bool:
        head_angle = cls.robot.curr_head4find_corner[0]
        width = False if head_angle == 35 else True
        corner = cls.robot._image_processor.get_yellow_line_corner(visualization=DEBUG)
        corner = corner if corner_filtering(corner=corner, line_info=cls.robot.line_info) else None
        if corner :
            (dx, dy) = get_distance_from_baseline(pos=corner)
            if dy > 10:  # 기준선 보다 위에 있다면
                if -50 <= dx <= 50:
                    cls.robot._motion.walk(dir='FORWARD', loop=1, width=width)
                elif dx <= -70:
                    cls.robot._motion.turn(dir='RIGHT', loop=1)
                elif -70 < dx <= -50:  # 오른쪽
                    cls.robot._motion.walk(dir='RIGHT', loop=1)
                elif 70 > dx >= 50:  # 왼쪽
                    cls.robot._motion.walk(dir='LEFT', loop=1)
                elif dx >= 70:
                    cls.robot._motion.turn(dir='LEFT', loop=1)
            else:
                if head_angle == 35:
                    #cls.robot._motion.walk(dir='FORWARD', loop=1, width=width)
                    return True
                else:
                    cls.robot.curr_head4find_corner.rotate(-1)
                    head_angle = cls.robot.curr_head4find_corner[0]
                    cls.robot._motion.set_head("DOWN", angle=head_angle)
        else:
            cls.mode = Mode.FIND_CONRER
        return False


    @classmethod
    def run(cls):
        mode = cls.mode
        print(mode.name)

        if mode == Mode.START:
            cls.mode = Mode.DETECT_ALPHABET
            cls.robot._motion.set_head("DOWN", angle=cls.robot.curr_head4room_alphabet[0])

        elif mode == Mode.DETECT_ALPHABET:
            if cls.detect_alphabet():
                cls.mode = Mode.FIND_BOX
                cls.box_pos = BoxPos.RIGHT if cls.robot.direction == Direction.LEFT else BoxPos.LEFT
                cls.robot._motion.set_head("DOWN", angle=cls.robot.curr_head4box[0])

        elif mode == Mode.FIND_BOX:
            if cls.find_box():
                cls.mode = Mode.TRACK_BOX

        elif mode == Mode.TRACK_BOX:
            if cls.track_box():
                cls.mode = Mode.TURN_TO_AREA
                cls.robot._motion.turn(dir=cls.fast_turn.name, grab=True, wide=True, sliding=True, loop=const.GREEN_ROOM_DEFAULT_TURN_FIND_AREA)

        elif mode == Mode.TURN_TO_AREA:
            if cls.turn_to_area():
                cls.mode = Mode.GO_TO_AREA

        elif mode == Mode.GO_TO_AREA:
            if cls.go_to_area():
                cls.mode = Mode.DROP_BOX

        elif mode == Mode.DROP_BOX:
            if cls.drop_box():
                cls.mode = Mode.FIND_CONRER
                cls.robot.curr_head4find_corner = deque([60, 45, 35])
                cls.robot._motion.set_head("DOWN", angle=cls.robot.curr_head4find_corner[0])
                cls.robot.color = LineColor.YELLOW
                cls.robot._motion.turn(dir=cls.fast_turn.name, loop=const.GREEN_ROOM_DEFAULT_TURN_FIND_CORNER, wide=True, sliding=True)

        elif mode == Mode.FIND_CONRER:
            if cls.find_corner():
                cls.mode = Mode.GO_TO_CORNER

        elif mode == Mode.GO_TO_CORNER:
            if cls.go_to_corner():
                cls.mode = cls.mode = Mode.OUT_ROOM
                loop: int = 4 if cls.fast_turn == Direction.RIGHT else 2
                cls.robot._motion.turn(dir=cls.robot.direction.name, loop=loop)
                
        elif mode == Mode.OUT_ROOM:
            if cls.out_room():
                cls.mode = Mode.END

        elif mode == Mode.END:
            return True
        
        return False

class BlackRoomMission(RoomMission):

    @classmethod
    def turn_to_area(cls) -> bool:

        return True


    @classmethod
    def find_box(cls) -> bool:

        head_angle = cls.robot.curr_head4box[0]
        time.sleep(0.2)
        cls.robot.set_line_and_edge_info()
        box_info = cls.robot._image_processor.get_milk_info(color=cls.alphabet_color)

        if box_info:
            return True
        else:
            if head_angle == 35:
                cls.robot._motion.turn(dir=cls.robot.direction.name, loop=2)
            cls.robot.curr_head4box.rotate(-1)
            head_angle = cls.robot.curr_head4box[0]
            cls.robot._motion.set_head("DOWN", angle=head_angle)
            return False


    @classmethod
    def find_yellow_line(cls) -> bool:
        if cls.robot.line_info["ALL_Y"][1]:
            cls.robot._motion.walk(dir="FORWARD", grab=True, loop=const.BLACK_ROOM_DEFAULT_OUT_ROOM_WALK)
            return True
        cls.robot._motion.turn(dir=cls.robot.direction.name, grab=True, wide=True, sliding=True, loop=1)
        return False



    @classmethod
    def find_corner(cls) -> bool:

        corner = cls.robot._image_processor.get_yellow_line_corner(visualization=DEBUG)
        corner = corner if corner_filtering(corner=corner, line_info=cls.robot.line_info) else None
        if corner:
            return True
        else:
            if cls.robot.curr_head4find_corner[0] == 35:
                cls.robot._motion.turn(dir=cls.robot.direction.name, loop=2)
            cls.robot.curr_head4find_corner.rotate(-1)
            head_angle = cls.robot.curr_head4find_corner[0]
            cls.robot._motion.set_head("DOWN", angle=head_angle)


    @classmethod
    def go_to_corner(cls) -> bool :
        head_angle = cls.robot.curr_head4find_corner[0]
        width = False if head_angle == 35 else True
        corner = cls.robot._image_processor.get_yellow_line_corner(visualization=DEBUG)
        if corner:
            (dx, dy) = get_distance_from_baseline(pos=corner)
            if dy > 10:  # 기준선 보다 위에 있다면
                if -50 <= dx <= 50:
                    cls.robot._motion.walk(dir='FORWARD', loop=1, width=width)
                elif dx <= -70:
                    cls.robot._motion.turn(dir='RIGHT', loop=1)
                elif -70 < dx <= -50:  # 오른쪽
                    cls.robot._motion.walk(dir='RIGHT', loop=1)
                elif 70 > dx >= 50:  # 왼쪽
                    cls.robot._motion.walk(dir='LEFT', loop=1)
                elif dx >= 70:
                    cls.robot._motion.turn(dir='LEFT', loop=1)
            else:
                if head_angle == 35:
                    cls.robot._motion.walk(dir='FORWARD', loop=1, width=width)
                    return True
                else:
                    cls.robot.curr_head4find_corner.rotate(-1)
                    head_angle = cls.robot.curr_head4find_corner[0]
                    cls.robot._motion.set_head("DOWN", angle=head_angle)
        else:
            cls.mode = Mode.FIND_CONRER
        return False


    @classmethod
    def go_out_area(cls) -> bool:
        cls.robot._motion.walk(dir="FORWARD", grab=True, loop=1)
        if cls.robot._image_processor.is_out_of_black():
            return True
        else:
            return False


    
    @classmethod
    def run(cls):
        mode = cls.mode
        print(mode.name)
        
        if mode == Mode.START:
            cls.mode = Mode.DETECT_ALPHABET
            cls.robot._motion.set_head("DOWN", angle=cls.robot.curr_head4room_alphabet[0])
            
        elif mode == Mode.DETECT_ALPHABET:
            if cls.detect_alphabet():
                cls.robot.black_room.append(cls.alphabet)
                cls.mode = Mode.FIND_BOX
                cls.robot._motion.set_head("DOWN", angle=cls.robot.curr_head4box[0])
                cls.robot._motion.turn(dir=cls.robot.direction.name, loop=const.BLACK_ROOM_DEFAULT_TURN_FIND_BOX)

                
        elif mode == Mode.FIND_BOX:
            if cls.find_box():
                cls.mode = Mode.TRACK_BOX

        elif mode == Mode.TRACK_BOX:
            if cls.track_box():
                cls.mode = Mode.FIND_YELLOW_LINE
                cls.robot.color = LineColor.YELLOW
                cls.robot._motion.set_head("DOWN", angle=60)
                cls.robot._motion.turn(dir=cls.robot.direction.name, grab=True, wide=True, sliding=True, loop=const.BLACK_ROOM_DEFAULT_TURN_FIND_CORNER)

        elif mode == Mode.FIND_YELLOW_LINE:
            if cls.find_yellow_line():
                cls.mode = Mode.GO_OUT_AREA
                cls.robot._motion.set_head("DOWN", angle=35)

        elif mode == Mode.GO_OUT_AREA:
            if cls.go_out_area():
                cls.mode = Mode.DROP_BOX

        elif mode == Mode.DROP_BOX:
            if cls.drop_box():
                cls.mode = Mode.FIND_CONRER
                cls.robot.curr_head4find_corner = deque([55, 45, 35])

        elif mode == Mode.FIND_CONRER:
            if cls.find_corner():
                cls.mode = Mode.GO_TO_CORNER
                
        elif mode == Mode.GO_TO_CORNER:
            if cls.go_to_corner():
                cls.mode = Mode.OUT_ROOM
                
        elif mode == Mode.OUT_ROOM:
            if cls.out_room():
                cls.mode = Mode.END
                
        elif mode == Mode.END:
            return True
        
        return False