from Brain.Robot import Robot
from enum import Enum, auto
import time

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
    def in_door(cls) -> bool:
        if cls.robot.line_info['V']:
            if 85 < cls.robot.line_info["DEGREE"] < 95:
                if 290 < cls.robot.line_info["V_X"][0] < 350:
                    if cls.robot.line_info["H"]:
                        cls.robot._motion.basic_form()
                        if cls.robot.line_info['H_Y'][1] < 100:
                            cls.robot._motion.walk(dir='FORWARD')
                        return True
                    else:
                        cls.robot._motion.walk(dir='FORWARD', loop=2, open_door = True)  # 팔뻗기
                else:
                    if cls.robot.line_info["V_X"][0] < 290:
                        cls.robot._motion.walk(dir='LEFT', loop=1, open_door = True) # 팔뻗기
                    elif cls.robot.line_info["V_X"][0] > 350:
                        cls.robot._motion.walk(dir='RIGHT', loop=1, open_door = True) # 팔뻗기

            elif 0 < cls.robot.line_info["DEGREE"] <= 85:
                cls.robot._motion.turn(dir='LEFT', loop=1, open_door = True) # 팔뻗기

            else:
                cls.robot._motion.turn(dir='RIGHT', loop=1, open_door = True) # 팔뻗기

        elif 0 < cls.robot.line_info["DEGREE"] <= 85:
                cls.robot._motion.turn(dir='LEFT', loop=1, open_door = True) # 팔뻗기
        else:
            cls.robot._motion.turn(dir='RIGHT', loop=1, open_door = True) # 팔뻗기
        return False
            
    @classmethod
    def out_door(cls) -> bool:
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
            if cls.in_door():
                cls.mode = Mode.DETECT_DIRECTION
            pass
        
        elif mode == Mode.DETECT_DIRECTION:
            if cls.detect_direction:
                cls.mode = Mode.END
        
        elif mode == Mode.OUT:
            pass
        
        if mode == Mode.END:
            return True
        
            

       
        
        return False