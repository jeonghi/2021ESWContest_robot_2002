from Brain.Robot import Robot
from enum import Enum

class DoorMission:

    @classmethod
    def set_robot(cls, robot: Robot):
        cls.robot = robot
    
    @classmethod
    def detect_alphabet(cls) -> bool:
        pass
    
    @classmethod
    def detect_arrow_direction(cls) -> bool:
        pass
    
    @classmethod
    def open_door(cls) -> bool:
        pass
    
    @classmethod
    def run(cls) -> bool:
        return True