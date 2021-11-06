from Sensor.ImageProcessor import ImageProcessor
from Sensor.LineDetector import LineDetector
from Actuator.Motion import Motion
import numpy as np
import cv2
import time
import sys
from collections import deque

class Robot:    
    def __init__(self, video_path =""):
        self._motion = Motion()
        self._image_processor = ImageProcessor(video_path=video_path)

    def set_basic_form(self):
        self._motion.basic_form()
        self.is_grab = False
        self.cube_grabbed = False
    
    def line_tracing(self, line_visualization=False, edge_visualization=False, ROI= False):
        line_info, edge_info = self._image_processor.line_tracing(color=self.color, line_visualization = line_visualization, edge_visualization=edge_visualization, ROI=ROI)
        return line_info, edge_info


    def walk(self):
        pass