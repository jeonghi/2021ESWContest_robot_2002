from Brain.Robot import Robot
from enum import Enum, auto
from Brain.DoorMission import DoorMission
from Brain.RoomMission import GreenRoomMission, BlackRoomMission
import time


CLEAR_LIMIT: int = 3

class Mode(Enum):
    IN = auto()
    ROOM_MISSION = auto()
    GO_TO_NEXT_ROOM = auto()
    OUT = auto()

class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()

class Controller:
    robot = Robot()
    line_info: tuple
    edge_info: tuple
    mode: Mode
    direction: Direction
    mission_done: int = 0
    
    @classmethod
    def check_go_to_next_room(cls) -> bool :
        return False if cls.mission_done > CLEAR_LIMIT else True
    
    @classmethod
    def get_ling_info(cls) -> tuple:
        cls.line_info, cls.edge_info = cls.robot.line_tracing()
        
    @classmethod
    def check_area_color(cls):
        cls.robot._motion.set_head(dir=cls.robot.direction, angle=45)
        cls.robot._motion.set_head(dir="DOWN", angle=45)
        time.sleep(0.5)
        cls.robot.color = "GREEN"
        cls.robot.line_tracing()
        cls.robot.curr_room_color = "GREEN" if cls.robot.edge_info["EDGE_DOWN"] else "BLACK"
        cls.robot.color = cls.robot.curr_room_color
        cls.robot._motion.notice_area(area=cls.robot.curr_room_color)
        cls.robot._motion.set_head(dir="LEFTRIGHT_CENTER")
    
    @classmethod
    def run(cls):
        cls.get_ling_info()
        if cls.mode == Mode.IN :
            DoorMission.run()
        elif cls.mode == Mode.ROOM_MISSION :

            Mission = GreenRoomMission if cls.curr_room_color == "GREEN" else BlackRoomMission
            if Mission.run():
                if cls.check_go_to_next_room():
                    cls.mode = Mode.GO_TO_NEXT_ROOM
                else:
                    cls.mode = Mode.OUT
                    
        elif cls.mode == Mode.GO_TO_NEXT_ROOM:
            pass
        elif cls.mode == Mode.OUT:
            DoorMission.run()
