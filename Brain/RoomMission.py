from Brain.Robot import Robot
from Brain.Constant import Direction, AreaColor, LineColor
from enum import Enum, auto
import time

class Mode(Enum):
    START = auto()
    DETECT_ALPHABET = auto()
    FIND_BOX = auto()
    TRACK_BOX = auto()
    TURN_TO_AREA = auto()
    DROP_BOX = auto()
    GO_TO_AREA = auto()
    FIND_CONRER = auto()
    GO_TO_CORNER = auto()
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

class RoomMission:

    mode: Mode = Mode.START
    robot: Robot = Robot

    alphabet_color: str
    alphabet: str
    area_color: AreaColor

    @classmethod
    def set_robot(cls, robot:Robot):
        cls.robot = robot


    @classmethod
    def check_area_color(cls):
        cls.robot._motion.set_head(dir=cls.robot.direction.name, angle=45)
        cls.robot._motion.set_head(dir="DOWN", angle=45)
        time.sleep(0.5)
        cls.area_color = AreaColor.GREEN if cls.robot.edge_info["EDGE_DOWN"] else AreaColor.BLACK
        cls.robot._motion.notice_area(area=cls.area_color.name)
        cls.robot._motion.set_head(dir="LEFTRIGHT_CENTER")
        cls.robot.color = cls.area_color.name
        return True
    
    @classmethod
    def detect_alphabet(cls) -> bool:
        head_angle = cls.robot.curr_head4room_alphabet[0]
        cls.robot._motion.set_head("DOWN", angle=head_angle)
        alphabet_info = cls.robot._image_processor.get_alphabet_info4room(edge_info=cls.robot.edge_info)
        if alphabet_info:
            cls.alphabet_color, cls.alphabet = alphabet_info
            return True
        else:
            cls.robot.curr_head4room_alphabet.rotate(-1)
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
        cls.robot._motion.set_head("DOWN", angle=head_angle)
        box_info = cls.robot._image_processor.get_milk_info(color=cls.alphabet_color, edge_info=cls.robot.edge_info)
        if box_info:
            (dx, dy) = get_distance_from_baseline(pos=box_info)

            if dy > 10:  # 기준선 보다 위에 있다면
                if -40 <= dx <= 40:
                    print("기준점에서 적정범위. 전진 전진")
                    if cls.robot.curr_head4box[0] == 75:
                        cls.robot._motion.walk(dir='FORWARD', loop=2)
                    else:
                        cls.robot._motion.walk(dir='FORWARD', loop=1)
                elif dx <= -90:
                    if cls.robot.curr_head4box[0] == 75:
                        cls.robot._motion.turn(dir='RIGHT', sleep=0.1, loop=2)
                    else:
                        cls.robot._motion.walk(dir='RIGHT', loop=1)
                elif -90 < dx <= -50:  # 오른쪽
                    print("기준점에서 오른쪽으로 많이 치우침. 조정한다")
                    if cls.robot.curr_head4box[0] == 75:
                        cls.robot._motion.walk(dir='RIGHT', loop=2)
                    else:
                        cls.robot._motion.walk(dir='RIGHT', loop=2)
                elif -50 < dx < -40:
                    if head_angle == 75:
                        cls.robot._motion.walk(dir='RIGHT', loop=1)
                    else:
                        cls.robot._motion.walk(dir='RIGHT', loop=1)
                    print("기준점에서 오른쪽으로 치우침. 조정한다")
                elif 90 > dx >= 50:  # 왼쪽
                    print("기준점에서 왼쪽으로 많이 치우침. 조정한다")
                    if head_angle == 75:
                        cls.robot._motion.walk(dir='LEFT', loop=2)
                    else:
                        cls.robot._motion.walk(dir='LEFT', loop=2)
                elif 50 > dx > 40:  # 왼쪽
                    print("기준점에서 왼쪽으로 치우침. 조정한다")
                    if head_angle == 75:
                        cls.robot._motion.walk(dir='LEFT', loop=1)
                    else:
                        cls.robot._motion.walk(dir='LEFT', loop=2)

                elif dx >= 90:
                    if head_angle == 75:
                        cls.robot._motion.turn(dir='LEFT', sleep=0.1, loop=2)
                    else:
                        cls.robot._motion.walk(dir='LEFT', loop=1)

            else:
                if head_angle == 35:
                    cls.robot._motion.grab(switch=True)
                    return True
                else:
                    cls.robot.curr_head4box.rotate(-1)

        else:
            cls.mode = Mode.FIND_BOX

        return False

    @classmethod
    def drop_box(cls) -> bool:
        cls.robot._motion.walk(dir='FORWARD', loop=2, grab=True)
        cls.robot._motion.grab(switch=False)
        cls.robot.color = LineColor.YELLOW
        time.sleep(0.5)
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
    def run(cls) -> bool:
        pass
        

