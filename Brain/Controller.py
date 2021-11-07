from Brain.Robot import Robot
from enum import Enum, auto
from Brain.DoorMission import DoorMission
from Brain.RoomMission import RoomMission, GreenRoomMission, BlackRoomMission
from Brain.Constant import Direction, AreaColor
import time


CLEAR_LIMIT: int = 3

class Mode(Enum):
    START = auto()
    IN = auto()
    CHECK_AREA_COLOR = auto()
    ROOM_MISSION = auto()
    GO_TO_NEXT_ROOM = auto()
    OUT = auto()
    END = auto()

class Controller:
    robot = Robot()
    line_info: dict
    edge_info: dict
    mode: Mode = Mode.START
    direction: Direction.LEFT
    mission_done: int = 0

    @classmethod
    def check_go_to_next_room(cls) -> bool:
        return False if cls.mission_done > CLEAR_LIMIT else True

    @classmethod
    def set_line_and_edge_info(cls) -> None:
        cls.line_info, cls.edge_info = cls.robot.line_tracing()

    @classmethod
    def go_to_next_room(cls) -> bool :
        return True

    @classmethod
    def run(cls):
        cls.set_line_and_edge_info()

        if cls.mode == Mode.START:
            cls.mode = Mode.IN

        elif cls.mode == Mode.IN:
            if DoorMission.run():
                cls.mode = Mode.GO_TO_NEXT_ROOM


        elif cls.mode == Mode.GO_TO_NEXT_ROOM:
            if cls.go_to_next_room():
                cls.mode = Mode.CHECK_AREA_COLOR

        elif cls.mode == Mode.CHECK_AREA_COLOR:
            RoomMission.set_line_ang_edge_info(cls.line_info, cls.edge_info)
            if RoomMission.check_area_color():
                cls.mode = Mode.ROOM_MISSION

        elif cls.mode == Mode.ROOM_MISSION:
            Mission = GreenRoomMission if RoomMission.area_color == AreaColor.GREEN else BlackRoomMission
            if Mission.run():
                cls.mission_done += 1
                if cls.check_go_to_next_room():
                    cls.mode = Mode.GO_TO_NEXT_ROOM
                else:
                    cls.mode = Mode.OUT

        elif cls.mode == Mode.OUT:
            DoorMission.run()
        elif cls.mode == Mode.END:
            return True

        return False
