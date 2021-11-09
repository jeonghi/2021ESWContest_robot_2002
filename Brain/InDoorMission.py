from Brain.Robot import Robot
from enum import Enum, auto
import time
from Constant import Direction, WalkInfo

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
            cls.robot._motion.walk('FORWARD', loop=8, open_door=True)
        else:
            if cls.robot.walk_info == WalkInfo.STRAIGHT:
                cls.robot._motion.walk('FORWARD', loop=2, open_door=True)
            elif cls.robot.walk_info == WalkInfo.V_LEFT:
                cls.robot._motion.walk('LEFT', loop=1, open_door=True)
            elif cls.robot.walk_info == WalkInfo.V_RIGHT:
                cls.robot._motion.walk('RIGHT', loop=1, open_door=True)
            elif cls.robot.walk_info == WalkInfo.MODIFY_LEFT:
                cls.robot._motion.open_door_turn('LEFT', 1)
            elif cls.robot.walk_info == WalkInfo.MODIFY_RIGHT:
                cls.robot._motion.open_door_turn('RIGHT', 1)
            
            elif cls.robot.walk_info in [ WalkInfo.DIRECTION_LINE, WalkInfo.CORNER_RIGHT, WalkInfo.CORNER_LEFT] :
                cls.robot._motion.basic_form()
                cls.robot._motion.set_head(dir='DOWN', angle=90)
                time.sleep(0.5)
                return True
                    
            else: # WalkInfo.BACKWARD
                cls.robot._motion.open_door_walk('BACKWARD', 1)

        return False

    @classmethod
    def detect_direction(cls) -> bool:
        direction = cls.robot._image_processor.get_arrow_direction()
        if direction:
            cls.robot._motion.set_head(dir='DOWN', angle=10)
            time.sleep(0.5)
        
            cls.robot._motion.walk('FORWARD', 2)
            cls.robot._motion.walk(cls.robot.direction.name, wide=True, loop = 4)
            cls.robot._motion.turn(cls.robot.direction.name, sliding=True, loop = 4)
            
            cls.robot.direction = Direction.LEFT if direction == "LEFT" else Direction.RIGHT
            return True
        
        cls.robot._motion.walk("BACKWARD", 1)
        time.sleep(0.5)
        return False
    
    @classmethod
    def run(cls) -> bool:
        mode = cls.mode
        
        if mode == Mode.START:
            cls.mode = Mode.DETECT_ALPHABET

        elif mode == Mode.DETECT_ALPHABET:
            if cls.detect_alphabet():
                cls.mode = Mode.IN_DOOR
        
        elif mode == Mode.IN_DOOR:
            if cls.in_door():
                cls.mode = Mode.DETECT_DIRECTION
            pass
        
        elif mode == Mode.DETECT_DIRECTION:
            if cls.detect_direction():
                cls.mode = Mode.END
        
        if mode == Mode.END:
            return True
        
        return False