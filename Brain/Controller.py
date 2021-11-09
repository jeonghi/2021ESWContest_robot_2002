from Brain.Robot import Robot
from enum import Enum, auto
from Brain.InDoorMission import InDoorMission
from Brain.OutDoorMission import OutDoorMission
from Brain.RoomMission import RoomMission, GreenRoomMission, BlackRoomMission
from Constant import Direction, AreaColor, LineColor, WalkInfo

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
    robot: Robot = Robot()
    mode: Mode = Mode.START
    mission_done: int = 0
    InDoorMission.set_robot(robot)
    OutDoorMission.set_robot(robot)
    RoomMission.set_robot(robot)
    robot.set_basic_form()
    ROI = False

    @classmethod
    def check_go_to_next_room(cls) -> bool:
        return False if cls.mission_done > CLEAR_LIMIT else True

    @classmethod
    def go_to_next_room(cls) -> bool :
        if cls.robot.walk_info == WalkInfo.STRAIGHT:
            cls.robot._motion.walk('FORWARD', 2)
        elif cls.robot.walk_info == WalkInfo.V_LEFT:
            cls.robot._motion.walk('LEFT', 1)
        elif cls.robot.walk_info == WalkInfo.V_RIGHT:
            cls.robot._motion.walk('RIGHT', 1)
        elif cls.robot.walk_info == WalkInfo.MODIFY_LEFT:
            cls.robot._motion.turn('LEFT', 1)
        elif cls.robot.walk_info == WalkInfo.MODIFY_RIGHT:
            cls.robot._motion.turn('RIGHT', 1)
        
        elif cls.robot.walk_info == WalkInfo.CORNER_LEFT:
            cls.robot._motion.walk('FORWARD', 2)
            if cls.robot.direction == Direction.RIGHT :
                return True
            else:
                if cls.mission_done >= CLEAR_LIMIT:
                    return True
                
        elif cls.robot.walk_info == WalkInfo.CORNER_RIGHT:
            cls.robot._motion.walk('FORWARD', 2)
            if cls.robot.direction == Direction.LEFT:
                return True
            else:
                if cls.mission_done >= CLEAR_LIMIT:
                    return True
        else: # WalkInfo.BACKWARD
            cls.robot._motion.walk('BACKWARD', 1)
        return False

    @classmethod
    def run(cls):
        mode = cls.mode
        cls.robot.set_line_and_edge_info(ROI=cls.ROI)
        print(mode.name)
        if mode == Mode.START:
            cls.mode = Mode.IN
            cls.ROI = True

        elif mode == Mode.IN:
            #in_Door = InDoorMission # 재훈
            if InDoorMission.run():
                cls.mode = Mode.GO_TO_NEXT_ROOM
            #cls.mode = Mode.GO_TO_NEXT_ROOM
            #cls.robot.direction = Direction.LEFT # 임시임
        
        elif mode == Mode.GO_TO_NEXT_ROOM:
            if cls.go_to_next_room():
                if cls.mission_done < CLEAR_LIMIT:
                    cls.mode = Mode.CHECK_AREA_COLOR # 미션
                    cls.ROI = False
                    cls.robot.color = LineColor.GREEN
                else:
                    out_Door = OutDoorMission # 재훈 - 시작은 H 안보일때까지 걷기 - develop Controller 확인하기
                    if out_Door.run():
                        return True # 퇴장

        elif mode == Mode.CHECK_AREA_COLOR:
            if RoomMission.check_area_color():
                cls.mode = Mode.ROOM_MISSION

        elif mode == Mode.ROOM_MISSION:
            Mission = GreenRoomMission if RoomMission.area_color == AreaColor.GREEN else BlackRoomMission
            if Mission.run():
                cls.mission_done += 1
                cls.ROI = True
                if cls.check_go_to_next_room():
                    cls.mode = Mode.GO_TO_NEXT_ROOM
                else:
                    cls.mode = Mode.OUT

        #elif mode == Mode.OUT:
            #DoorMission.run()
        
        #elif mode == Mode.END:
            #return True

        return False
