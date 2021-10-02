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
        #self._image_processor = ImageProcessor(video_path="Sensor/src/line_test/case2.h264")
        self._line_detector = LineDetector()
        self.direction = 'RIGHT'
        # self.mode = 'start'
        self.mode = 'start_mission'
        self.color = 'YELLOW'
        #self.color = ''
        self.box_pos = ''
        self.alphabet_color = None
        self.cube_grabbed = False
        self.curr_room_color = ""
        self.count = 0
        self.progress_of_roobot= [None, ]
        self.walk_info = None
        self.curr_head = deque([60,45,35])
        self.curr_activating_pos = "" # 방에서 활동중인 위치

    def set_basic_form(self):
        self._motion.basic_form()

    def get_distance_from_baseline(self, box_info, baseline=(320, 380)):
        # if bx - cx > 0
        # 왼쪽에 박스가 있는 것이므로 왼쪽으로 움직여야함,
        # if bx - cx < 0
        # 오른쪽에 박스가 있는 것이므로 오른쪽으로 움직여야함,
        # if by - cy > 0
        # 위쪽에 박스가 있는 것
        # if by - cy < 0
        # 아래쪽에 박스가 있는
        (bx, by) = baseline
        (cx, cy) = box_info
        return (bx-cx, by-cy)
    
    def check_turn(self):
        self._motion.turn("SLIDING_RIGHT",loop=6,sleep=1,grab=True,sliding=True)

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

    
    def update_box_pos(self, edge_info:dict, box_info:tuple):
        if edge_info["EDGE_DOWN"]:
            center_x = 320
            (cor_x, cor_y) = (edge_info["EDGE_DOWN_X"], edge_info["EDGE_DOWN_Y"])
            (box_x, box_y) = box_info

            if cor_x - 40 <= box_x <= cor_x + 40 :
                if box_y <= cor_y:
                    self.box_pos = "MIDDLE"
                else:
                    if box_x <= cor_x :
                        self.box_pos = "RIGHT"
                    else:
                        self.box_pos = "LEFT"


            elif box_x < cor_x -40:
                self.box_pos = "LEFT"

            else:
                self.box_pos = "RIGHT"
            print(f"BOX POS -> {self.curr_activating_pos}:, {cor_x},{cor_y}")
        return

    def detect_room_alphabet(self):
        self._motion.set_head(dir="LEFTRIGHT_CENTER")  # 알파벳을 인식하기 위해 고개를 다시 정면으로 향하게 한다.
        # 만약 알파벳 정보가 없다면 영상처리 측면을 개선하거나, 약간의 움직임을 통해 프레임 refresh가 필요하다.
        if self.alphabet_color is None:
            self._motion.set_head(dir="DOWN", angle=90)
            time.sleep(0.6)
            alphabet = self._image_processor.get_alphabet_info4room()
            if alphabet is None:
                print("감지되는 알파벳 정보가 없습니다")
                return
            (color, _ ) = alphabet
            self.alphabet_color = color
            print(alphabet)

        if self.alphabet_color:
            print(f"Milk box color is {self.alphabet_color}")
            self.mode = 'find_box'
        return

    def recognize_area_color(self):
        self._motion.set_head(dir=self.direction, angle=45) # 화살표 방향과 동일한 방향으로 45도 고개를 돌린다
        time.sleep(0.5)
        self._motion.set_head(dir="DOWN", angle=45) # 아래로 45도 고개를 내린다
        time.sleep(0.5)
        self.color = self._image_processor.get_area_color() # 안전지역인지, 확진지역인지 색상을 구별한다. BLACK 또는 GREEN
        self._motion.notice_area(area=self.color) # 지역에 대한 정보를 말한다
        time.sleep(0.5)
        self.mode = 'detect_room_alphabet' # 알파벳 인식 모드로 변경한다.
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
        line_info, edge_info, result =  self._image_processor.line_tracing(color=self.color)
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
        if direction == 'LEFT':
            if self.box_pos == 'RIGHT':
                self._motion.turn(dir='LEFT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
                time.sleep(1)
            if self.box_pos == 'LEFT':
                self._motion.turn(dir='RIGHT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
                time.sleep(1)
        elif direction == 'RIGHT':
            if self.box_pos == 'LEFT':
                self._motion.turn(dir='LEFT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
                time.sleep(1)
            if self.box_pos == 'RIGHT':
                self._motion.turn(dir='RIGHT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
                time.sleep(1)
        else:
            print('no direction')
            
                
            
    def catch_box(self):
        self._motion.grab()
        if self.box_pos == 'RIGHT':
            self._motion.turn(dir='LEFT', loop=5, grab=True)
            self._motion.move_arm(dir = 'LOW')
            time.sleep(1)
            self.mode = 'check_area'
        elif self.box_pos == 'LEFT':
            self._motion.turn(dir='RIGHT', loop=5, grab=True)
            self._motion.move_arm(dir = 'LOW')
            time.sleep(1)
            self.mode = 'check_area'
        else:
            self._motion.move_arm(dir = 'LOW')
            time.sleep(1)
            self.mode = 'check_area'
            
    def check_area(self, line_info, edge_info):
        print(line_info["ALL_X"], line_info["H"])
        if self.box_pos == 'RIGHT':
            if line_info["H"] == True:
                self.mode = 'fit_area'
                time.sleep(1)
            else:
                self._motion.turn(dir='LEFT', loop=1, grab=True)
                time.sleep(1)
        elif self.box_pos == 'LEFT':
            if line_info["H"] == True:
                self.mode = 'fit_area'
                time.sleep(1)
            else:
                self._motion.turn(dir='RIGHT', loop=1, grab=True)
                time.sleep(1)
        elif self.box_pos == 'MIDDLE':
            self.mode = 'fit_area'
            time.sleep(1)
        else:
            print("self.box_pos is None, Please check it")
        

    def fit_area(self, line_info, edge_info):
        print(line_info["ALL_X"])
        if self.box_pos == 'RIGHT':
            if line_info["ALL_X"][1] > 440:
                if line_info["ALL_X"][0] < 180:
                    print('find!!!!!!!!!!!!')
                    self._motion.move_arm(dir = 'HIGH') # 잡은 상태로 팔 앞으로 뻗고 고개 내림
                    time.sleep(1)
                    self.mode = 'move_into_area'
                else:
                    self._motion.walk(dir='RIGHT', loop=1, grab=True)
                    time.sleep(1)
            else:
                self._motion.walk(dir='RIGHT', loop=1, grab=True)
                time.sleep(1)
        elif self.box_pos == 'LEFT':
            if line_info["ALL_X"][0] < 150 :
                if line_info["ALL_X"][1] > 440:
                    print('find!!!!!!!!!!!!')
                    self._motion.move_arm(dir = 'HIGH') # 잡은 상태로 팔 앞으로 뻗고 고개 내림
                    time.sleep(1)
                    self.mode = 'move_into_area'
                else:
                    self._motion.walk(dir='LEFT', loop=1)
                    time.sleep(1)
            else:
                self._motion.walk(dir='LEFT', loop=1)
                time.sleep(1)
        elif self.box_pos == 'MIDDLE':
            if edge_info["EDGE_DOWN_X"] < 300:
                self._motion.walk(dir='RIGHT', loop=1, grab=True)
                time.sleep(1)
            elif edge_info["EDGE_DOWN_X"] > 340 :
                self._motion.walk(dir='LEFT', loop=1, grab=True)
                time.sleep(1)
            else: # elif 300 < edge_info["EDGE_DOWN_X"] < 360 :
                self._motion.move_arm(dir = 'HIGH') # 잡은 상태로 팔 앞으로 뻗고 고개 내림
                time.sleep(1)
                self.mode = 'move_into_area'
        else:
            print("self.box_pos is None, Please check it")
            
# ---------------------- set head mode 45 ----------------------------------------------------------------          
    def move_into_area(self, line_info, edge_info):
        print(line_info['ALL_Y'])
        if self.box_pos == 'LEFT' or 'RIGHT':
            if line_info['ALL_Y'][1] > 460: # 발 나온다는 생각으로 절반 아래에 오면 발 앞이라고 생각할 것임 -- 수정 예정
                self.mode = 'box_into_area'
            else:
                self._motion.walk(dir='FORWARD', loop=1, grab=True)
                time.sleep(1)
        elif self.box_pos == 'MIDDLE':
            if line_info['ALL_Y'][1] > 460:
                self.mode = 'box_into_area'
            else:
                self._motion.walk(dir='FORWARD', loop=1, grab=True)
                time.sleep(1)
        else:
            print("self.box_pos is None, Please check it")

# ---------------------- set head mode 35 ----------------------------------------------------------------
    #def box_into_area(self, line_info, edge_info):
        #if self.box_pos == 'LEFT' or 'RIGHT':
            #if line_info['ALL_Y'][1] > 240: # 발 나온다는 생각으로 절반 아래에 오면 발 앞이라고 생각할 것임 -- 수정 예정
                #if line_info["H"] == True and line_info['H_DEGREE'] < 2 :
                    #self._motion.walk(dir='FORWARD', loop=1, grab=True)
                    #self._motion.grab(switch=False) # 앉고 잡은 박스 놓는 모션 넣기
                    #self.mode = 'end_mission'
                    #self.color = 'YELLOW'
               # else:
                #    #line_info['H_DEGREE'] 따라 수평선 찾는 거 넣을 예정인데 우선은 다른 걸로 대체
                 #   self._motion.walk(dir='FORWARD', loop=4, grab=True)
                  #  self._motion.grab(witch=False) # 앉고 잡은 박스 놓는 모션 넣기
                   # self.mode = 'end_mission'
                    #self.color = 'YELLOW'
           # else:
             #   self._motion.walk(dir='FORWARD', loop=1, grab=True)


       # elif self.box_pos == 'MIDDLE':
          #  if line_info['ALL_Y'][1] > 240:
                #line_info['H_DEGREE'] 따라 수평선 찾는 거 넣을 예정인데 우선은 다른 걸로 대체
              #  self._motion.walk(dir='FORWARD', loop=4, grab=True)
              #  self._motion.grab(switch=False) # 앉고 잡은 박스 놓는 모션 넣기
              #  self.mode = 'end_mission'
              #  self.color = 'YELLOW'
           # else:
               # self._motion.walk(dir='FORWARD', loop=1, grab=True)
       # else:
      #      print("self.box_pos is None, Please check it")
    
    def box_into_area(self, line_info, edge_info):
        self._motion.walk(dir='FORWARD', loop=4, grab=True)
        self._motion.grab(switch=False) # 앉고 잡은 박스 놓는 모션 넣기
        self._motion.set_head(dir ='DOWN', angle=60)
        self.mode = 'end_mission'
        self.color = 'YELLOW'


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
                self._motion.walk("FORWARD", 2)
                self._motion.walk(self.direction, 2)
                self._motion.turn(self.direction, 7)
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


                # 0. 확진 / 안전 구역 확인 : self.color 바꿔주세요, self.mode = 'box_tracking'로 바꿔주세요.
        elif self.mode == 'start_mission':
            self.recognize_area_color()

        # 1. red, blue 알파벳 구별: edge_info["EDGE_UP_Y"] 기준으로 윗 공간, self.alphabet_color 알파벳 색깔 넣어주세요
        elif self.mode == 'detect_room_alphabet':
            self.detect_room_alphabet()


        # 2. 박스 트래킹 : self.alphabet_color 기준으로 edge_info["EDGE_UP_Y"] 아래 공간, self.box_pos박스 위치 바꿔주세요 (LEFT, MIDDLE, RIGHT)
        ## grap on 과 동시에 self.mode = 'box_into_area'로 바꾸기
        ## # 1) 박스 grap on 하면 손 내리고 고개든다 (MIDDLE이면 고개 좀 많이 내려주기, LEFT RIGHT는 30 정도면 될 듯?아마??)
        # ++ 집은 채로 손내리는 모션
        # ++ 고개 드는 모션
        elif self.mode == 'find_box':
            ### 계속해서 안전/확진지역 영역의 코너 정보를 기반으로 현재 로봇이 방에서 어디에서 활동하고 있는지를 업데이트 해줍니다.
            self._motion.set_head("DOWN", self.curr_head[0])
            box_info = self._image_processor.get_milk_info(color=self.alphabet_color)
            if box_info is None:
                if self.curr_head[0] == 35:
                    self._motion.turn(dir=self.direction, loop=1)
                self.curr_head.rotate(-1)
            else:
                self.mode = "track_box"
                self.update_box_pos(edge_info=edge_info, box_info=box_info)
                print("box_pos: ",self.box_pos)

        elif self.mode == 'track_box':
            self._motion.set_head("DOWN", self.curr_head[0])
            box_info = self._image_processor.get_milk_info(color=self.alphabet_color)
            if box_info is None:
                self.mode = 'find_box'
            else:
                (cx, cy) = box_info
                (dx, dy) = self.get_distance_from_baseline(box_info=box_info)
                if dy > 10:  # 기준선 보다 위에 있다면
                    if -40 <= dx <= 40:
                        print("기준점에서 적정범위. 전진 전진")
                        self._motion.walk(dir='FORWARD', loop=1)
                    elif  dx <= -90 :
                        self._motion.turn(dir='RIGHT', loop=1)
                    elif -90 < dx <= -50:  # 오른쪽
                        print("기준점에서 오른쪽으로 많이 치우침. 조정한다")
                        self._motion.walk(dir='RIGHT', loop=3)
                    elif -50 < dx < -40:
                        print("기준점에서 오른쪽으로 치우침. 조정한다")
                        self._motion.walk(dir='RIGHT', loop=1)
                    elif 90 > dx >= 50:  # 왼쪽
                        print("기준점에서 왼쪽으로 많이 치우침. 조정한다")
                        self._motion.walk(dir='LEFT', loop=3)
                    elif 50 > dx > 40:  # 왼쪽
                        print("기준점에서 왼쪽으로 치우침. 조정한다")
                        self._motion.walk(dir='LEFT', loop=1)
                    elif dx >= 90:
                        self._motion.turn(dir='LEFT', loop=1)
                        
                else:
                    if self.curr_head[0] == 35:
                        self._motion.grab(switch=True)
                        
                        if self.box_pos == 'RIGHT':
                            self._motion.turn(dir='LEFT', loop=5, grab=True)
                            self._motion.move_arm(dir = 'LOW')
                            time.sleep(1)
                            self.mode = 'check_area'
                        elif self.box_pos == 'LEFT':
                            self._motion.turn(dir='RIGHT', loop=5, grab=True)
                            self._motion.move_arm(dir = 'LOW')
                            time.sleep(1)
                            self.mode = 'check_area'
                        else:
                            self._motion.move_arm(dir = 'LOW')
                            time.sleep(1)
                            self.mode = 'check_area'
                        
                    else:
                        self.curr_head.rotate(-1)


        #elif self.mode == 'catch_box':
            #self.catch_box()

        # 3. 박스 구역의 평행선 H 기준으로 안으로 또는 밖으로 옮기기
        elif self.mode == 'check_area':
            self.check_area(line_info, edge_info)
            
        elif self.mode == 'fit_area':
            self.fit_area(line_info, edge_info)
            
        elif self.mode == 'move_into_area':
            self.move_into_area(line_info, edge_info)

        elif self.mode == 'box_into_area':
            self.box_into_area(line_info, edge_info)

        # 방탈출 #로봇 시야각 맞추기
        elif self.mode == 'end_mission' or self.mode == 'find_edge':
            if edge_info["EDGE_POS"] != None : # yellow edge 감지
                if 300 < edge_info["EDGE_POS"][0] < 360 : # yellow edge x 좌표 중앙 O
                    print('yellow edge 감지 중앙 O')
                    self.mode = 'return_line' # --> find_V
                    if self.progress_of_roobot[0] != self.mode:
                        self.progress_of_roobot.insert(0, self.mode)
                else: # yellow edge 중앙 X
                    print('yellow edge 감지 중앙 X')
                    self.find_edge()
                    if self.progress_of_roobot[0] != self.mode:
                        self.progress_of_roobot.insert(0, self.mode)
            else: # yellow edge 감지 X
                print('yellow edge 감지 X ')
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
            