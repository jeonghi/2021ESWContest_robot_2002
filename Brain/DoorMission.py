from Brain.Robot import Robot
from enum import Enum, auto

class Mode(Enum):
    START = auto()
    DETECT_ALPHABET = auto()
    IN = auto()
    DETECT_DIRECTION = auto()
    OUT = auto()
    END = auto()
class DoorMission:

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
            return True
        
        cls.robot.curr_head4door_alphabet.rotate(-1)    
        return False
    
    @classmethod
    def detect_direction(cls) -> bool:
        direction = cls.robot._image_processor.get_arrow_direction()
        if direction:
            cls.robot._motion.set_head(dir='DOWN', angle=10)
            cls.robot.direction = direction
            return True
        
        cls.robot._motion.walk("BACKWARD", 1)
        return False
    
    @classmethod
    def open_door(cls) -> bool:
        pass
    
    @classmethod
    def run(cls) -> bool:
        mode = cls.mode
        
        if mode == Mode.START:
            cls.mode = Mode.DETECT_ALPHABET

        elif mode == Mode.DETECT_ALPHABET:
            if cls.detect_alphabet:
                cls.mode = Mode.IN
        
        elif mode == Mode.IN:
            pass
        
        elif mode == Mode.OUT:
            pass
            

        elif mode == Mode.DETECT_DIRECTION:
            if cls.detect_direction:
                cls.mode = Mode.IN
        
        return False