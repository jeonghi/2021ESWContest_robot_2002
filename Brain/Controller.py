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
        #self._image_processor = ImageProcessor(video_path="Sensor/src/line_test/return_line.h264")
        self._line_detector = LineDetector()
        self.direction = "LEFT"
        # self.mode = 'start'
        # self.mode = 'end_mission'
        self.cube_grabbed = False
        self.curr_room_color = "GREEN"
        self.count = 0
        self.progress_of_roobot= [None, ]
        self.walk_info = None


    def set_basic_form(self):
        self._motion.basic_form()


    def trace_milk(self, area:str) -> None :
        grabbed_head_moving = [None]
        grabbed_head_moving.append(self._motion.move_arm(grab=True, level=1))
        grabbed_head_moving.append(self._motion.move_arm(grab=True, level=2))
        grabbed_head_moving.append(self._motion.move_arm(grab=True, level=3))
        dq = deque(grabbed_head_moving)
        while(dq[0]):

            pass


    def check_green_area(self) -> None :
        grabbed_head_moving = ["begin",1, 2, 3,"end"]
        flag = 1
        dq = deque(grabbed_head_moving)
        dq.rotate(n=flag)
        while (True):
            if dq[0] == "begin":
                flag = 1
                self._motion.turn(dir="LEFT", grab=True, loop=2)
                time.sleep(1)
            elif dq[0] == "end":
                flag = -1
                self._motion.turn(dir="LEFT", grab=True, loop=2)
                time.sleep(1)
            else:
                self._motion.move_arm(grab=True, level=dq[0])
                time.sleep(1)
            dq.rotate(n=flag)

                



    # def transport_milk_to_green_area(self) -> bool: # if return false, retry trace milk
    #     doing_mission_flag = True
    #     while doing_mission_flag :
    #         self.cube_grabbed = True if self._motion.get_IR() < 100 else False
    #         if self.cube_grabbed :
    #             return False
    #         while self.check_green_area() is False: # 찾았다.
    #             self._motion.turn(dir=self.direction, loop=2, grab=True)
    #         self._motion.move_arm(grab=True, level=3) # 손 위로 번쩍 고개 완전 아래로 들고 전진
    #         while self._image_processor.check_green_area() is False:
    #             self._motion.walk(dir="FORWARD", loop=2, grab=True)
    #         # 내려 놓기







