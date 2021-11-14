from Brain.Robot import Robot
from enum import Enum, auto
import time
from Constant import Direction, WalkInfo, debug_mode

class Mode(Enum):
    START = auto()
    DETECT_ALPHABET = auto()
    IN_DOOR = auto()
    DETECT_DIRECTION = auto()
    END = auto()
class InDoorMission:

    mode: Mode = Mode.START
    robot: Robot = Robot

    @classmethod
    def set_robot(cls, robot: Robot):
        cls.robot = robot
    
    @classmethod 
    def detect_alphabet(cls) -> bool:
        cls.robot._motion.set_head(dir="DOWN", angle=cls.robot.curr_head4door_alphabet[0])
        
        if debug_mode.IS_ON:
            alphabet = debug_mode.DOOR_ALPHABET
        else:
            alphabet = cls.robot._image_processor.get_door_alphabet()
        
        if alphabet:
            print("alphabet:", alphabet)
            cls.robot._motion.notice_direction(dir=alphabet)   
            cls.robot._motion.set_head(dir="DOWN", angle=10)
            time.sleep(1)
            return True
        
        cls.robot.curr_head4door_alphabet.rotate(-1)    
        return False

    @classmethod
    def in_door(cls) -> bool:
        dst = cls.robot._motion.get_IR()
        if dst > 100 :
            cls.robot._motion.walk('FORWARD', loop=4, open_door=True, width=False)
        else:
            if cls.robot.walk_info == WalkInfo.STRAIGHT:
                cls.robot._motion.walk('FORWARD', loop=2, open_door=True, width=False)
            elif cls.robot.walk_info == WalkInfo.V_LEFT:
                if cls.robot.line_info['H_Y'][1] <= 100:
                    cls.robot._motion.walk('LEFT', loop=1, open_door=True)
                else:
                    cls.robot._motion.walk('FORWARD', loop=2, open_door=True, width=False)
            elif cls.robot.walk_info == WalkInfo.V_RIGHT:
                if cls.robot.line_info['H_Y'][1] <= 100:
                    cls.robot._motion.walk('RIGHT', loop=1, open_door=True)
                else:
                    cls.robot._motion.walk('FORWARD', loop=2, open_door=True, width=False)
            elif cls.robot.walk_info == WalkInfo.MODIFY_LEFT:
                cls.robot._motion.open_door_turn('LEFT', 1)
            elif cls.robot.walk_info == WalkInfo.MODIFY_RIGHT:
                cls.robot._motion.open_door_turn('RIGHT', 1)
            
            elif cls.robot.walk_info in [ WalkInfo.DIRECTION_LINE, WalkInfo.CORNER_RIGHT, WalkInfo.CORNER_LEFT] :
                cls.robot._motion.basic_form()
                cls.robot._motion.set_head(dir='DOWN', angle=90)
                time.sleep(2)
                return True
                    
            else: # WalkInfo.BACKWARD
                cls.robot._motion.open_door_walk('BACKWARD', 1)

        return False
    
    @classmethod
    def run(cls) -> bool:
        mode = cls.mode
        
        if mode == Mode.START:
            cls.mode = Mode.DETECT_ALPHABET

        elif mode == Mode.DETECT_ALPHABET:
            if cls.detect_alphabet():
                #cls.robot._motion.walk('FORWARD', loop=15, open_door=True)
                cls.robot._motion.walk('FORWARD', loop=7, open_door=True, width=False)
                cls.mode = Mode.IN_DOOR
        
        elif mode == Mode.IN_DOOR:
            if cls.in_door():
                cls.mode = Mode.END

        if mode == Mode.END:
            return True
        
        return False