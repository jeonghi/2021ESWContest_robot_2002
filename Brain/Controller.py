from Sensor.ImageProcessor import ImageProcessor
from Sensor.LineDetector import LineDetector
from Actuator.Motion import Motion
from Sensor.ColorChecker import get_pixel_rate4green
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
        self._line_detector = LineDetector()
        self.mode = None
        self.direction = "RIGHT"

    def detect_alphabet(self):
        self._motion.set_head('DOWN', 75)
        flag = True
        alphabet = None
        while alphabet is None:
            alphabet = self._image_processor.get_door_alphabet()
            
            if alphabet is not None:
                break

            if flag:
                self._motion.walk("RIGHT")
            else:
                self._motion.walk("LEFT")
        
            flag = not flag
        self._motion.notice_direction(dir=alphabet)

    def line_tracing(self):
        self._motion.set_head('DOWN', 30)
        while True:
            src = self._image_processor.get_image(visualization=False)
            src = cv2.resize(src, dsize=(640,480))
            ans, result_img = self._line_detector.get_all_lines(src)
            cv2.imshow('src', result_img)
            cv2.waitKey(1)

            # ans list : [0]현재 방향(동작 보정 각도), [1]vertical, [2]vertical-x, [3]horizontal, [4]horizontal-y, [5]horizontal-minx, [6]horizontal-max

            if ans[1] is not None and ans[3] is None: #직선만 검출
                if 300 < ans[2] <340:
                    print('FORWARD', ans)
                    self._motion.walk(dir='FORWARD', loop=1) # 일정 y좌표때 멈추기
                else:
                    if ans[2] < 300:
                        print('MODIFY walk --LEFT', ans)
                        self._motion.walk(dir='LEFT', loop=1)
                    elif ans[2] > 340:
                        print('MODIFY walk --RIGHT', ans)
                        self._motion.walk(dir='RIGHT', loop=1)

            elif ans[1] is None and ans[3] is None: # 아무 직선도 검출 안됨(수직, 수평선 검출될 때까지 계속 회전)
                if ans[0] < 85:
                    print('MODIFY angle --LEFT', ans)
                    self._motion.turn(dir='LEFT', loop=1)
                elif ans[0] > 95:
                    print('MODIFY angle --RIGHT', ans)
                    self._motion.turn(dir='RIGHT', loop=1)

            else:
            #elif ans[1] is None and ans[3] is not None: # 수평만 검출, ㄱ자랑 T자 앞에 있다는 뜻
                # 가려는 방향으로 두칸 이동 및 회전
                #print('INFRONT OF LINE --go LEFT 2 and trun LEFT', ans)

            #elif ans[1] is not None and ans[3] is not None: # 수직 수평 둘다 검출
                # ans[5] 수평선의 마지막 x좌표 - 중앙보다 작으면 ㄱ , 중앙보다 크면 T 
                if ans[4] > 200: 
                    if ans[5] < 50 and ans[6] < 340:
                        # ㄱ자
                        print('ㄱ자', ans)
                        if self.mode == 'LEFT':
                            print(self.mode, "모드여서 좌회전 안하고 직진합니다.")
                            self._motion.walk(dir='FORWARD', loop=4)
                            #self. count += 1
                        elif self.mode == 'RIGHT':
                            self._motion.turn('LEFT', loop=8)
                        else:
                            print("화살표 인식 전입니다.")

                    elif ans[5] > 300 and ans[6]>600:
                        # ㄴ자
                        print('ㄴ자', ans)
                        if self.mode == 'LEFT':
                            self._motion.turn('RIGHT', loop=8)
                        elif self.mode == 'RIGHT':
                            print(self.mode, "모드여서 우회전 안하고 직진합니다.")
                            self._motion.walk(dir='FORWARD', loop=4)
                            #self. count += 1
                        else:
                            print("화살표 인식 전입니다.")
                        
                    else:
                        # T자 :: 가려는 방향으로 두칸 이동 및 회전
                        print('T자 :: INFRONT OF LINE --go WANT mode 4 and trun WANT mode', ans)
                        self._motion.set_head("DOWN", 100)
                        while self.mode == None:
                            self.mode = self._image_processor.get_arrow_direction()
                            print('MODE::', self.mode)
                            time.sleep(0.1)
                        self._motion.set_head('DOWN', 10)
                        self._motion.walk('FORWARD', 2)
                        self._motion.walk(self.mode, 4)
                        self._motion.turn(self.mode, 8)
                else:
                    self._motion.walk('FORWARD')
                    print(ans[4], 'low then 150')

    def recognize_area_color(self):
        self._motion.set_head(self.direction, 45)
        self._motion.set_head('DOWN', 60)
        time.sleep(1)
        color = self._image_processor.get_area_color()
        self._motion.notice_area(area=color)
        self._motion.set_head("UPDOWN_CENTER")
        self._motion.set_head("LEFTRIGHT_CENTER")
        return
        
