from Sensor.ImageProcessor import ImageProcessor
from Sensor.lines_class import LineDetector
from Actuator.Motion import Motion
import numpy as np
import cv2
import time
import sys

import cv2
import numpy as np


class Robot:

    def __init__(self, video_path =""):
        self._motion = Motion()
        self._image_processor = ImageProcessor(video_path=video_path)

    def detect_alphabet(self):
        alphabet = self._image_processor.get_door_alphabet()
        self._motion.notice_direction(dir=alphabet)
        exit()

    def line_tracing(self):
        src = self._image_processor.get_image(visualization=False)
        src = cv2.resize(src, dsize=(480, 640))
        ans, src = LineDetector.get_all_lines(src)
        # ans list : [0]현재 방향(동작 보정 각도), [1]vertical, [2]vertical-x, [3]horizontal, [4]horizontal-y, [5]horizontal-minx, [6]horizontal-max
        if ans[1] != 'None' and ans[3] == 'None': #직진
            if 80< ans[0]<100: # 각도가 80~100 이도록
                self._motion.walk(dir='FORWARD', loop=1) # 일정 y좌표때 멈추기
        elif ans[1] != 'None' and ans[3] != 'None':
            # ans[5] 수평선의 마지막 x좌표 - 중앙보다 작으면 ㄱ , 중앙보다 크면 T 
            if 200 < ans[4]:
                if ans[5] < 50 and ans[6] < 340:
                    # ㄱ자
                    print('ㄱ자')
                elif ans[5] > 300 and ans[6]>600:
                    # ㄴ자
                    print('ㄴ자')
                else:
                    # T자
                    print('T자')
            else:
                self._motion.walk(dir='FORWARD')
        