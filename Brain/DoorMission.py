from Brain.Controller import Controller
from enum import Enum

robot = Controller.robot
class DoorMission:
    
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