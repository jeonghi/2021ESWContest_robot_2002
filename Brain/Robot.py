from Sensor.ImageProcessor import ImageProcessor
from Sensor.LineDetector import LineDetector
from Actuator.Motion import Motion
import numpy as np
import cv2
import time
import sys
from collections import deque

class Robot:    
    def __init__(self, video_path ="", mode="start", DEBUG=False):
        # 모듈들 객체 생성
        self._motion = Motion()
        self._image_processor = ImageProcessor(video_path=video_path)
        self._line_detector = LineDetector()
        self.DEBUG = DEBUG
        # 멤버 변수 셋팅
        self.mode: str = mode
        self.color: str = "YELLOW"
        self.direction: str = ''
        self.alphabet: str = None
        self.alphabet_color: str = None
        self.curr_room_color: str = None
        self.cube_grabbed: bool = False
        self.count: int = 0
        self.progress_of_robot: list = [None]
        self.is_grab: bool = False
        self.walk_info: str = None
        self.curr_head4box: deque = deque([75, 60, 35])
        self.curr_head4room_alphabet: deque = deque([85, 80])
        self.curr_head4door_alphabet: deque = deque([80, 75])
        self.black_room: list = []
        self.return_head: str = "" 
        self.mode_history: str = self.mode
        self.box_pos: str = ""
        self.out_map: int = 0