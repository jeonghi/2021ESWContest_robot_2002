from Sensor.ImageProcessor import ImageProcessor
from Sensor.LineDetector import LineDetector
from Actuator.Motion import Motion
import numpy as np
import cv2
import time
import sys

class Robot:

    def __init__(self, video_path =""):
        self._motion = Motion()
        self._image_processor = ImageProcessor(video_path=video_path)
        #self._image_processor = ImageProcessor(video_path="Sensor/src/line_test/case2.h264")
        self._line_detector = LineDetector()
        self.direction = 'LEFT'
        # self.mode = 'start'
        self.mode = 'end_mission'
        self.color = 'YELLOW'
        self.box_pos = 'RIGHT'
        self.alphabet_color = 'RED'
        self.cube_grabbed = False
        self.curr_room_color = "GREEN"
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
        if not self.cube_grabbed:
            self._motion.set_head(dir='DOWN', angle=60)
        else:
            self._motion.set_head("UPDOWN_CENTER")

        src = self._image_processor.get_image(visualization=False)
        h, w = src.shape[:2]
        frame_center_x = w / 2
        frame_center_y = h / 2

        cube_center_x, cube_center_y = self._image_processor.get_cube_saferoom()
        saferoom_pos_x, saferoom_pos_y = self._image_processor.get_saferoom_position()

        is_cube_found = True
        if cube_center_x is None:
            is_cube_found = False

        is_saferoom_found = True
        if saferoom_pos_x is None:
            is_saferoom_found = False

        #cur_ir = self._motion.get_IR()
        #print('cur IR:: ', cur_ir)

        #cube_grabbed = False if cur_ir < 100 else True

        if self.cube_grabbed:
            if not is_saferoom_found:
                self._motion.turn('LEFT', grab=True)
                print("saferoom not found")
            else:
                if abs(frame_center_x - saferoom_pos_x) < 20 and (frame_center_y - saferoom_pos_y) > 20:
                    self._motion.walk('FORWARD', grab=True)
                elif abs(frame_center_x - saferoom_pos_x) < 20 and saferoom_pos_y > 440:
                    self._motion.grab(switch=False)
                elif saferoom_pos_x < 300:
                    self._motion.turn('LEFT', grab=True)
                    print("saferoom found left")
                elif saferoom_pos_x > 340:
                    self._motion.turn('RIGHT', grab=True)
                    print("saferoom found right")
        else:
            if abs(frame_center_x - cube_center_x) < 20:
                self._motion.walk('FORWARD')
            elif cube_center_x > 300:
                self._motion.walk('RIGHT')
            elif cube_center_x < 340:
                self._motion.walk('LEFT')
            if abs(frame_center_x - cube_center_x) < 20 and cube_center_y > 440:
                self._motion.grab()
                self.cube_grabbed = True

    def line_tracing(self):
        line_info, edge_info, result =  self._image_processor.line_tracing(self.color)
        cv2.imshow('result', result)
        cv2.waitKey(1)
        #print(line_info)
        #print(edge_info)
        return line_info, edge_info
        

    def detect_direction(self):
        self.direction = self._image_processor.get_arrow_direction()
        if self.direction == None :
            self.mode = 'detect_direction: fail'
        else:
            self.mode = 'detect_direction: success'
            print(self.direction)

    def walk(self, line_info):
        # line_info = {"DEGREE" : 0, "V" : False, "V_X" : [0 ,0], "V_Y" : [0 ,0], "H" : False, "H_X" : [0 ,0], "H_Y" : [0 ,0]}   
        if self.walk_info == '│':
            if 300 < line_info["V_X"][0] <340:
                print('│', line_info)
                self._motion.walk(dir='FORWARD', loop=1)
            else:
                if line_info["V_X"][0] < 300:
                    print('← ←', line_info["V_X"][0])
                    self._motion.walk(dir='LEFT', loop=1)
                elif line_info["V_X"][0] > 340:
                    print('→ →', line_info["V_X"][0])
                    self._motion.walk(dir='RIGHT', loop=1)

        elif self.walk_info == None: # 'modify_angle'
            if line_info["DEGREE"] < 85:
                print('MODIFY angle --LEFT', line_info)
                self._motion.turn(dir='LEFT', loop=1)
            elif line_info["DEGREE"] > 95:
                print('MODIFY angle --RIGHT', line_info)
                self._motion.turn(dir='RIGHT', loop=1)

        else:
            print('walk_info is not │ or None ------------>', self.walk_info)    


    def find_edge(self): #find_corner_for_outroom
        # self.box_pos 반대로 돌면서 yellow edge 찾기
        if self.box_pos == 'RIGHT':
            self._motion.turn(dir='LEFT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
            time.sleep(1)
        if self.box_pos == 'LEFT':
            self._motion.turn(dir='RIGHT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
            time.sleep(1)

    def return_line(self): # 안씀
        self._motion.walk(dir='FOWARD', loop=2)


    def find_V(self): # 안씀
        self._motion.turn(self.direction, 1)


    # start > detect_alphabet> walk │ > ─ > detect_direction > walk │ > ┐ , ┌  > start_mission > end_mission > find_edge > return_line > find_V > walk > is_finish_Line > finish
    def setting_mode(self):
        line_info, edge_info = self.line_tracing()
        # line_info = {"DEGREE" : 0, "V" : False, "V_X" : [0 ,0], "V_Y" : [0 ,0], "H" : False, "H_X" : [0 ,0], "H_Y" : [0 ,0]}    
        # edge_info ={"EDGE_POS": None,"EDGE_L": False, "L_X" : [0 ,0], "L_Y" : [0 ,0],"EDGE_R": False, "R_X" : [0 ,0], "R_Y" : [0 ,0]}

        print(self.mode)
        # 방위 인식
        if self.mode == 'start' :
            if self.progress_of_roobot[0] != self.walk_info:
                self.progress_of_roobot.insert(0, self.walk_info)

            self.mode = 'detect_alphabet' # --> walk

            if self.progress_of_roobot[0] != self.mode:
                self.progress_of_roobot.insert(0, self.mode)

        elif self.mode == 'detect_alphabet':
            self.detect_alphabet()
            self.mode = 'walk'

        # 걷기 # 보정 추가로 넣기
        elif self.mode == 'walk' and self.walk_info != '┐' and self.walk_info != '┌' :
            if line_info["V"]==True and line_info["H"]==False:
                self.walk_info = '│'
                self.walk(line_info)
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
                    self.mode = 'detect_direction'
                    if self.progress_of_roobot[0] != self.walk_info:
                        self.progress_of_roobot.insert(0, self.walk_info)

            elif line_info["V"]==False and line_info["H"]==True: 
                self.mode = 'detect_direction'
                if self.progress_of_roobot[0] != self.walk_info:
                    self.progress_of_roobot.insert(0, self.walk_info)
            else:
                self.walk_info = None # 'modify_angle'
                self.walk(line_info)      

        # 화살표 방향 인식
        elif self.mode == 'detect_direction' or self.mode == 'detect_direction: fail':
            if self.mode == 'detect_direction: fail':
                self._motion.walk("BACKWARD", 1)
            else:
                pass

            if self.direction == None:
                self.detect_direction()
            else:
                self.mode = 'walk' 

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
        # 0. 확진 / 안전 구역 확인 : self.color 바꿔주세요



        # 1. red, blue 알파벳 구별: edge_info["EDGE_UP_Y"] 기준으로 윗 공간, self.alphabet_color 알파벳 색깔 넣어주세요
        # 2. 박스 트래킹 : self.alphabet_color 기준으로 edge_info["EDGE_UP_Y"] 아래 공간, self.box_pos박스 위치 바꿔주세요 (LEFT, RIGHT)



        # 3. 박스 구역의 평행선 H 기준으로 안으로 또는 밖으로 옮기기
            # 1) 박스 grap on 하면 손 내리고 고개든다
            # 2) H 찾을 때까지 돈다
                # self.box_pos == 'RIGHT' -> turn LEFT
                # self.box_pos == 'LEFT' -> turn RIGHT
            # 3) H 가장 끝 x값이 화면 끝라인에 근접하면? 돌기 멈춤
                # self.box_pos == 'RIGHT' -> ' max x > 600 ' -> 멈춤
                # self.box_pos == 'LEFT'  -> ' min_x < 50 '  -> 멈춤
            # 4) H 감지해서 얼추 맞추면 손 올리고 고개 내린다
            # 5) H에 가까워질 때까지 걷는다
            # 6) 화면에 그냥 lines 감지되면 mean y값이 일정범위 이상이 되면 멈춘다
            # 7) H 감지될 때까지 보정한다
                # H_degree가 몇이냐에 따라 turn LEFT, RIGHT 보정들어감
            # 8) 한두걸음 가서 놓는다.
        # 4. grap off 동작하면서 self.mode = 'end_mission', self.color = 'YELLOW'로 바꿔주세요









        # 미션 끝나면? - self.mode == 'end_mission'
        # 방탈출 #로봇 시야각 맞추기
        elif self.mode == 'end_mission' or self.mode == 'find_edge':
            if edge_info["EDGE_POS"] != None : # yellow edge 감지
                if 300 < edge_info["EDGE_POS"][0] < 360 : # yellow edge x 좌표 중앙 O
                    self.mode = 'return_line' # --> find_V
                    if self.progress_of_roobot[0] != self.mode:
                        self.progress_of_roobot.insert(0, self.mode)
                else: # yellow edge 중앙 X
                     self.find_edge()
                     if self.progress_of_roobot[0] != self.mode:
                        self.progress_of_roobot.insert(0, self.mode)
            else: # yellow edge 감지 X 
                self.mode = 'find_edge' # --> return_line
                self.find_edge()
                if self.progress_of_roobot[0] != self.mode:
                    self.progress_of_roobot.insert(0, self.mode)        

        elif self.mode == 'return_line':
            if edge_info["EDGE_POS"] != None :
                if edge_info["EDGE_POS"][1] > 478: # yellow edge y 좌표 가까이 O
                    #self._motion.walk(dir='FORWARD', loop=2)
                    #self.mode = 'find_V' # --> 걸을 직선 찾고 walk
                    self._motion.turn(self.direction, 1) ##
                    self.walk_info = None
                    self.mode = 'walk' ##
                    if self.progress_of_roobot[0] != self.mode:
                        self.progress_of_roobot.insert(0, self.mode)
                else: # yellow edge y 좌표 가까이 X
                    self.mode = 'return_line' # --> find_V
                    # self.return_line()
                    self._motion.walk(dir='FORWARD', loop=1)
                    if self.progress_of_roobot[0] != self.mode:
                        self.progress_of_roobot.insert(0, self.mode)
            else: # yellow edge 감지 X 
                self.mode = 'find_edge' # --> return_line
                self.find_edge()
                if self.progress_of_roobot[0] != self.mode:
                    self.progress_of_roobot.insert(0, self.mode)   
                    
        elif self.mode == 'find_V':
            if line_info["V"] == True :
                if 300 < line_info["V_X"][0] <340:
                    self._motion.walk(dir='FORWARD', loop=2)
                    self.mode = 'walk'
                else:
                    if line_info["V_X"][0] < 300:
                        self._motion.walk(dir='LEFT', loop=1)
                    elif line_info["V_X"][0] > 340:
                        self._motion.walk(dir='RIGHT', loop=1)
            else:
                self.mode = 'find_V'
                # self.find_V()
                self._motion.turn(self.direction, 1)


        # 나가기
        elif self.mode == 'is_finish_line':
            if self.count < 3:
                self._motion.walk(dir='FORWARD', loop=8)
                self.mode = 'walk'
                # self.count += 1 # count 방식 미션 grap_off 기준으로 count하면 좋을 듯 :: 중요
            else:
                self.mode = 'finish' # --> stop!
                if self.progress_of_roobot[0] != self.mode:
                        self.progress_of_roobot.insert(0, self.mode)
            