class GreenRoomMission(RoomMission):

    box_pos: BoxPos

    @classmethod
    def find_box(cls) -> bool:

        head_angle = cls.robot.curr_head4box[0]
        cls.robot._motion.set_head("DOWN", angle=head_angle)
        box_info = cls.robot._image_processor.get_milk_info(color=cls.alphabet_color, edge_info=cls.robot.edge_info)

        if box_info:
            cls.update_box_pos(box_info=box_info)
            return True
        else:
            if head_angle == 35:
                cls.robot._motion.turn(dir=cls.robot.direction.name, loop=8)
            cls.robot.curr_head4box.rotate(-1)
            return False

    @classmethod
    def update_box_pos(cls, box_info: tuple):

        if cls.robot.edge_info["EDGE_DOWN"]:
            cor_x, cor_y = cls.robot.edge_info["EDGE_DOWN_X"], cls.robot.edge_info["EDGE_DOWN_Y"]
            (box_x, box_y) = box_info
            dx = 30
            if cor_x - dx <= box_x <= cor_x + dx:
                cls.box_pos = BoxPos.MIDDLE
            elif box_x < cor_x - dx:
                cls.box_pos = BoxPos.LEFT
            else:
                cls.box_pos = BoxPos.RIGHT
        else:
            cls.box_pos = BoxPos.RIGHT if cls.robot.direction == Direction.LEFT else BoxPos.LEFT

    @classmethod
    def turn_to_area(cls) -> bool:

        found_area: bool = cls.robot.line_info["H"] and cls.robot.line_info["len(H)"] >= 300

        if found_area :
            cls.robot._motion.move_arm(dir='HIGH')
            return True

        if cls.box_pos == BoxPos.RIGHT:
            cls.robot._motion.turn(dir="LEFT", loop=1, grab=True)
        else:
            cls.robot._motion.turn(dir="RIGHT", loop=1, grab=True)
        return False

    @classmethod
    def go_to_area(cls) -> bool:
        in_area: bool = cls.robot.line_info['ALL_Y'][1] > 460
        if in_area:
            return True
        cls.robot._motion.walk(dir="FORWARD", loop=1, grab=True)
        return False


    @classmethod
    def find_corner(cls) -> bool:
        head_angle = cls.robot.curr_head4find_corner[0]
        cls.robot.motion.set_head("DOWN", angle=head_angle)
        corner = cls.robot._image_processor.get_yellow_line_corner()
        if corner:
            return True
        else:
            if head_angle == 35:
                if cls.box_pos == BoxPos.RIGHT:
                    cls.robot._motion.turn(dir=Direction.LEFT.name, loop=2)
                else:
                    cls.robot._motion.turn(dir=Direction.RIGHT.name, loop=2)
            cls.robot.curr_head4find_corner.rotate(-1)

    @classmethod
    def go_to_corner(cls) -> bool:
        head_angle = cls.robot.curr_head4find_corner[0]
        cls.robot.motion.set_head("DOWN", angle=head_angle)
        corner = cls.robot._image_processor.get_yellow_line_corner()
        if corner:
            (dx, dy) = get_distance_from_baseline(pos=corner)
            if dy > 10:  # 기준선 보다 위에 있다면
                if -40 <= dx <= 40:
                    cls.robot._motion.walk(dir='FORWARD', loop=1)
                elif dx <= -90:
                    cls.robot._motion.walk(dir='RIGHT', loop=1)
                elif -90 < dx <= -50:  # 오른쪽
                    cls.robot._motion.walk(dir='RIGHT', loop=2)
                elif -50 < dx < -40:
                    cls.robot._motion.walk(dir='RIGHT', loop=1)
                elif 90 > dx >= 50:  # 왼쪽
                    cls.robot._motion.walk(dir='LEFT', loop=2)
                elif 50 > dx > 40:  # 왼쪽
                    cls.robot._motion.walk(dir='LEFT', loop=2)
                elif dx >= 90:
                    cls.robot._motion.walk(dir='LEFT', loop=1)
            else:
                if head_angle == 35:
                    return True
                else:
                    cls.robot.curr_head4find_corner.rotate(-1)
        else:
            cls.mode = Mode.FIND_CONRER
        pass


    @classmethod
    def run(cls):
        mode = cls.mode
        if mode == Mode.START:
            cls.mode = Mode.DETECT_ALPHABET

        elif mode == Mode.DETECT_ALPHABET:
            if cls.detect_alphabet():
                cls.mode = Mode.FIND_BOX

        elif mode == Mode.FIND_BOX:
            if cls.find_box():
                cls.mode = Mode.TRACK_BOX

        elif mode == Mode.TRACK_BOX:
            if cls.track_box():
                cls.mode = Mode.TURN_TO_AREA

        elif mode == Mode.TURN_TO_AREA:
            if cls.turn_to_area():
                cls.mode = Mode.GO_TO_AREA

        elif mode == Mode.GO_TO_AREA:
            if cls.go_to_area():
                cls.mode = Mode.DROP_BOX

        elif mode == Mode.DROP_BOX:
            if cls.drop_box():
                cls.mode = Mode.FIND_CONRER

        elif mode == Mode.FIND_CONRER:
            if cls.find_corner():
                cls.mode = Mode.GO_TO_CORNER

        elif mode == Mode.GO_TO_CORNER:
            if cls.go_to_corner():
                cls.mode = Mode.END

        elif mode == Mode.END:
            return True
        
        return False

