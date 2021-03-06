from Sensor.ImageProcessor import ImageProcessor
from Actuator.Motion import Motion
from Constant import LineColor, Direction, WalkInfo
from collections import deque

class Robot:
    def __init__(self, video_path =""):
        self._motion = Motion()
        self._image_processor = ImageProcessor(video_path=video_path)
        self.curr_head4door_alphabet = deque([80, 75])
        self.curr_head4room_alphabet: deque
        self.curr_head4box: deque
        self.curr_head4find_corner: deque
        self.color: LineColor = LineColor.YELLOW
        self.black_room: list = list()
        self.line_info: dict
        self.edge_info: dict
        self.walk_info: WalkInfo
        self.direction: Direction


    def set_basic_form(self):
        self._motion.basic_form()
        self.is_grab = False
        self.cube_grabbed = False


    def set_line_and_edge_info(self, line_visualization=False, edge_visualization=False, ROI= False):
        self.line_info, self.edge_info, _ = self._image_processor.line_tracing(color=self.color.name, line_visualization = line_visualization, edge_visualization=edge_visualization, ROI=ROI)
        if self.color == LineColor.YELLOW:
            self.walk_info = self._image_processor.line_checker(self.line_info)