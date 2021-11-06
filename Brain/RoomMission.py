from Brain.Controller import Controller
from enum import Enum, auto

robot = Controller.robot
class Mode(Enum):
    START = auto()
    DETECT_ALPHABET = auto()
    FIND_BOX = auto()
    TRACK_BOX = auto()
    TURN_TO_AREA = auto()
    GO_TO_AREA = auto()
    FIND_CONRER = auto()
    GO_TO_CORNER = auto()
    END = auto()
class RoomMission:

    mode: Mode = Mode.START
    
    line_info = {}
    edge_info = {}
    
    @classmethod
    def detect_alphabet(cls) -> bool:
        alphabet_info = robot._image_processor.get_alphabet_info4room(edge_info=cls.edge_info)
        if alphabet_info:
            robot.alphabet_color, robot.alphabet = alphabet_info
            return True
        
        return False
    
    @classmethod
    def find_box(cls) -> bool:
        pass
    
    @classmethod
    def track_box() -> bool:
        pass
    
    @classmethod
    def turn_to_area() -> bool:
        pass
    
    @classmethod
    def go_to_area() -> bool:
        pass
    
    @classmethod
    def find_corner() -> bool:
        pass
    
    @classmethod
    def go_to_corner() -> bool:
        pass
    
    @classmethod
    def run():
        pass
        

class GreenRoomMission(RoomMission):

    @classmethod
    def turn_to_area(cls) -> bool:
        cls.turn_to_area()

    @classmethod
    def go_to_corner(cls):
        cls.go_to_corner()

    @classmethod
    def run(cls):
        mode = cls.mode
        if mode == Mode.START:
            pass
        elif mode == Mode.DETECT_ALPHABET:
            pass
        elif mode == Mode.FIND_BOX :
            pass
        elif mode == Mode.TRACK_BOX :
            pass
        elif mode == Mode.TURN_TO_AREA:
            pass
        elif mode == Mode.GO_TO_AREA:
            pass
        elif mode == Mode.FIND_CONRER:
            pass
        elif mode == Mode.GO_TO_CORNER:
            pass
        elif mode == Mode.END:
            return True
        
        return False

class BlackRoomMission(RoomMission):
    
    @classmethod
    def detect_alphabet(cls) -> bool:
        cls.detect_alphabet()
        
    @classmethod
    def turn_to_area(cls) -> bool:
        cls.turn_to_area()

    @classmethod
    def go_to_area(cls) -> bool:
        cls.go_to_area()

    @classmethod
    def find_corner(cls) -> bool:
        cls.find_corner()

    @classmethod
    def go_to_corner(cls):
        cls.go_to_corner()
    
    @classmethod
    def run(cls):
        mode = cls.mode
        
        if mode == Mode.START:
            cls.mode = Mode.DETECT_ALPHABET
            
        elif mode == Mode.DETECT_ALPHABET:
             if cls.detect_alphabet():
                cls.mode = Mode.TURN_TO_AREA
                
        elif mode == Mode.TURN_TO_AREA:
            if cls.turn_to_area():
                cls.mode = Mode.GO_TO_AREA
                
        elif mode == Mode.GO_TO_AREA:
            if cls.go_to_area():
                cls.mode = Mode.FIND_BOX
                
        elif mode == Mode.FIND_BOX:
            if cls.find_box():
                cls.mode = Mode.TRACK_BOX
                
        elif mode == Mode.TRACK_BOX:
            if cls.track_box():
                cls.mode = Mode.FIND_CONRER
        
        elif mode == Mode.FIND_CONRER:
            if cls.find_corner():
                cls.mode = Mode.GO_TO_CORNER
                
        elif mode == Mode.GO_TO_CORNER:
            if cls.go_to_corner():
                cls.mode = Mode.END
                
        elif mode == Mode.END:
            return True
        
        return False