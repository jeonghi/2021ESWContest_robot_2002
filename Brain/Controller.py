from Sensor.ImageProcessor import ImageProcessor
from Sensor.LineDetector import LineDetector
from Actuator.Motion import Motion
import numpy as np
import cv2
import time
import sys
from collections import deque

class Robot:

    def __init__(self, video_path ="", DEBUG = False):
        self._motion = Motion(DEBUG)
        self._image_processor = ImageProcessor(video_path=video_path)
        #self._image_processor = ImageProcessor(video_path="Sensor/src/line_test/return_line.h264")
        self._line_detector = LineDetector()
        self.direction = None
        # self.mode = 'start'
        self.mode = 'end_mission'
        self.cube_grabbed = False
        self.cur_room_color = "GREEN"
        self.saferoom_pos = "LEFT"
        self.count = 0
        self.progress_of_roobot= [None, ]
        self.walk_info = None

    def set_basic_form(self):
        self._motion.basic_form()

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

    def tracking_cube(self):
        def head_down(state):
            if state == "UPDOWN_CENTER":
                return 60
            elif state == 60:
                return 45
            elif state == 45:
                return 30
            elif state == 30:
                return 20
            else:
                return state

        def head_up(state):
            if state == 20:
                return 30
            elif state == 30:
                return 45
            elif state == 45:
                return 60
            elif state == 60:
                return "UPDOWN_CENTER"
            else:
                return state

        v_angle, _ = self._motion.get_head()
        cube_center_x, cube_center_y = self._image_processor.get_cube_saferoom()

        src = self._image_processor.get_image(visualization=False)
        h, w = src.shape[:2]

        frame_center_x = w / 2
        frame_center_y = h / 2

        if not self.cube_grabbed:
            if v_angle == 20:
                #v_angle = 60
                self._motion.grab()
                self.cube_grabbed = True

            if abs(frame_center_x - cube_center_x) < 20:
                self._motion.walk('FORWARD')

                if cube_center_y > (frame_center_y + 20):
                    print("cube below center!")
                    print("v_angle: ", v_angle)

                    v_angle = head_down(v_angle)
                    self._motion.set_head("DOWN", v_angle)

            elif cube_center_x < 300:
                self._motion.walk('LEFT')
            elif cube_center_x > 340:
                self._motion.walk('RIGHT')
        else:
            print("GRABED!!!")
            h_degree = self._image_processor.get_saferoom_position()
            if self.saferoom_pos == "LEFT":
                v_angle = 60
                self._motion.set_head("DOWN", v_angle)
                #self._motion.walk('BACKWARD', loop=2, grab=True)
                self._motion.turn('LEFT', loop=15, grab=True)
                self.saferoom_pos = ""

            if h_degree is None:
                return

            if h_degree < 0:
                print("turn LEFT")
                #self._motion.turn('LEFT', grab=True)
            elif h_degree > 0:
                print("turn RIGHT")
                #self._motion.turn('RIGHT', grab=True)

            if np.abs(h_degree) > 175:
                print("HEAD DOWN")
                #self._motion.set_head("DOWN", 10)

    def line_tracing(self):
        line_info,edge_info, result =  self._image_processor.line_tracing()
        cv2.imshow('result', result)
        cv2.waitKey(1)
        #print(line_info)
        #print(edge_info)
        return line_info, edge_info

    def detect_direction(self):
        self.detect_alphabet()
        self.mode = 'walk'

    def walk(self, line_info):
        # line_info = {"DEGREE" : 0, "V" : False, "V_X" : [0 ,0], "V_Y" : [0 ,0], "H" : False, "H_X" : [0 ,0], "H_Y" : [0 ,0]}
        if self.walk_info == '│':
            if 300 < line_info["V_X"][0] <340:
                print('│', line_info)
                self._motion.walk(dir='FORWARD', loop=1)
            else:
                if line_info["V_X"][0] < 300:
                    print('← ←', line_info)
                    self._motion.walk(dir='LEFT', loop=1)
                elif line_info["V_X"][0] > 340:
                    print('→ →', line_info)
                    self._motion.walk(dir='RIGHT', loop=1)

        elif self.walk_info == '─':
            self._motion.walk(dir='BACK', loop=2)
            if self.progress_of_roobot[2] == 'detect_direction':
                self.mode = 'detect_direction: fail'
            else:
                self.mode = 'walk'

        elif self.walk_info == None: # 'modify_angle'
            if line_info["DEGREE"] < 85:
                print('MODIFY angle --LEFT', line_info)
                self._motion.turn(dir='LEFT', loop=1)
            elif line_info["DEGREE"] > 95:
                print('MODIFY angle --RIGHT', line_info)
                self._motion.turn(dir='RIGHT', loop=1)

        else:
            print("self.walk_info is blank, Please check line_info")

    def find_edge(self):
        self._motion.set_head('DOWN', 60)
        self._motion.turn(dir='LEFT', loop=2)

    def return_line(self):
        self._motion.walk(dir='FOWARD', loop=2)

    def find_V(self):
        self._motion.turn(self.direction, 1)

    def setting_mode(self):
        line_info, edge_info = self.line_tracing()
        # line_info = {"DEGREE" : 0, "V" : False, "V_X" : [0 ,0], "V_Y" : [0 ,0], "H" : False, "H_X" : [0 ,0], "H_Y" : [0 ,0]}
        # edge_info ={"EDGE_POS": None,"EDGE_L": False, "L_X" : [0 ,0], "L_Y" : [0 ,0],"EDGE_R": False, "R_X" : [0 ,0], "R_Y" : [0 ,0]}

        # 방위 인식
        if self.mode == 'start' :
            self.mode = 'detect_direction' # --> walk
            if self.progress_of_roobot[0] != self.mode:
                self.progress_of_roobot.insert(0, self.mode)

        if self.mode == 'detect_direction' or self.mode == 'detect_direction: fail':
            if self.direction != None:
                self.detect_direction()
                self.mode = 'detect_direction'
            else:
                self.mode = 'walk'

        # 걷기 # 보정 추가로 넣기
        elif self.mode == 'walk' and self.walk_info != '┐' and self.walk_info != '┌' :
            if line_info["V"]==True and line_info["H"]==False:
                self.walk_info = '│'
                self.walk(line_info, self.walk_info)
                if self.progress_of_roobot[0] != self.walk_info:
                    self.progress_of_roobot.insert(0, self.walk_info)
            elif line_info["V"]==True and line_info["H"]==True:
                if line_info["V_X"][0] < 20 and line_info["V_X"][1] < 360 :
                    self.walk_info = '┐'
                    if self.progress_of_roobot[0] != self.walk_info:
                        self.progress_of_roobot.insert(0, self.walk_info)
                elif line_info["V_X"][0] > 280 and line_info["V_X"][1] > 600 :
                    self.walk_info = '┌'
                    if self.progress_of_roobot[0] != self.walk_info:
                        self.progress_of_roobot.insert(0, self.walk_info)
                else :
                    self.walk_info = 'T'
                    if self.progress_of_roobot[0] != self.walk_info:
                        self.progress_of_roobot.insert(0, self.walk_info)
            elif line_info["V"]==False and line_info["H"]==True:
                self.walk_info = '─'
                self.walk(line_info, self.walk_info)
                if self.progress_of_roobot[0] != self.walk_info:
                    self.progress_of_roobot.insert(0, self.walk_info)
            else:
                self.walk_info = None # 'modify_angle'
                self.walk(line_info, self.walk_info)

        # 미션 진입 판별
        elif self.mode == 'walk' and self.walk_info == '┐':
            if self.direction == 'RIGHT':
                self.mode = 'start_mission' # --> end_mission --> return_line
                if self.progress_of_roobot[0] != self.mode:
                    self.progress_of_roobot.insert(0, self.mode)

            elif self.direction == 'LEFT':
                self.mode = 'is_finish_line' # --> walk / finish
                if self.progress_of_roobot[0] != self.mode:
                    self.progress_of_roobot.insert(0, self.mode)
            else:
                print('The Robot has not direction, Please Set **self.direction**')

        elif self.mode == 'walk' and self.walk_info =='┌':
            if self.direction == 'LEFT':
                self.mode = 'start_mission' # --> end_mission
                if self.progress_of_roobot[0] != self.mode:
                    self.progress_of_roobot.insert(0, self.mode)
            elif self.direction == 'RIGHT':
                self.mode = 'is_finish_line' # --> finish
                if self.progress_of_roobot[0] != self.mode:
                    self.progress_of_roobot.insert(0, self.mode)
            else:
                print('The Robot has not direction, Please Set **self.direction**')

        # elif self.mode == 'start_mission':

        # 미션 끝나면? - self.mode == 'end_mission'

        # 방탈출
        elif self.mode == 'end_mission' or self.mode == 'find_edge':
            if edge_info["EDGE_POS"] != None :
                if 300 < edge_info["EDGE_POS"][0] < 360 :
                    self.mode == 'return_line' # --> find_V
                    if self.progress_of_roobot[0] != self.mode:
                        self.progress_of_roobot.insert(0, self.mode)
            else:
                self.mode = 'find_edge' # --> return_line
                self.find_edge()
                if self.progress_of_roobot[0] != self.mode:
                    self.progress_of_roobot.insert(0, self.mode)

        elif self.mode == 'return_line':
            if edge_info["EDGE_POS"][1] > 465:
                self.mode = 'find_V' # --> walk
                if self.progress_of_roobot[0] != self.mode:
                    self.progress_of_roobot.insert(0, self.mode)
            else:
                self.mode = 'return_line' # --> find_V
                self.return_line()
                if self.progress_of_roobot[0] != self.mode:
                    self.progress_of_roobot.insert(0, self.mode)

        elif self.mode == 'find_V':
            self._motion.turn(self.direction, 1)
            if line_info["V"] == True :
                self.mode = 'walk'
            else:
                self.mode = 'find_V'
                self.find_V()

        # 나가기
        elif self.mode == 'is_finish_line':
            if self.count < 3:
                self._motion.walk(dir='FORWARD', loop=8)
                self.mode = 'walk'
            else:
                self.mode = 'finish' # --> stop!
                if self.progress_of_roobot[0] != self.mode:
                        self.progress_of_roobot.insert(0, self.mode)
            self.count += 1



    def setting_mode_test(self):
        line_info, edge_info = self.line_tracing()
        # line_info = {"DEGREE" : 0, "V" : False, "V_X" : [0 ,0], "V_Y" : [0 ,0], "H" : False, "H_X" : [0 ,0], "H_Y" : [0 ,0]}
        # edge_info ={"EDGE_POS": None,"EDGE_L": False, "L_X" : [0 ,0], "L_Y" : [0 ,0],"EDGE_R": False, "R_X" : [0 ,0], "R_Y" : [0 ,0]}

        # 방위 인식
        if self.mode == 'start' :
            self.mode = 'detect_direction' # --> walk
            if self.progress_of_roobot[0] != self.mode:
                print(self.mode)
                self.progress_of_roobot.insert(0, self.mode)

        if self.mode == 'detect_direction' or self.mode == 'detect_direction: fail':
            if self.direction != None:
                #self.detect_direction()
                self.mode = 'detect_direction'
            else:
                self.mode = 'walk'

        # 걷기 # 보정 추가로 넣기
        elif self.mode == 'walk' and self.walk_info != '┐' and self.walk_info != '┌' :
            if line_info["V"]==True and line_info["H"]==False:
                self.walk_info = '│'
                # self.walk(line_info, self.walk_info)
                if self.progress_of_roobot[0] != self.walk_info:
                    print(self.walk_info)
                    self.progress_of_roobot.insert(0, self.walk_info)
            elif line_info["V"]==True and line_info["H"]==True:
                if line_info["V_X"][0] < 20 and line_info["V_X"][1] < 360 :
                    self.walk_info = '┐'
                    if self.progress_of_roobot[0] != self.walk_info:
                        print(self.walk_info)
                        self.progress_of_roobot.insert(0, self.walk_info)
                elif line_info["V_X"][0] > 280 and line_info["V_X"][1] > 600 :
                    self.walk_info = '┌'
                    if self.progress_of_roobot[0] != self.walk_info:
                        self.progress_of_roobot.insert(0, self.walk_info)
                else :
                    self.walk_info = 'T'
                    if self.progress_of_roobot[0] != self.walk_info:
                        print(self.walk_info)
                        self.progress_of_roobot.insert(0, self.walk_info)
            elif line_info["V"]==False and line_info["H"]==True:
                self.walk_info = '─'
                # self.walk(line_info, self.walk_info)
                if self.progress_of_roobot[0] != self.walk_info:
                    print(self.walk_info)
                    self.progress_of_roobot.insert(0, self.walk_info)
            else:
                print(self.walk_info)
                self.walk_info = None # 'modify_angle'
                # self.walk(line_info, self.walk_info)

        # 미션 진입 판별
        elif self.mode == 'walk' and self.walk_info == '┐':
            if self.direction == 'RIGHT':
                self.mode = 'start_mission' # --> end_mission --> return_line
                if self.progress_of_roobot[0] != self.mode:
                    print(self.mode)
                    self.progress_of_roobot.insert(0, self.mode)

            elif self.direction == 'LEFT':
                self.mode = 'is_finish_line' # --> walk / finish
                if self.progress_of_roobot[0] != self.mode:
                    print(self.mode)
                    self.progress_of_roobot.insert(0, self.mode)
            else:
                print('The Robot has not direction, Please Set **self.direction**')

        elif self.mode == 'walk' and self.walk_info =='┌':
            if self.direction == 'LEFT':
                self.mode = 'start_mission' # --> end_mission
                if self.progress_of_roobot[0] != self.mode:
                    print(self.mode)
                    self.progress_of_roobot.insert(0, self.mode)
            elif self.direction == 'RIGHT':
                self.mode = 'is_finish_line' # --> finish
                if self.progress_of_roobot[0] != self.mode:
                    print(self.mode)
                    self.progress_of_roobot.insert(0, self.mode)
            else:
                print('The Robot has not direction, Please Set **self.direction**')

        # elif self.mode == 'start_mission':

        # 미션 끝나면? - self.mode == 'end_mission'

        # 방탈출
        elif self.mode == 'end_mission' or self.mode == 'find_edge':
            if edge_info["EDGE_POS"] != None :
                if 300 < edge_info["EDGE_POS"][0] < 360 :
                    self.mode == 'return_line' # --> find_V
                    if self.progress_of_roobot[0] != self.mode:
                        print(self.mode)
                        self.progress_of_roobot.insert(0, self.mode)
                else:
                    print(edge_info["EDGE_POS"])
                    self.mode='find_edge'
                    print(self.mode)
            else:
                self.mode = 'find_edge' # --> return_line
                #self.find_edge()
                if self.progress_of_roobot[0] != self.mode:
                    print(self.mode)
                    self.progress_of_roobot.insert(0, self.mode)

        elif self.mode == 'return_line':
            if edge_info["EDGE_POS"][1] > 465:
                self.mode = 'find_V' # --> walk
                if self.progress_of_roobot[0] != self.mode:
                    print(self.mode)
                    self.progress_of_roobot.insert(0, self.mode)
            else:
                self.mode = 'return_line' # --> find_V
                #self.return_line()
                if self.progress_of_roobot[0] != self.mode:
                    print(self.mode)
                    self.progress_of_roobot.insert(0, self.mode)

        elif self.mode == 'find_V':
            #self._motion.turn(self.direction, 1)
            if line_info["V"] == True :
                self.mode = 'walk'
                if self.progress_of_roobot[0] != self.mode:
                    print(self.mode)
                    self.progress_of_roobot.insert(0, self.mode)
            else:
                self.mode = 'find_V'
                #self.find_V()

        # 나가기
        elif self.mode == 'is_finish_line':
            if self.count < 3:
                #self._motion.walk(dir='FORWARD', loop=8)
                self.mode = 'walk'
                if self.progress_of_roobot[0] != self.mode:
                    print(self.mode)
                    self.progress_of_roobot.insert(0, self.mode)
            else:
                self.mode = 'finish' # --> stop!
                if self.progress_of_roobot[0] != self.mode:
                    print(self.mode)
                    self.progress_of_roobot.insert(0, self.mode)
            self.count += 1

    def find_yellow_corner_for_out_room(self) -> None:
        grabbed_head_moving = ["begin", "HIGH", "LOW", "MIDDLE", "end"]
        flag = -1
        dq = deque(grabbed_head_moving)
        dq.rotate(flag)
        while True:
            src = self._image_processor.get_image()
            print(result)
            if dq[0] == "begin":
                flag = -1
                self._motion.turn(dir="LEFT", grab=True, loop=2)
                time.sleep(1)
            elif dq[0] == "end":
                flag = 1
                self._motion.turn(dir="LEFT", grab=True, loop=2)
                time.sleep(1)
            else:
                self._motion.move_arm(dir=dq[0])
                time.sleep(1)
            dq.rotate(flag)
