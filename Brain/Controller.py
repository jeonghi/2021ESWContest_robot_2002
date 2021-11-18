from Brain.Robot import Robot
from enum import Enum, auto
from Brain.InDoorMission import InDoorMission
from Brain.OutDoorMission import OutDoorMission
from Brain.RoomMission import RoomMission, GreenRoomMission, BlackRoomMission
from Constant import Direction, AreaColor, LineColor, WalkInfo, debug_mode, const

import time

CLEAR_LIMIT: int = 2
class Mode(Enum):
    START = auto()
    IN = auto()
    DETECT_DIRECTION = auto()
    CHECK_AREA_COLOR = auto()
    ROOM_MISSION = auto()
    GO_TO_NEXT_ROOM = auto()
    OUT = auto()
    END = auto()

class Controller:
    robot: Robot = Robot()
    mode: Mode = Mode.START
    mission_done: int = 0
    fail_count: int = 0
    InDoorMission.set_robot(robot)
    OutDoorMission.set_robot(robot)
    RoomMission.set_robot(robot)

    if debug_mode.IS_ON:
        room = debug_mode.ROOMS[mission_done]
        RoomMission.set_debug(room.name_color, room.room_name, room.area_color)

    robot.set_basic_form()
    ROI = False
    @classmethod
    def set_test_mode(cls, mode: Mode) -> None:
        cls.mode = mode
        if cls.mode == Mode.DETECT_DIRECTION:
            cls.robot._motion.set_head(dir='DOWN', angle=70)
            time.sleep(2)
            cls.ROI = False
            cls.robot.color=LineColor.YELLOW
        elif cls.mode == Mode.CHECK_AREA_COLOR:
            cls.ROI = False
            cls.robot.direction = Direction.LEFT
        elif cls.mode == Mode.GO_TO_NEXT_ROOM:
            cls.robot._motion.set_head("DOWN", 10)
            cls.ROI = True
            cls.robot.color=LineColor.YELLOW
            cls.robot.direction = Direction.RIGHT
        elif cls.mode == Mode.OUT:
            cls.ROI = True
            cls.robot.color=LineColor.YELLOW
            cls.robot.direction = Direction.LEFT
            cls.mission_done = 2


    @classmethod
    def check_go_to_next_room(cls) -> bool:
        if debug_mode.IS_ON:
            room = debug_mode.ROOMS[cls.mission_done]
            RoomMission.set_debug(room.name_color, room.room_name, room.area_color)

        return False if cls.mission_done > CLEAR_LIMIT else True

    @classmethod
    def go_to_next_room(cls) -> bool :
        #print(cls.robot.walk_info)
        if cls.robot.walk_info == WalkInfo.STRAIGHT:
            if cls.robot.line_info["H"]:
                cls.robot._motion.walk('FORWARD', 1, width = False)
            else:
                cls.robot._motion.walk('FORWARD', 1)
        elif cls.robot.walk_info == WalkInfo.V_LEFT:
            cls.robot._motion.walk('LEFT', 1)
        elif cls.robot.walk_info == WalkInfo.V_RIGHT:
            cls.robot._motion.walk('RIGHT', 1)
        elif cls.robot.walk_info == WalkInfo.MODIFY_LEFT:
            cls.robot._motion.turn('LEFT', 1)
        elif cls.robot.walk_info == WalkInfo.MODIFY_RIGHT:
            cls.robot._motion.turn('RIGHT', 1)

        elif cls.robot.walk_info == WalkInfo.CORNER_LEFT:
            if cls.robot.direction == Direction.RIGHT:
                cls.robot._motion.walk('FORWARD', 1)
                print(cls.robot.direction)
                return True
            else:
                if cls.mission_done >= CLEAR_LIMIT:
                    return True
                else:
                    cls.robot._motion.walk('FORWARD', 4)

        elif cls.robot.walk_info == WalkInfo.CORNER_RIGHT:
            if cls.robot.direction == Direction.LEFT:
                cls.robot._motion.walk('FORWARD', 1)
                print(cls.robot.direction)
                return True
            else:
                if cls.mission_done >= CLEAR_LIMIT:
                    return True
                else:
                    cls.robot._motion.walk('FORWARD', 4)

        else: # WalkInfo.BACKWARD, WalkInfo.DIRECTION_LINE
            cls.robot._motion.walk('BACKWARD', 1)
        return False

    @classmethod
    def detect_direction(cls) -> bool:
        if debug_mode.IS_ON:
            direction = debug_mode.DIRECTION
        else:
            direction = cls.robot._image_processor.get_arrow_direction(visualization=False)

        if direction:
            cls.robot.direction = Direction.LEFT if direction == "LEFT" else Direction.RIGHT

            return True

        #cls.robot._motion.walk("BACKWARD", 1)
        time.sleep(1.0)
        return False

    @classmethod
    def room_run(cls):
        cls.robot.color = LineColor.YELLOW
        cls.robot.set_line_and_edge_info(ROI=cls.ROI)
        Mission = GreenRoomMission
        return Mission.run()


    @classmethod
    def run(cls):
        mode = cls.mode
        cls.robot.set_line_and_edge_info(ROI=cls.ROI)
        print(mode.name)
        if mode == Mode.START:
            cls.mode = Mode.IN

        elif mode == Mode.IN:
            if InDoorMission.run():
                cls.mode = Mode.DETECT_DIRECTION
                cls.ROI = False

        elif mode == Mode.DETECT_DIRECTION:
            if cls.fail_count > 1:
                cls.robot.direction = const.DEFAULT_DIRECTION
                cls.robot._motion.set_head(dir='DOWN', angle=10)
                time.sleep(0.5)
                # cls.robot._motion.walk("FORWARD", width=False, loop=1) # 업어야됨 인식 문제로 후진할 때 주석해제
                cls.robot._motion.walk(cls.robot.direction.name, wide=True,
                                       loop=const.DEFAULT_WALK_AFTER_DETECT_DIRECTION)
                cls.robot._motion.turn(cls.robot.direction.name, sliding=True,
                                       loop=const.DEFAULT_TURN_AFTER_DETECT_DIRECTION)
                cls.fail_count = 0
                cls.mode = Mode.GO_TO_NEXT_ROOM
                cls.ROI = True
            elif cls.detect_direction():
                cls.fail_count = 0
                cls.robot._motion.set_head(dir='DOWN', angle=10)
                time.sleep(0.5)
                #cls.robot._motion.walk("FORWARD", width=False, loop=1) # 업어야됨 인식 문제로 후진할 때 주석해제
                cls.robot._motion.walk(cls.robot.direction.name, wide=True, loop=const.DEFAULT_WALK_AFTER_DETECT_DIRECTION)
                cls.robot._motion.turn(cls.robot.direction.name, sliding=True, loop=const.DEFAULT_TURN_AFTER_DETECT_DIRECTION)
                cls.mode = Mode.GO_TO_NEXT_ROOM
                cls.ROI = True
            else:
                cls.fail_count += 1

        elif mode == Mode.GO_TO_NEXT_ROOM:
            if cls.go_to_next_room():
                if cls.mission_done < CLEAR_LIMIT:
                    cls.mode = Mode.CHECK_AREA_COLOR  # 미션
                    print("COLOR MODE: ", cls.mode)
                    cls.ROI = False
                else:
                    cls.mode = Mode.OUT

        elif mode == Mode.CHECK_AREA_COLOR:
            if RoomMission.check_area_color():
                cls.mode = Mode.ROOM_MISSION

        elif mode == Mode.ROOM_MISSION:
            Mission = GreenRoomMission if RoomMission.area_color == AreaColor.GREEN else BlackRoomMission
            if Mission.run():
                cls.mission_done += 1
                Mission.reset()
                print(Mode.ROOM_MISSION.name, cls.mission_done)
                cls.ROI = True
                cls.mode = Mode.GO_TO_NEXT_ROOM
                cls.robot._motion.set_head("DOWN", angle=10)
                time.sleep(0.5)

        elif mode == Mode.OUT:
            cls.robot.color=LineColor.YELLOW
            if OutDoorMission.run():
                return True # 퇴장

        return False
