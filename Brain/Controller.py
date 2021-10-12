from Sensor.ImageProcessor import ImageProcessor
from Sensor.LineDetector import LineDetector
from Actuator.Motion import Motion
import numpy as np
import cv2
import time
import sys
from collections import deque

class Robot:

    def __init__(self, video_path ="", DEBUG=False):
        self._motion = Motion(DEBUG)
        self._image_processor = ImageProcessor(video_path=video_path)
        self._line_detector = LineDetector()
        self.direction = None
        self.alphabet = None
        self.alphabet_color = None
        self.cube_grabbed = False
        self.return_head = None # return 할 때 고개 각도 바꿀 지 고민 중 10/08
        self.count = 2
        self.progress_of_roobot= [None, ]
        
        self.walk_info = None
        self.curr_head = deque([75,60,35])
        self.curr_activating_pos = "" # 방에서 활동중인 위치

        
        self.mode = "start"
        self.direction = None
        self.color = "YELLOW"
        self.box_pos = ""
        self.curr_room_color = ""
        
        #self.mode = "walk"
        #self.direction = "LEFT"
        #self.color = "YELLOW"
        #self.box_pos = ""
        #self.curr_room_color = ""
        
        #self.mode = 'walk'
        #self.direction = 'LEFT'
        #self.color = "YELLOW"
        #self.box_pos = None
        #self.curr_room_color = ""

        # 박스 앞에 놓고 테스트 하고 싶을 때
        #self.direction = 'RIGHT'
        #self.mode = 'catch_box'
        #self.color = 'BLACK'
        #self.box_pos = 'LEFT'
        #self.curr_room_color = "BLACK"

        # ㄱ 자 오기 전부터 walk부터 테스트하고 싶을 때 실행시키기전에 먼저 10도 내려주기
        #self.direction = 'LEFT'
        #self.mode = 'walk'
        #self.color = 'YELLOW'
        #self.box_pos = None
        #self._motion.set_head("DOWN", 10)
        #self.curr_room_color = None
        self.mode_history = self.mode


    def set_basic_form(self):
        self._motion.basic_form()
        
    def check_motion(self):
        self._motion.grab()
        #self._motion.walk(dir = 'LEFT', loop=4 )

    def get_distance_from_baseline(self, box_info, baseline=(320, 370)):
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
        #self._motion.move_arm(dir = 'LOW')
        #self._motion.walk(dir='FORWARD', loop=1)
        self._motion.set_head('DOWN', 45)


    def old_line_tracing(self):
        self._motion.set_head('DOWN', 30)
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


    def detect_alphabet(self):
        self._motion.set_head('DOWN', 75)
        #time.sleep(1)
        flag = True
        self.alphabet = self._image_processor.get_door_alphabet()
        print(self.alphabet)
        if self.alphabet is None:
            alphabet = self._image_processor.get_door_alphabet()
            #if flag:
                #self._motion.walk("RIGHT")
                #time.sleep(1)
            #else:
                #self._motion.walk("LEFT")
                #time.sleep(1)

            #flag = not flag
        else:
            self._motion.notice_direction(dir=self.alphabet)
            #time.sleep(1)
    
    
    def update_box_pos(self, edge_info:dict, box_info:tuple):
        if edge_info["EDGE_DOWN"]:
            center_x = 320
            (cor_x, cor_y) = (edge_info["EDGE_DOWN_X"], edge_info["EDGE_DOWN_Y"])
            (box_x, box_y) = box_info
            dx = 50
            if cor_x - dx <= box_x <= cor_x + dx :
                if box_y <= cor_y:
                    self.box_pos = "MIDDLE"
                else:
                    if box_x <= cor_x :
                        self.box_pos = "RIGHT"
                    else:
                        self.box_pos = "LEFT"


            elif box_x < cor_x -dx:
                self.box_pos = "LEFT"

            else:
                self.box_pos = "RIGHT"
                
            print(f"BOX POS -> {self.curr_activating_pos}:, {cor_x},{cor_y}")
        elif self.direction == "RIGHT":
            self.box_pos = "LEFT"
        else:
            self.box_pos = "RIGHT"

    def detect_room_alphabet(self, edge_info):
        self._motion.set_head(dir="LEFTRIGHT_CENTER")  # 알파벳을 인식하기 위해 고개를 다시 정면으로 향하게 한다.
        # 만약 알파벳 정보가 없다면 영상처리 측면을 개선하거나, 약간의 움직임을 통해 프레임 refresh가 필요하다.
        if self.alphabet_color is None:
            self._motion.set_head(dir="DOWN", angle=80)
            time.sleep(0.6)
            alphabet = self._image_processor.get_alphabet_info4room(method="CONTOUR", edge_info=edge_info)
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
        #self.color = self._image_processor.get_area_color() # 안전지역인지, 확진지역인지 색상을 구별한다. BLACK 또는 GREEN
        #self.curr_room_color = self._image_processor.get_area_color()
        self.color = 'GREEN'
        line_info, edge_info = self.line_tracing(line_visualization=False, edge_visualization=True)
        if edge_info['EDGE_DOWN'] == True:
            self.color ='GREEN'
        else:
            self.color ='BLACK'
        self._motion.notice_area(area=self.color) # 지역에 대한 정보를 말한다
        self.curr_room_color = self.color
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

    def line_tracing(self, line_visualization=False, edge_visualization=False):
        line_info, edge_info, result =  self._image_processor.line_tracing(color=self.color, line_visualization = line_visualization, edge_visualization=edge_visualization)
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
            #self._motion.walk('FORWARD', 2)
            #self._motion.walk(self.direction, 4)
            #self._motion.turn(self.direction, 8)
            #self._motion.set_head('DOWN', 10)
            print(self.direction)

    def walk(self, line_info, walk_info):
        # line_info = {"DEGREE" : 0, "V" : False, "V_X" : [0 ,0], "V_Y" : [0 ,0], "H" : False, "H_X" : [0 ,0], "H_Y" : [0 ,0]}
        self._motion.set_head(dir = 'DOWN', angle = 10)
        #time.sleep(1)
        if walk_info == '│':
            if line_info["DEGREE"] > 85 and line_info["DEGREE"] < 95:
                if 290 < line_info["V_X"][0] <350:
                    print('walk')
                    print('│', line_info)
                    self._motion.walk(dir='FORWARD', loop=1)
                    #time.sleep(1)
                else:
                    if line_info["V_X"][0] < 290:
                        print('← ←', line_info["V_X"][0])
                        self._motion.walk(dir='LEFT', loop=1)
                        #time.sleep(1)
                    elif line_info["V_X"][0] > 350:
                        print('→ →', line_info["V_X"][0])
                        self._motion.walk(dir='RIGHT', loop=1)
                        #time.sleep(1)
            elif line_info["DEGREE"] <= 85:
                print('MODIFY angle --LEFT', line_info)
                self._motion.turn(dir='LEFT', loop=1)
                #time.sleep(1)
            elif line_info["DEGREE"] >= 95:
                print('MODIFY angle --RIGHT', line_info)
                self._motion.turn(dir='RIGHT', loop=1)
                #time.sleep(1)
            else:
                print('else')


        elif walk_info == None: # 'modify_angle'
            if line_info["DEGREE"] <= 85:
                print('MODIFY angle --LEFT', line_info)
                self._motion.turn(dir='LEFT', loop=1)
                #time.sleep(1)
            elif line_info["DEGREE"] >= 95:
                print('MODIFY angle --RIGHT', line_info)
                self._motion.turn(dir='RIGHT', loop=1)
                #time.sleep(1)
            else:
                print('else')

        else:
            print('walk_info is not │ or None ------------>', self.walk_info)    


    def find_edge(self): #find_corner_for_outroom
        if self.curr_room_color=='BLACK':
            self._motion.turn(dir=self.direction, loop=1, grab=True) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
            time.sleep(1.5)

        elif self.curr_room_color == 'GREEN':
            if self.direction == 'LEFT':
                if self.box_pos == 'RIGHT':
                    self._motion.turn(dir='LEFT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
                    time.sleep(1.5)
                if self.box_pos == 'LEFT':
                    self._motion.turn(dir='RIGHT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
                    time.sleep(1.5)
            elif self.direction == 'RIGHT':
                if self.box_pos == 'LEFT':
                    self._motion.turn(dir='RIGHT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
                    time.sleep(1.5)
                if self.box_pos == 'RIGHT':
                    self._motion.turn(dir='LEFT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
                    time.sleep(1.5)
            else:
                print('no direction')
                
            
    def catch_box(self):
        self._motion.grab()
        if self.color == 'GREEN':
            if self.box_pos == 'RIGHT':
                self._motion.turn(dir='LEFT', loop=5, grab=True)
                self._motion.move_arm(dir = 'LOW')
                #time.sleep(1)
                self.mode = 'check_area'
            elif self.box_pos == 'LEFT':
                self._motion.turn(dir='RIGHT', loop=5, grab=True)
                self._motion.move_arm(dir = 'LOW')
                #time.sleep(1)
                self.mode = 'check_area'
            else:
                self._motion.move_arm(dir = 'LOW')
                #time.sleep(1)
                self.mode = 'check_area'
        elif self.color == 'BLACK':
            self._motion.turn(dir=self.direction, loop=5, grab=True)
            #time.sleep(1)
            self.mode = 'end_mission'
            self.color = 'YELLOW'
            
            
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
        self._motion.set_head(dir='DOWN', angle=35)
        time.sleep(1)
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
        self._motion.walk(dir='FORWARD', loop=2, grab=True)
        self._motion.grab(switch=False) # 앉고 잡은 박스 놓는 모션 넣기
        #self._motion.set_head(dir ='DOWN', angle=60)
        #self.mode = 'end_mission'
        self.color = 'YELLOW'
        self.count += 1


    # start > detect_alphabet> walk │ > ─ > detect_direction > walk │ > ┐ , ┌  > start_mission > end_mission > find_edge > return_line > find_V > walk > is_finish_Line > finish
    def setting_mode(self):
        if self.color == 'YELLOW':
            line_info, edge_info = self.line_tracing(line_visualization=True, edge_visualization=False)
        elif self.color == 'GREEN':
            line_info, edge_info = self.line_tracing(line_visualization=False, edge_visualization=True)
        else:
            line_info, edge_info = self.line_tracing()
        # line_info = {"DEGREE" : 0, "V" : False, "V_X" : [0 ,0], "V_Y" : [0 ,0], "H" : False, "H_X" : [0 ,0], "H_Y" : [0 ,0]}    
        # edge_info ={"EDGE_POS": None,"EDGE_L": False, "L_X" : [0 ,0], "L_Y" : [0 ,0],"EDGE_R": False, "R_X" : [0 ,0], "R_Y" : [0 ,0]}

        print(self.mode, self.walk_info)
        # 방위 인식
        if self.mode == 'start' :
            if self.progress_of_roobot[0] != self.walk_info:
                self.progress_of_roobot.insert(0, self.walk_info)

            self.mode = 'detect_alphabet' # --> walk

            if self.progress_of_roobot[0] != self.mode:
                self.progress_of_roobot.insert(0, self.mode)

        elif self.mode == 'detect_alphabet':
            if self.alphabet is None:
                self.detect_alphabet()
            else:
                self._motion
                self.mode = 'walk'
                #self._motion.move_arm(dir="HIGH")

        # 화살표 방향 인식
        elif self.mode == 'detect_direction' or self.mode == 'detect_direction: fail':
            self._motion.set_head(dir='DOWN', angle=90)
            if self.mode == 'detect_direction: fail':
                self._motion.walk("BACKWARD", 1)
                time.sleep(1)
            else:
                pass

            if self.direction == None:
                self.detect_direction()
            else:
                self._motion.walk('FORWARD', 2)
                self._motion.walk(self.direction, 4)
                self._motion.turn(self.direction, 8)
                self._motion.set_head('DOWN', 10)
                time.sleep(1)
                #self._motion.walk("FORWARD", 1)
                #self._motion.walk(self.direction, 2)
                #self._motion.turn(self.direction, 7)
                self.mode = 'walk' 
                self.walk_info = '│'
                self._motion.set_head(dir='DOWN', angle = 10)
                time.sleep(1)



        # 걷기 # 보정 추가로 넣기
        elif self.mode == 'walk' and self.walk_info != '┐' and self.walk_info != '┌' :
            print('walk start!!!!')
            self._motion.set_head(dir='DOWN', angle = 10)
            time.sleep(1)
            if line_info["V"]==True and line_info["H"]==False:
                print('go')
                self.walk_info = '│'
                self.walk(line_info, self.walk_info)
                if self.progress_of_roobot[0] != self.walk_info:
                    self.progress_of_roobot.insert(0, self.walk_info)
                    
            elif line_info["V"]==False and line_info["H"]==False:
                print('modify_angle')
                self.walk_info = None # 'modify_angle'
                self.walk(line_info, self.walk_info)     

            else:
                print(line_info["H_X"])
                if line_info["H_X"][0] <= 100 and line_info["H_X"][1] >= 550 :
                    self.walk_info = 'T'
                    print(line_info["H_Y"][1])
                    if line_info["H_Y"][1] > 190:
                        self.mode = 'detect_direction'
                        
                        self.set_basic_form()
                        if self.progress_of_roobot[0] != self.walk_info:
                            self.progress_of_roobot.insert(0, self.walk_info)
                    else:
                        self._motion.walk("FORWARD", 1)
                        time.sleep(1)
                        
                else:
                    if line_info["H_X"][0] <= 200 and line_info["H_X"][1] <= 400:
                        self.walk_info = '┐'
                        if self.progress_of_roobot[0] != self.walk_info:
                            self.progress_of_roobot.insert(0, self.walk_info)

                    elif line_info["H_X"][1] >= 400 and line_info["H_X"][0] >= 200 :
                        self.walk_info = '┌'
                        if self.progress_of_roobot[0] != self.walk_info:
                            self.progress_of_roobot.insert(0, self.walk_info)
                    else:
                        print('out of range')

        
        # 미션 진입 판별
        #elif self.mode == 'walk' and self.walk_info == '┐':
            #self._motion.set_head(dir='DOWN', angle = 10)
            #if line_info["H_Y"][1] > 280:
                #if self.direction == 'RIGHT':
                    #self.mode = 'start_mission' # --> end_mission --> return_line
                    #if self.progress_of_roobot[0] != self.mode:
                        #self.progress_of_roobot.insert(0, self.mode)

                #elif self.direction == 'LEFT':
                    #self.mode = 'is_finish_line' # --> walk / finish
                    #if self.progress_of_roobot[0] != self.mode:
                        #self.progress_of_roobot.insert(0, self.mode)
                #else:
                    #print('The Robot has not direction, Please Set **self.direction**')
            #else:
                #self._motion.walk("FORWARD", 1)
                #time.sleep(1)

        elif self.mode == 'walk' and self.walk_info =='┌':
            self._motion.set_head(dir='DOWN', angle = 10)
            #time.sleep(1)
            if line_info["H_Y"][1] > 50 :
                self._motion.walk("FORWARD", 2)
                #time.sleep(1)
                if self.direction == 'RIGHT':
                    self.mode = 'is_finish_line' # --> end_mission --> return_line
                    if self.progress_of_roobot[0] != self.mode:
                        self.progress_of_roobot.insert(0, self.mode)

                elif self.direction == 'LEFT':
                
                    self.mode = 'start_mission' # --> walk / finish
                    if self.progress_of_roobot[0] != self.mode:
                        self.progress_of_roobot.insert(0, self.mode)
                else:
                    print('The Robot has not direction, Please Set **self.direction**')
            else:
                self.walk(line_info, '│')
                #time.sleep(1)
            


        # 미션 진입 판별
        elif self.mode == 'walk' and self.walk_info == '┐':
            self._motion.set_head(dir='DOWN', angle = 10)
            #time.sleep(1)
            if line_info["H_Y"][1] > 90 :
                self._motion.walk("FORWARD", 1)
                #time.sleep(1)
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
            else:
                self.walk(line_info,'│')
                #time.sleep(1)
            
                

        #elif self.mode == 'walk' and self.walk_info =='┌':
            #self._motion.set_head(dir='DOWN', angle = 10)
            #if line_info["H_Y"][0] > 280:
                #if self.direction == 'LEFT':
                    #self.mode = 'start_mission' # --> end_mission
                    #if self.progress_of_roobot[0] != self.mode:
                        #self.progress_of_roobot.insert(0, self.mode)
                #elif self.direction == 'RIGHT':
                    #self.mode = 'is_finish_line' # --> finish 
                    #if self.progress_of_roobot[0] != self.mode:
                        #self.progress_of_roobot.insert(0, self.mode)
                #else:
                    #print('The Robot has not direction, Please Set **self.direction**')
            #else:
                #self._motion.walk("FORWARD", 1)
                #time.sleep(1)


                # 0. 확진 / 안전 구역 확인 : self.color 바꿔주세요, self.mode = 'box_tracking'로 바꿔주세요.
        elif self.mode == 'start_mission':
            self.recognize_area_color()

        # 1. red, blue 알파벳 구별: edge_info["EDGE_UP_Y"] 기준으로 윗 공간, self.alphabet_color 알파벳 색깔 넣어주세요
        elif self.mode == 'detect_room_alphabet':
            self.detect_room_alphabet(edge_info=edge_info)


        # 2. 박스 트래킹 : self.alphabet_color 기준으로 edge_info["EDGE_UP_Y"] 아래 공간, self.box_pos박스 위치 바꿔주세요 (LEFT, MIDDLE, RIGHT)
        ## grap on 과 동시에 self.mode = 'box_into_area'로 바꾸기
        ## # 1) 박스 grap on 하면 손 내리고 고개든다 (MIDDLE이면 고개 좀 많이 내려주기, LEFT RIGHT는 30 정도면 될 듯?아마??)
        # ++ 집은 채로 손내리는 모션
        # ++ 고개 드는 모션
        elif self.mode == 'find_box':
            ### 계속해서 안전/확진지역 영역의 코너 정보를 기반으로 현재 로봇이 방에서 어디에서 활동하고 있는지를 업데이트 해줍니다.
            self._motion.set_head("DOWN", self.curr_head[0])
            box_info = self._image_processor.get_milk_info(color=self.alphabet_color, edge_info = edge_info)
            if box_info is None:
                if self.curr_head[0] == 35:
                    self._motion.turn(dir=self.direction, loop=1)
                self.curr_head.rotate(-1)
            else:
                self.mode = "track_box"
                if self.curr_room_color == "GREEN":
                    self.update_box_pos(edge_info=edge_info, box_info=box_info)
                print("box_pos: ", self.box_pos)


        elif self.mode == 'track_box':
            self._motion.set_head("DOWN", self.curr_head[0])
            box_info = self._image_processor.get_milk_info(color=self.alphabet_color, edge_info=edge_info)
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
                        if self.color == 'GREEN':
                            if self.box_pos == 'RIGHT':
                                self._motion.turn(dir='LEFT', loop=5, grab=True)
                                self._motion.move_arm(dir = 'LOW')
                                #time.sleep(1)
                                self.mode = 'check_area'
                            elif self.box_pos == 'LEFT':
                                self._motion.turn(dir='RIGHT', loop=5, grab=True)
                                self._motion.move_arm(dir = 'LOW')
                                #time.sleep(1)
                                self.mode = 'check_area'
                            else:
                                self._motion.move_arm(dir = 'LOW')
                                #time.sleep(1)
                                self.mode = 'check_area'
                        elif self.color == 'BLACK':
                            self._motion.turn(dir=self.direction, loop=5, grab=True)
                            #time.sleep(1)
                            self.mode = 'end_mission'
                            self.color = 'YELLOW'
                            
                    else:
                        self.curr_head.rotate(-1)


        elif self.mode == 'catch_box':
            self.catch_box()

        # 3. 박스 구역의 평행선 H 기준으로 안으로 또는 밖으로 옮기기
        elif self.mode == 'check_area':
            self.check_area(line_info, edge_info)
            
        elif self.mode == 'fit_area':
            self.fit_area(line_info, edge_info)
            
        elif self.mode == 'move_into_area':
            self.move_into_area(line_info, edge_info)

        elif self.mode == 'box_into_area':
            self.box_into_area(line_info, edge_info)
            if self.box_pos == 'LEFT':
               self._motion.turn(dir = 'RIGHT', loop=9 )
               
            if self.box_pos == 'RIGHT':
               self._motion.turn(dir = 'LEFT', loop=9 )
            else:
                pass
                
            self.mode = 'end_mission'
            self.colot = 'YELLOW'


        #elif self.mode == 'end_mission':
            #self._motion.set_head(dir ='DOWN', angle = 45)
            #if edge_info["EDGE_POS"] != None : # yellow edge 감지
                #if 300 < edge_info["EDGE_POS"][0] < 380 : # yellow edge x 좌표 중앙 O
                    #print('yellow edge 감지 중앙 O')
                    #self.mode = 'return_line' # --> find_V
                    #if self.progress_of_roobot[0] != self.mode:
                        #self.progress_of_roobot.insert(0, self.mode)
                #else: # yellow edge 중앙 X
                    #print('yellow edge 감지 중앙 X')
                    #self.find_edge()
                    #if self.progress_of_roobot[0] != self.mode:
                        #self.progress_of_roobot.insert(0, self.mode)
           # else: # yellow edge 감지 X
               # print('yellow edge 감지 X ')
               # self.mode = 'end_mission' # --> find_edge
              #  self.find_edge()
              #  if self.progress_of_roobot[0] != self.mode:
                   # self.progress_of_roobot.insert(0, self.mode)       
        


#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
        elif self.mode == 'end_mission':
            self._motion.set_head(dir ='DOWN', angle = 60)
            time.sleep(1)
            if self.box_pos == 'RIGHT':
                if line_info["ALL_X"][1] != 0 and line_info["ALL_X"][1] > 240:
                    if line_info["ALL_Y"][1] < 320 : # yellow 감지
                        self._motion.set_head(dir ='DOWN', angle = 60)
                        time.sleep(1.5)
                        self.return_head = '60'
                        self.mode = 'find_edge'
                    else:
                        self._motion.set_head(dir ='DOWN', angle = 45)
                        time.sleep(1.5)
                        self.mode = 'find_edge'
                        self.return_head = '45'
                else:
                    if self.curr_room_color == 'BLACK':
                        self._motion.turn(dir = 'LEFT', loop = 1, grab = True)
                        time.sleep(1)
                    else:
                        self._motion.turn(dir = 'LEFT', loop = 1)
                        time.sleep(1)
            else:
                if line_info["ALL_X"][1] != 0 and line_info["ALL_X"][1] > 240:
                    if line_info["ALL_Y"][1] < 320 : # yellow 감지
                        self._motion.set_head(dir ='DOWN', angle = 60)
                        time.sleep(1.5)
                        self.return_head = '60'
                        self.mode = 'find_edge'
                    else:
                        self._motion.set_head(dir ='DOWN', angle = 45)
                        time.sleep(1.5)
                        self.mode = 'find_edge'
                        self.return_head = '45'
                  
                else:
                    if self.curr_room_color == 'BLACK':
                        self._motion.turn(dir = 'RIGHT', loop = 1, grab = True)
                        time.sleep(1)
                    else:
                        self._motion.turn(dir = 'RIGHT', loop = 1)
                        time.sleep(1)
    
        elif self.mode == 'find_edge':
            if edge_info["EDGE_POS"] != None : # yellow edge 감지
                if 300 < edge_info["EDGE_POS"][0] < 380 : # yellow edge x 좌표 중앙 O
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
                self.mode = 'find_edge' # --> find_edge
                self.find_edge()
                if self.progress_of_roobot[0] != self.mode:
                    self.progress_of_roobot.insert(0, self.mode)    

        elif self.mode == 'return_line':
            if self.return_head == '60':
                if line_info["ALL_Y"][1] > 240 :
                    self._motion.set_head(dir='DOWN', angle=45)
                    self.return_head = '45'
                    time.sleep(1.5)
                        
            elif self.return_head == '45':
                if line_info["ALL_Y"][1] > 240 :
                    self._motion.set_head(dir='DOWN', angle=35)
                    self.return_head = '35'
                    time.sleep(1.5)
            
            if self.curr_room_color == 'BLACK':
                if edge_info["EDGE_POS"] != None :
                    print(self.curr_room_color, edge_info["EDGE_POS"][1])
                    if edge_info["EDGE_POS"][1] > 450: # yellow edge y 좌표 가까이 O
                        self._motion.walk(dir='FORWARD', loop=1, grab=True)
                        self._motion.grab(switch = False)
                        self._motion.turn(dir=self.direction, loop = 2)
                        time.sleep(1)
                        self.mode = 'find_V' # --> 걸을 직선 찾고 walk
                        if self.progress_of_roobot[0] != self.mode:
                            self.progress_of_roobot.insert(0, self.mode)
                    else: # yellow edge y 좌표 가까이 X
                        self.mode = 'return_line' # --> find_V
                        self._motion.walk(dir='FORWARD', loop=1, grab=True)
                        time.sleep(1)           
                        if self.progress_of_roobot[0] != self.mode:
                            self.progress_of_roobot.insert(0, self.mode)
                else: # yellow edge 감지될 때까지 걷기
                    self._motion.walk(dir='FORWARD', loop=1, grab=True)
                    time.sleep(1)
                    if self.progress_of_roobot[0] != self.mode:
                        self.progress_of_roobot.insert(0, self.mode)

            elif self.curr_room_color == 'GREEN':
                if edge_info["EDGE_POS"] != None :
                    if edge_info["EDGE_POS"][1] > 450: # yellow edge y 좌표 가까이 O
                        self._motion.walk(dir='FORWARD', loop=1)
                        self._motion.turn(dir=self.direction, loop = 2)
                        time.sleep(1)
                        self.mode = 'find_V' # --> 걸을 직선 찾고 walk
                        if self.progress_of_roobot[0] != self.mode:
                            self.progress_of_roobot.insert(0, self.mode)
                    else: # yellow edge y 좌표 가까이 X
                        self.mode = 'return_line' # --> find_V
                        # self.return_line()
                        self._motion.walk(dir='FORWARD', loop=1)
                        time.sleep(1)
                        if self.progress_of_roobot[0] != self.mode:
                            self.progress_of_roobot.insert(0, self.mode)
                else: # yellow edge 감지 X 
                    self.mode = 'find_edge' # --> return_line
                    self.find_edge()
                    if self.progress_of_roobot[0] != self.mode:
                        self.progress_of_roobot.insert(0, self.mode)
#------------------------------------------------------------------------------------------------------    
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------



       # elif self.mode == 'return_line':
            #if self.return_head == '55': #
                #if line_info["ALL_Y"][1] <= 100: #
                  #  pass#
                #else:#
                   # self._motion.set_head(dir ='DOWN', angle = 45)#
                  #  self.return_head = '45'#
            #else:#
                #print('self.return_head is empty')#

           # if self.curr_room_color == 'BLACK':
              #  self._motion.set_head(dir='DOWN', angle=35)
              #  if edge_info["EDGE_POS"] != None :
               #     print(self.curr_room_color, edge_info["EDGE_POS"][1])
               #     if edge_info["EDGE_POS"][1] > 450: # yellow edge y 좌표 가까이 O
               #         self._motion.walk(dir='FORWARD', loop=2)
                #        self._motion.grab(switch = False)
                #        self._motion.turn(dir=self.direction, loop = 3)

                #        self.mode = 'find_V' # --> 걸을 직선 찾고 walk

                        # 10/08 수정 전
                        #self.walk_info = None
                        #self.mode = 'walk' ##
                        #self.walk_info = '│'
                        #self._motion.turn(dir=self.direction, loop = 3)
                        
                 #       if self.progress_of_roobot[0] != self.mode:
                 #           self.progress_of_roobot.insert(0, self.mode)
                 #   else: # yellow edge y 좌표 가까이 X
                 #       self.mode = 'return_line' # --> find_V
                 #       self._motion.walk(dir='FORWARD', loop=1, grab=True)
                 #       time.sleep(1)           
                  #      if self.progress_of_roobot[0] != self.mode:
                #            self.progress_of_roobot.insert(0, self.mode)
              #  else: # yellow edge 감지 X
                  #  self._motion.walk(dir='FORWARD', loop=1, grab=True)
                  #  time.sleep(1)
                 #   if self.progress_of_roobot[0] != self.mode:
                  #      self.progress_of_roobot.insert(0, self.mode)

          #  elif self.curr_room_color == 'GREEN':
             #   self._motion.set_head(dir='DOWN', angle=35)
             #   if edge_info["EDGE_POS"] != None :
                 #   if edge_info["EDGE_POS"][1] > 450: # yellow edge y 좌표 가까이 O
                  #      self._motion.walk(dir='FORWARD', loop=2)
                  #      self._motion.grab(switch = False)
                  #      self._motion.turn(dir=self.direction, loop = 3)

                  #      self.mode = 'find_V' # --> 걸을 직선 찾고 walk

                        #self._motion.walk(dir='FORWARD', loop=2)
                        #self._motion.turn(self.direction, 2) ##
                        #self.walk_info = None
                        #self.mode = 'walk' ##
                        #self.walk_info = '│'
                        #self._motion.turn(dir=self.direction, loop = 3)
                        #self._motion.walk(dir='FORWARD', loop=1)
                     #   if self.progress_of_roobot[0] != self.mode:
                    #        self.progress_of_roobot.insert(0, self.mode)
                 #   else: # yellow edge y 좌표 가까이 X
                 #       self.mode = 'return_line' # --> find_V
                        # self.return_line()
                 #       self._motion.walk(dir='FORWARD', loop=1)
                 #       if self.progress_of_roobot[0] != self.mode:
                  #          self.progress_of_roobot.insert(0, self.mode)
             #   else: # yellow edge 감지 X 
                 #   self.mode = 'find_edge' # --> return_line
                 #   self.find_edge()
                 #   if self.progress_of_roobot[0] != self.mode:
                   #     self.progress_of_roobot.insert(0, self.mode)
                    
        elif self.mode == 'find_V':
            if line_info["V"] == True :
                if 300 < line_info["V_X"][0] <340:
                    self._motion.walk(dir='FORWARD', loop=2)
                    time.sleep(1)
                    self.mode = 'walk'
                    self.walk_info = '│'
                else:
                    if line_info["V_X"][0] < 300:
                        self._motion.walk(dir='LEFT', loop=1)
                        time.sleep(1)
                    elif line_info["V_X"][0] > 340:
                        self._motion.walk(dir='RIGHT', loop=1)
                        time.sleep(1)
            else:
                self.mode = 'find_V'
                self._motion.turn(self.direction, 1)
                time.sleep(1)


        # 나가기
        elif self.mode == 'is_finish_line':
            if line_info['H'] == True:
                self.walk(line_info, '│')
                time.sleep(1)
            else: #line_info['H'] == False
                if self.count < 3:
                     self.mode = 'walk'
                     self.walk_info = '│'
                    # self.count += 1 # count 방식 미션 grap_off 기준으로 count하면 좋을 듯 :: 중요
                else:
                    self.mode = 'finish' # --> stop!
                    self._motion.turn(dir=self.direction, loop =5)
                    time.sleep(1)
                    if self.progress_of_roobot[0] != self.mode:
                            self.progress_of_roobot.insert(0, self.mode)

        # 나가기
        elif self.mode == 'finish':
            #self.walk(line_info, '│')
            self.mode = 'walk'
            self.walk_info = '│'
            
        if self.mode_history != self.mode :
            self.mode_history = self.mode
            cv2.destroyAllWindows()