from Sensor.ImageProcessor import ImageProcessor
from Sensor.LineDetector import LineDetector
from Actuator.Motion import Motion
from Sensor.ColorChecker import get_pixel_rate4green
import numpy as np
import cv2
import time
import sys

class Robot:

    def __init__(self, video_path =""):
        self._motion = Motion()
        self._image_processor = ImageProcessor(video_path=video_path)
        self._line_detector = LineDetector()
        self.direction = None
        self.curr_room_color = "GREEN"

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
        self._motion.set_head('DOWN', 45)
        while True:
            src = self._image_processor.get_image(visualization=False)
            src = cv2.resize(src, dsize=(640,480))
            line_info, result_img = self._line_detector.get_all_lines(src)
            cv2.imshow('src', result_img)
            cv2.waitKey(1)
            
            if line_info["V"] and not line_info["H"]:
                if 300 < line_info["VPOS"] <340:
                    print('FORWARD', line_info)
                    self._motion.walk(dir='FORWARD', loop=1)
                else:
                    if line_info["VPOS"] < 300:
                        print('MODIFY walk --LEFT', line_info)
                        self._motion.walk(dir='LEFT', loop=1)
                    elif line_info["VPOS"] > 340:
                        print('MODIFY walk --RIGHT', line_info)
                        self._motion.walk(dir='RIGHT', loop=1)

            elif not line_info["V"] and not line_info["H"]:
                if line_info["DEGREE"] < 85:
                    print('MODIFY angle --LEFT', line_info)
                    self._motion.turn(dir='LEFT', loop=1)
                elif line_info["DEGREE"] > 95:
                    print('MODIFY angle --RIGHT', line_info)
                    self._motion.turn(dir='RIGHT', loop=1)


            else:
                if line_info["HPOS"] > 200: 
                    if line_info["H_MIN_X"] < 50 and line_info["H_MAX_X"] < 340:
                        print('┒', line_info)
                        if self.direction == 'LEFT':
                            print(self.direction, "모드여서 좌회전 안하고 직진합니다.")
                            self._motion.walk(dir='FORWARD', loop=4)
                            #self.count += 1
                        elif self.direction == 'RIGHT':
                            self._motion.turn('LEFT', loop=8)
                        else:
                            print("화살표 인식 전입니다.")

                    elif line_info["H_MIN_X"] > 300 and line_info["H_MAX_X"]>600:
                        print('┎', line_info)
                        if self.direction == 'LEFT':
                            self._motion.turn('RIGHT', loop=8)
                        elif self.direction == 'RIGHT':
                            print(self.direction, "모드여서 우회전 안하고 직진합니다.")
                            self._motion.walk(dir='FORWARD', loop=4)
                            #self.count += 1
                        else:
                            print("화살표 인식 전입니다.")
                        
                    else:
                        print('T', line_info)
                        self._motion.set_head("DOWN", 100)
                        self.direction = self._image_processor.get_arrow_direction()
                        print('MODE::', self.direction)
                        time.sleep(0.1)
                        while self.direction == None:
                            self._motion.walk("BACKWARD", 1)
                            self.direction = self._image_processor.get_arrow_direction()
                            print('MODE::', self.direction)
                            time.sleep(0.1)
                        self._motion.set_head('DOWN', 10)
                        self._motion.walk('FORWARD', 2)
                        self._motion.walk(self.direction, 4)
                        self._motion.turn(self.direction, 8)
                else:
                    self._motion.walk('FORWARD')
                    print('low then 150')

    def recognize_area_color(self):
        self._motion.set_head(self.direction, 45)
        self._motion.set_head('DOWN', 60)
        time.sleep(1)
        color = self._image_processor.get_area_color()
        self._motion.notice_area(area=color)
        self._motion.set_head("UPDOWN_CENTER")
        self._motion.set_head("LEFTRIGHT_CENTER")
        return

    def turn_to_yellow_line_corner(self, turn):
        baseline = (bx, by) = (320, 420)
        r = self._motion.set_head("DOWN", 60)
        if self.curr_room_color is "GREEN" : # 안전 지역에서 빠져 나간다면 물건을 집지 않고 그냥 회전
            self._motion.turn(dir=turn, loop=3)
            flag = True
            while True:
                corner_pos = self._image_processor.get_yellow_line_corner_pos()
                if corner_pos:
                    (cx, cy) = corner_pos
                    if bx - 50 <= cx <= bx + 50: # 적정범위 이내이면 물건 들고 전진, 리턴
                        print("코너가 적정 범위에 들어왔습니다. 코너로 전진합니다")
                        self._motion.walk(dir="FORWARD")
                        cv2.destroyAllWindows()
                        return
                    elif bx-80 <= cx < bx-50: # 적정범위밖 왼쪽으로 치우쳐있다면요
                        print("코너가 범위에서 왼쪽으로 벗어났습니다. 오른쪽으로 ")
                        self._motion.turn(dir="RIGHT")
                    elif bx+50 < cx <= bx+80: # 적정범위밖 오른쪽으로 치우쳐있다면
                        print("코너가 범위에서 오쪽으로 벗어났습니다. 왼쪽으로 턴")
                        self._motion.turn(dir="LEFT")
                    else:
                        print("걍 범위에 들지도 않아 지정 방향으로 턴")
                        self._motion.turn(dir=turn)
                else:
                    if flag:
                        self._motion.set_head("DOWN", 30)
                    else:
                        self._motion.set_head("DOWN", 60)
                    flag = not flag
                    print("코너가 검출되지 않았습니다 지정 방향으로 턴")
                    self._motion.turn(dir=turn)
        
