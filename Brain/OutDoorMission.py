from Brain.Robot import Robot
from enum import Enum, auto
import time
from Constant import Direction
import numpy as np

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
        print(np.mean(cls.robot.line_info['H_Y']))
        if not cls.robot.line_info['H'] or np.mean(cls.robot.line_info['H_Y']) > 155:
            return True
        else:
            cls.robot._motion.walk('FORWARD', 1, width = False)
            return False
    
    @classmethod
    def out_door(cls) -> bool:
        if cls.robot.direction == Direction.LEFT:
            cls.robot._motion.open_door(dir='LEFT', loop=10)
        else:
            cls.robot._motion.open_door(dir='RIGHT', loop=10)

        cls.robot._motion.notice_alpha(cls.robot.black_room)
        
        return True
    
    @classmethod
    def run(cls) -> bool:
        mode = cls.mode
        
        if mode == Mode.START:
            print('out start')
            cls.mode = Mode.OUT_LINE

        elif mode == Mode.OUT_LINE:
            print('out_line')
            if cls.out_line():
                print('out_line:: True')
                cls.mode = Mode.OUT_DOOR
        
        elif mode == Mode.OUT_DOOR:
            if cls.out_door():
                cls.mode = Mode.END
        
        if mode == Mode.END:
            return True
        
        return False