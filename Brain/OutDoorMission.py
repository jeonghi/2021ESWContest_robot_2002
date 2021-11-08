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
            if cls.robot.line_info['V']:
                if 85 < cls.robot.line_info["DEGREE"] < 95:
                    if 290 < cls.robot.line_info["V_X"][0] < 350:
                        cls.robot._motion.walk(dir='FORWARD', loop=2, open_door = True)
                    else:
                        if cls.robot.line_info["V_X"][0] < 290:
                            cls.robot._motion.walk(dir='LEFT', loop=1, open_door = True)
                        elif cls.robot.line_info["V_X"][0] > 350:
                            cls.robot._motion.walk(dir='RIGHT', loop=1, open_door = True)

                elif 0 < cls.robot.line_info["DEGREE"] <= 85:
                    cls.robot._motion.turn(dir='LEFT', loop=1, open_door = True)

                else:
                    cls.robot._motion.turn(dir='RIGHT', loop=1, open_door = True)

            elif 0 < cls.robot.line_info["DEGREE"] <= 85:
                    cls.robot._motion.turn(dir='LEFT', loop=1, open_door = True)
            else:
                cls.robot._motion.turn(dir='RIGHT', loop=1, open_door = True)
        else:
            return True
                
        return False
    
    @classmethod
    def out_door(cls) -> bool:
        if cls.robot.direction == 'LEFT':
            cls.robot._motion.open_door(dir='LEFT', loop=15)
        else:
            cls.robot._motion.open_door(dir='RIGHT', loop=15)
        
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