class BlackRoomMission(RoomMission):
    @classmethod
    def find_box(cls) -> bool:

        head_angle = cls.robot.curr_head4box[0]
        cls.robot._motion.set_head("DOWN", angle=head_angle)
        box_info = cls.robot._image_processor.get_milk_info(color=cls.alphabet_color, edge_info=cls.robot.edge_info)

        if box_info:
            return True
        else:
            if head_angle == 35:
                cls.robot._motion.turn(dir=cls.robot.direction.name, loop=2)
            cls.robot.curr_head4box.rotate(-1)
            return False

    @classmethod
    def turn_to_area(cls) -> bool:
        cls.robot._motion.turn(dir=cls.robot.direction.name, loop=4)
        return True

    @classmethod
    def find_corner(cls) -> bool:
        arm_pos = cls.robot.curr_arm_pos[0]
        cls.robot._motion.move_arm(arm_pos)
        corner = cls.robot._image_processor.get_yellow_line_corner()
            
        if corner:
            return True
        else:
            if arm_pos == 'MIDDLE':
                cls.robot._motion.turn(cls.robot.direction.name, grab=True, loop=2)         
            cls.robot.curr_arm_pos.rotate(-1)

    @classmethod
    def go_to_corner(cls):
        cls.go_to_corner()
    
    @classmethod
    def run(cls):
        mode = cls.mode
        
        if mode == Mode.START:
            cls.mode = Mode.DETECT_ALPHABET
            
        elif mode == Mode.DETECT_ALPHABET:
            if cls.detect_alphabet():
                cls.mode = Mode.TURN_TO_AREA

        elif mode == Mode.TURN_TO_AREA:
            if cls.turn_to_area():
                cls.mode = Mode.FIND_BOX
                
        elif mode == Mode.FIND_BOX:
            if cls.find_box():
                cls.mode = Mode.TRACK_BOX

        elif mode == Mode.TRACK_BOX:
            if cls.track_box():
                cls.mode = Mode.FIND_CONRER
        
        elif mode == Mode.FIND_CONRER:
            if cls.find_corner():
                cls.mode = Mode.GO_TO_CORNER
                
        elif mode == Mode.GO_TO_CORNER:
            if cls.go_to_corner():
                cls.mode = Mode.DROP_BOX

        elif mode == Mode.DROP_BOX:
            if cls.drop_box():
                cls.mode = Mode.END
                
        elif mode == Mode.END:
            return True
        
        return False