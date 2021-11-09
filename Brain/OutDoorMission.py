from Brain.Robot import Robot
from enum import Enum, auto
import time

class Mode(Enum):
    START = auto()
    OUT_LINE = auto()
    OUT_DOOR = auto()
    END = auto()
    
class OutDoorMission:

    mode: Mode = Mode.START
    robot: Robot = Robot

    @classmethod
    def set_robot(cls, robot: Robot):
        cls.robot = robot
    
    @classmethod
    def out_line(cls) -> bool:
        if cls.robot.line_info['H']:
            cls.robot._motion.walk('FORWARD', 1)
            return False
        else:
            return True
    
    @classmethod
    def out_door(cls) -> bool:
        if cls.robot.direction == 'LEFT':
            cls.robot._motion.open_door(dir='LEFT', loop=15)
        else:
            cls.robot._motion.open_door(dir='RIGHT', loop=15)

        cls.robot._motion.notice_alpha(cls.robot.black_room)
        # 정환 self.blackroom True일때 notice 해주는 구문 작성해주세여
        
        return True
    
    @classmethod
    def run(cls) -> bool:
        mode = cls.mode
        
        if mode == Mode.START:
            cls.mode = Mode.OUT_LINE

        elif mode == Mode.OUT_LINE:
            if cls.out_line:
                cls.mode = Mode.OUT_DOOR
        
        elif mode == Mode.OUT_DOOR:
            if cls.out_door:
                cls.mode = Mode.END
        
        if mode == Mode.END:
            return True
        
        return False