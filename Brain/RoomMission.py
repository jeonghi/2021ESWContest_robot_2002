from Brain.Controller import Controller
from enum import Enum, auto

robot = Controller.robot

class Mode(Enum):
    START = auto()
    DETECT_ALPHABET = auto()
    FIND_BOX = auto()
    TRACK_BOX = auto()
    TURN_TO_AREA = auto()
    GO_TO_AREA = auto()
    FIND_CONRER = auto()
    GO_TO_CORNER = auto()
    END = auto()

class BoxPos(Enum):
    RIGHT = auto()
    MIDDLE = auto()
    LEFT = auto()

def get_distance_from_baseline(box_info: tuple, baseline: tuple = (320, 370)):
    """
    :param box_info: 우유팩 위치 정보를 tuple 형태로 받아온다. 우유팩 영역 중심 x좌표와 y좌표 순서
    :param baseline: 우유팩 위치 정보와 비교할 기준점이다.
    :return: 우유팩이 지정한 기준점으로부터 떨어진 상대적 거리를 tuple로 반환한다.
    """
    bx, by = baseline
    cx, cy = box_info
    return bx - cx, by - cy

class RoomMission:

    mode: Mode = Mode.START
    
    line_info: dict = {}
    edge_info: dict = {}

    alphabet_color: str
    alphabet: str
    box_pos: BoxPos.LEFT
    
    @classmethod
    def detect_alphabet(cls) -> bool:
        head_angle = robot.curr_head4room_alphabet[0]
        robot._motion.set_head("DOWN", angle=head_angle)
        alphabet_info = robot._image_processor.get_alphabet_info4room(edge_info=cls.edge_info)
        if alphabet_info:
            cls.alphabet_color, cls.alphabet = alphabet_info
            return True
        else:
            robot.curr_head4room_alphabet.rotate(-1)
            return False

    @classmethod
    def find_box(cls) -> bool:
        head_angle = robot.curr_head4box[0]
        robot._motion.set_head("DOWN", angle=head_angle)
        box_info = robot._image_processor.get_milk_info(color=cls.alphabet_color, edge_info=cls.edge_info)
        if box_info:
            return True
        else:
            if head_angle == 35:
                robot._motion.turn(dir=Controller.direction, loop=7)
            robot.curr_head4box.rotate(-1)
            return False
    
    @classmethod
    def track_box(cls) -> bool:
        """

        :return: if grab box return True else False
        """
        head_angle = robot.curr_head4box[0]
        robot._motion.set_head("DOWN", angle=head_angle)
        box_info = robot._image_processor.get_milk_info(color=cls.alphabet_color, edge_info=cls.edge_info)
        if box_info:
            (dx, dy) = get_distance_from_baseline(box_info=box_info)

            if dy > 10:  # 기준선 보다 위에 있다면
                if -40 <= dx <= 40:
                    print("기준점에서 적정범위. 전진 전진")
                    if robot.curr_head4box[0] == 75:
                        robot._motion.walk(dir='FORWARD', loop=2)
                    else:
                        robot._motion.walk(dir='FORWARD', loop=1)
                elif dx <= -90:
                    if robot.curr_head4box[0] == 75:
                        robot._motion.turn(dir='RIGHT', sleep=0.1, loop=2)
                    else:
                        robot._motion.walk(dir='RIGHT', loop=1)
                elif -90 < dx <= -50:  # 오른쪽
                    print("기준점에서 오른쪽으로 많이 치우침. 조정한다")
                    if robot.curr_head4box[0] == 75:
                        robot._motion.walk(dir='RIGHT', loop=2)
                    else:
                        robot._motion.walk(dir='RIGHT', loop=2)
                elif -50 < dx < -40:
                    if head_angle == 75:
                        robot._motion.walk(dir='RIGHT', loop=1)
                    else:
                        robot._motion.walk(dir='RIGHT', loop=1)
                    print("기준점에서 오른쪽으로 치우침. 조정한다")
                elif 90 > dx >= 50:  # 왼쪽
                    print("기준점에서 왼쪽으로 많이 치우침. 조정한다")
                    if head_angle == 75:
                        robot._motion.walk(dir='LEFT', loop=2)
                    else:
                        robot._motion.walk(dir='LEFT', loop=2)
                elif 50 > dx > 40:  # 왼쪽
                    print("기준점에서 왼쪽으로 치우침. 조정한다")
                    if head_angle == 75:
                        robot._motion.walk(dir='LEFT', loop=1)
                    else:
                        robot._motion.walk(dir='LEFT', loop=2)

                elif dx >= 90:
                    if head_angle == 75:
                        robot._motion.turn(dir='LEFT', sleep=0.1, loop=2)
                    else:
                        robot._motion.walk(dir='LEFT', loop=1)

            else:
                if head_angle == 35:
                    robot._motion.grab(switch=True)
                    return True
                else:
                    robot.curr_head4box.rotate(-1)

        else:
            cls.mode = Mode.FIND_BOX

        return False

    
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

    @classmethod
    def turn_to_area(cls) -> bool:

        if cls.line_info["H"] and cls.line_info["len(H)"] >= 300:
            return True

        if cls.box_pos == BoxPos.RIGHT:
            robot._motion.turn(dir="LEFT", loop=1, grab=True)
        else:
            robot._motion.turn(dir="RIGHT", loop=1, grab=True)

        return False

    @classmethod
    def go_to_area(cls) -> bool:
        pass



    @classmethod
    def go_to_corner(cls):
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

        elif mode == Mode.TRACK_BOX :
            if cls.track_box():
                cls.mode = Mode.TURN_TO_AREA

        elif mode == Mode.TURN_TO_AREA:
            if cls.turn_to_area():
                cls.mode = Mode.GO_TO_AREA


        elif mode == Mode.GO_TO_AREA:
            pass
        elif mode == Mode.FIND_CONRER:
            pass
        elif mode == Mode.GO_TO_CORNER:
            pass
        elif mode == Mode.END:
            return True
        
        return False

class BlackRoomMission(RoomMission):

    @classmethod
    def turn_to_area(cls) -> bool:
        cls.robot._motion.turn()
        return True

    @classmethod
    def go_to_area(cls) -> bool:
        cls.go_to_area()

    @classmethod
    def find_corner(cls) -> bool:
        cls.find_corner()

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
                cls.mode = Mode.END
                
        elif mode == Mode.END:
            return True
        
        return False