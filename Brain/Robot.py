from Sensor.ImageProcessor import ImageProcessor
from Sensor.LineDetector import LineDetector
from Actuator.Motion import Motion
from Brain.Constant import LineColor, Direction
import numpy as np
import cv2
import time
import sys
from collections import deque

class Robot:
    def __init__(self, video_path =""):
        self._motion = Motion()
        self._image_processor = ImageProcessor(video_path=video_path)
        self.curr_head4door_alphabet: deque = deque([85, 80])
        self.curr_head4room_alphabet: deque = deque([85, 80])
        self.curr_head4box: deque = deque([75, 60, 35])
        self.curr_head4find_corner: deque = deque([60, 35])
        self.curr_arm_pos: deque = deque(['LOW', 'HIGH'])
        self.color: LineColor = LineColor.YELLOW
        self.line_info: tuple
        self.edge_info: tuple
        self.walk_info : str
        self.direction: Direction

    def set_basic_form(self):
        self._motion.basic_form()
        self.is_grab = False
        self.cube_grabbed = False

    def set_line_and_edge_info(self, line_visualization=True, edge_visualization=False, ROI= False):
        self.line_info, self.edge_info, _ = self._image_processor.line_tracing(color=self.color.name, line_visualization = line_visualization, edge_visualization=edge_visualization, ROI=ROI)
        if self.color == LineColor.YELLOW:
            self.walk_info = self._image_processor.line_checker(self.line_info)