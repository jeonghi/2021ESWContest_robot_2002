from Sensor.ImageProcessor import ImageProcessor
from Sensor.LineDetector import LineDetector
from Actuator.Motion import Motion
import numpy as np
import cv2
import time
import sys
from collections import deque

SAFETY = True

class Controller:
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
        self.line_info, self.edge_info = self.line_tracing()

    def line_tracing(self, line_visualization=False, edge_visualization=False, ROI= False):
        self.line_info, self.edge_info, result = self._image_processor.line_tracing(color=self.color, line_visualization = line_visualization, edge_visualization=edge_visualization, ROI=ROI)
        return self.line_info, self.edge_info

    def detect_direction(self) -> bool:
        self.direction = self._image_processor.get_arrow_direction()
        if self.direction:
            return True
        return False

    def walk(self, line_info, go: bool, open_door=False):
        """
         self.line_info = {
        "DEGREE" : 0,
        "V" : False,
        "V_X" : [0 ,0],
        "V_Y" : [0 ,0],
        "H" : False,
        "H_X" : [0 ,0],
        "H_Y" : [0 ,0]
        }
        """
        if not self.is_grab and self.progress_of_robot[-1] in ['detect_door_alphabet', 'finish']:
            self.is_grab = True
            self._motion.move_arm(dir='HIGH')

        self._motion.set_head(dir='DOWN', angle=10)

        if 85 < self.line_info["DEGREE"] < 95:
            if go:
                if 290 < self.line_info["V_X"][0] < 350:
                    if self.line_info["H"]:
                        self._motion.walk(dir='FORWARD', loop=1, grab=self.is_grab) # 팔뻗기
                    else:
                        self._motion.walk(dir='FORWARD', loop=2, grab=self.is_grab)  # 팔뻗기
                else:
                    if self.line_info["V_X"][0] < 290:
                        self._motion.walk(dir='LEFT', loop=1, grab=self.is_grab) # 팔뻗기
                    elif self.line_info["V_X"][0] > 350:
                        self._motion.walk(dir='RIGHT', loop=1, grab=self.is_grab) # 팔뻗기

        elif 0 < self.line_info["DEGREE"] <= 85:
            print('MODIFY angle --LEFT')
            self._motion.turn(dir='LEFT', loop=1, grab=self.is_grab) # 팔뻗기
       
        elif self.line_info["DEGREE"] == 0 :
            print(self.mode, 'mode walk no line')
            self._motion.walk(dir='BACKWARD')
            time.sleep(1) #뒤로 걷는 거 휘청거려서 sleep 넣음

        else:
            print('MODIFY angle --RIGHT')
            self._motion.turn(dir='RIGHT', loop=1, grab=self.is_grab) # 팔뻗기
        

    def find_edge(self): #find_corner_for_outroom
        if self.curr_room_color == 'BLACK':
            self._motion.turn(dir=self.direction, loop=1, grab=True)  # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
        else:
            if self.direction == 'LEFT':
                if self.box_pos == 'RIGHT':
                    self._motion.turn(dir='LEFT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
                else:
                    self._motion.turn(dir='RIGHT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
            else:
                if self.box_pos == 'LEFT':
                    self._motion.turn(dir='RIGHT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
                else:
                    self._motion.turn(dir='LEFT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
        time.sleep(0.3)

    def catch_box(self):
        self._motion.grab()
        if self.curr_room_color == 'GREEN':
            if self.box_pos == 'RIGHT':
                self._motion.turn(dir='LEFT', loop=4, grab=True)
            elif self.box_pos == 'LEFT':
                self._motion.turn(dir='RIGHT', loop=4, grab=True)
            self._motion.move_arm(dir='LOW')
            self.mode = 'check_area'
        else:
            self._motion.turn(dir=self.direction, loop=4, grab=True)
            self.mode = 'end_mission'
            self.color = 'YELLOW'
        time.sleep(0.5)

    def check_area(self, line_info, edge_info):
        print('self.line_info[H]:', self.line_info["H"], 'self.line_info[H_Y]:', self.line_info["H_Y"])
        if self.box_pos == 'RIGHT':
            if self.line_info["H"]:
                if self.line_info["len(H)"] >= 300:
                    self.mode = 'fit_area'
                else:
                    self._motion.walk(dir='RIGHT', loop=1, wide= True, grab=True)
            else:
                self._motion.turn(dir='LEFT', loop=1, grab=True)
        elif self.box_pos == 'LEFT':
            if self.line_info["H"]:
                if self.line_info["len(H)"] >= 300:
                    self.mode = 'fit_area'
                else:
                    self._motion.walk(dir='LEFT', loop=1, wide= True, grab=True)
            else:
                self._motion.turn(dir='RIGHT', loop=1, grab=True)
        else:
            self.mode = 'fit_area'


    def fit_area(self, line_info, edge_info):
        if self.box_pos == 'RIGHT':
            if self.line_info["ALL_X"][1] > 360:
                if self.line_info["ALL_X"][0] < 200:
                    self._motion.set_head(dir='DOWN', angle=35)
                    time.sleep(0.3)
                    self._motion.move_arm(dir='HIGH')  # 잡은 상태로 팔 앞으로 뻗고 고개 내림
                    self.mode = 'move_into_area'
                else:
                    self._motion.walk(dir='RIGHT', loop=1, wide=True, grab=True)
            else:
                self._motion.walk(dir='RIGHT', loop=1, wide=True, grab=True)
        elif self.box_pos == 'LEFT':
            if self.line_info["ALL_X"][0] < 150:
                if self.line_info["ALL_X"][1] > 480:
                    self._motion.set_head(dir='DOWN', angle=35)
                    time.sleep(0.3)
                    self._motion.move_arm(dir='HIGH')  # 잡은 상태로 팔 앞으로 뻗고 고개 내림
                    self.mode = 'move_into_area'
                else:
                    self._motion.walk(dir='LEFT', wide=True, loop=1)
            else:
                self._motion.walk(dir='LEFT', wide=True, loop=1)
        else:
            self._motion.move_arm(dir='HIGH')  # 잡은 상태로 팔 앞으로 뻗고 고개 내림
            self.mode = 'move_into_area'
        print('self.line_info["ALL_X"][0]:', self.line_info["ALL_X"][0], 'self.line_info["ALL_X"][1]:', self.line_info["ALL_X"][1] )
        time.sleep(0.5)
                
    def move_into_area(self, line_info, edge_info):
        if self.box_pos:
            if self.line_info['ALL_Y'][1] > 460: # 발 나온다는 생각으로 절반 아래에 오면 발 앞이라고 생각할 것임 -- 수정 예정
                self.mode = 'box_into_area'
            else:
                self._motion.walk(dir='FORWARD', loop=1, grab=True)
                time.sleep(1)
        else:
            print("self.box_pos is None, Please check it")

    def box_into_area(self, line_info: tuple, edge_info: tuple):
        self._motion.walk(dir='FORWARD', loop=2, grab=True)
        self._motion.grab(switch=False)
        self.color = 'YELLOW'
        self.count += 1
        
    def start(self):
        self.mode = 'detect_door_alphabet'  # --> walk
    
    def detect_door_alphabet(self):
        self._motion.set_head(dir="DOWN", angle=self.curr_head4door_alphabet[0])
        if self.detect_door_alphabet():
            self._motion.set_head(dir="DOWN", angle=10)
            time.sleep(1)
            self.mode = 'close_to_direction_line'

            time.sleep(0.3)
        else:
            self.curr_head4door_alphabet.rotate(-1)
            
    def close_to_direction_line(self):
        if self.line_info['V']:
            if 85 < self.line_info["DEGREE"] < 95:
                if 290 < self.line_info["V_X"][0] < 350:
                    if self.line_info["H"]:
                        self._motion.basic_form()
                        if self.line_info['H_Y'][1] < 100:
                            print('H랑 멀어서 가까이 다가감', self.line_info['H_Y'][1])
                            self._motion.walk(dir='FORWARD')
                        self._motion.set_head(dir='DOWN', angle=90)
                        time.sleep(1.0)
                        self.mode = 'detect_direction'
                    else:
                        self._motion.walk(dir='FORWARD', loop=2, grab=self.is_grab, open_door = True)  # 팔뻗기
                else:
                    if self.line_info["V_X"][0] < 290:
                        self._motion.walk(dir='LEFT', loop=1, grab=self.is_grab, open_door = True) # 팔뻗기
                    elif self.line_info["V_X"][0] > 350:
                        self._motion.walk(dir='RIGHT', loop=1, grab=self.is_grab, open_door = True) # 팔뻗기

            elif 0 < self.line_info["DEGREE"] <= 85:
                print('MODIFY angle --LEFT')
                self._motion.turn(dir='LEFT', loop=1, grab=self.is_grab, open_door = True) # 팔뻗기

            else:
                print('MODIFY angle --RIGHT')
                self._motion.turn(dir='RIGHT', loop=1, grab=self.is_grab, open_door = True) # 팔뻗기

        elif 0 < self.line_info["DEGREE"] <= 85:
                print('MODIFY angle --LEFT')
                self._motion.turn(dir='LEFT', loop=1, grab=self.is_grab, open_door = True) # 팔뻗기
        else:
            print('MODIFY angle --RIGHT')
            self._motion.turn(dir='RIGHT', loop=1, grab=self.is_grab, open_door = True) # 팔뻗기
    
    def close_to_direction_line(self):
        if self.line_info['V']:
            if 85 < self.line_info["DEGREE"] < 95:
                if 290 < self.line_info["V_X"][0] < 350:
                    if self.line_info["H"]:
                        self._motion.basic_form()
                        if self.line_info['H_Y'][1] < 100:
                            print('H랑 멀어서 가까이 다가감', self.line_info['H_Y'][1])
                            self._motion.walk(dir='FORWARD')
                        self._motion.set_head(dir='DOWN', angle=90)
                        time.sleep(1.0)
                        self.mode = 'detect_direction'
                    else:
                        self._motion.walk(dir='FORWARD', loop=2, grab=self.is_grab, open_door = True)  # 팔뻗기
                else:
                    if self.line_info["V_X"][0] < 290:
                        self._motion.walk(dir='LEFT', loop=1, grab=self.is_grab, open_door = True) # 팔뻗기
                    elif self.line_info["V_X"][0] > 350:
                        self._motion.walk(dir='RIGHT', loop=1, grab=self.is_grab, open_door = True) # 팔뻗기

            elif 0 < self.line_info["DEGREE"] <= 85:
                print('MODIFY angle --LEFT')
                self._motion.turn(dir='LEFT', loop=1, grab=self.is_grab, open_door = True) # 팔뻗기

            else:
                print('MODIFY angle --RIGHT')
                self._motion.turn(dir='RIGHT', loop=1, grab=self.is_grab, open_door = True) # 팔뻗기

        elif 0 < self.line_info["DEGREE"] <= 85:
                print('MODIFY angle --LEFT')
                self._motion.turn(dir='LEFT', loop=1, grab=self.is_grab, open_door = True) # 팔뻗기
        else:
            print('MODIFY angle --RIGHT')
            self._motion.turn(dir='RIGHT', loop=1, grab=self.is_grab, open_door = True) # 팔뻗기
            
    def start_line(self):
        if self.line_info['compact_H']:
            self._motion.open_door(loop = 1)
            self.mode = "entrance"
        else:
            self._motion.turn(dir='LEFT')
    
    def entrance(self):
        if not self.line_info['V']:
            if (self.edge_info['L_Y'][0]< 5 and self.edge_info['L_Y'][0] > 200) or (self.edge_info['R_Y'][0]< 5 and self.edge_info['R_Y'][0] > 200):
                print('입구 빠져 나옴 -- 조정 필요', ', EDGE_R:', self.edge_info['EDGE_R'], ', EDGE_L:', self.edge_info['EDGE_L'])
                self._motion.open_door(loop = 1)
                self._motion.basic_form()
                self._motion.open_door_turn(dir='RIGHT', loop=3)
                self.mode = 'direction_line'
                #self._motion.basic_form()
                #self._motion.turn(dir='SLIDING_RIGHT', loop=2)
                #self.mode = 'direction_line'
            else:
                if self.line_info['H_DEGREE'] > 174 :
                    if 160 <= self.line_info['H_Y'][1] < 250:
                        print('입구 빠져 나가는 중', 'H:', self.line_info['H'], self.line_info['H_Y'][1])
                        self._motion.open_door(loop = 1)
                    elif self.line_info['H_Y'][1] < 160:
                        print('입구 빠져 나가는 중 - H 멀어서 가까이 다가감', self.line_info['H'], self.line_info['H_Y'][1])
                        self._motion.open_door_walk(dir='FORWARD') # 수정 완료
                    else: # H가 너무 가깝다는 것, H 업다는 것
                        print('입구 빠져 나가는 중 - H 가까워서 한발자국 뒤로', self.line_info['H'], self.line_info['H_Y'][1])
                        self._motion.open_door_walk(dir='BACKWARD') # 수정 완료
                        print('entrance :: H is so closed')
                        time.sleep(1) #뒤로 가는 거 휘청거려서 넣음
                else:
                    print('H:', self.line_info['H_DEGREE'], ', EDGE_R:', self.edge_info['EDGE_R'], ', EDGE_L:', self.edge_info['EDGE_L'])
                    if self.edge_info['EDGE_R']:
                        self._motion.open_door_turn(dir='LEFT')
                    elif self.edge_info['EDGE_L']:
                        self._motion.open_door_turn(dir='RIGHT')
                    else:
                        self._motion.open_door_walk(dir='BACKWARD')
                        print('No H')
        else:
            print('입구 빠져 나옴', 'V:', self.line_info['V'], self.line_info["V_X"])
            #if self.line_info["V_X"][1] > 550:
            self._motion.open_door(loop = 1)
            self._motion.open_door_turn(dir='RIGHT', loop=4)
            self._motion.basic_form()
            self.mode = 'direction_line'
            #self._motion.basic_form()
            #self._motion.turn(dir='SLIDING_RIGHT', loop=4)
            #self.mode = 'direction_line'
            
    def direction_line(self):
        if self.line_info['compact_H']:
            #self._motion.basic_form()
            
            if self.line_info['H_Y'][1] < 100:
                print('H랑 멀어서 가까이 다가감', self.line_info['H_Y'][1])
                self._motion.walk(dir='FORWARD')
                
            print('H 앞에 정지', self.line_info['H_DEGREE'])
            print('만약 H 앞이 아닌데 detect_direction 하면 기본 돌기 횟수 수정 필요 --윗줄 print문 중에 조정필요라 떴으면 378번줄, 안 떴으면 407번줄')
            
            self._motion.set_head(dir='DOWN', angle=90)
            time.sleep(1.2)
            self.mode = 'detect_direction'
        else:
            print('H 찾는 중', self.line_info['H_DEGREE'])
            self._motion.turn(dir='RIGHT')
    
    def detect_direction(self):
        if self.detect_direction():
            self._motion.set_head(dir='DOWN', angle=10)
            time.sleep(0.3)
            # if self.line_info['DEGREE'] != 0:
            # self.walk(self.line_info, True)
            # else:
            self._motion.walk('FORWARD', 2)  # 너무 뒤에서 멈추면 추가
            self._motion.walk(self.direction, wide= True, loop = 4)
            self._motion.turn(self.direction, sliding= True, loop = 4)
            self.mode = 'walk'
            self.walk_info = '│'
        else:
            self._motion.walk("BACKWARD", 1)
            print('detect direction is failed')
            time.sleep(0.5)
        
    def walk(self):
        self._motion.set_head(dir='DOWN', angle=10)
        #time.sleep(0.3)

        if self.walk_info in ['┐', '┌']:  # 코너에서
            if self.line_info["H"]:
                #if self.line_info["H_Y"][1] > 90:  # 라인이 감지는 되는데 좀 위에 있으면 전진하고 방향 정보에 맞춰 모드 바꿔줌
                #self._motion.walk("FORWARD", 2)
                if self.walk_info == '┌':
                    if self.direction == 'RIGHT':
                        self.mode = 'is_finish_line'
                    else:
                        self.mode = 'start_mission'
                else:
                    if self.direction == 'RIGHT':
                        self.mode = 'start_mission'
                    else:
                        self.mode = 'is_finish_line'
                #else:
                    #self.walk(self.line_info, True)
            else:  # 코너인데 라인 정보 감지가 안되면 멈춰야하는거 아닌가?
                self.walk(self.line_info, True)

        else:  # 직진하면 그렇게 만들 수 있게
            if self.line_info["H"]:
                if np.mean(self.line_info["H_X"]) < 320:
                    self.walk_info = '┐'
                else:
                    self.walk_info = '┌'
            else:
                if self.line_info["V"]:
                    self.walk_info = '│'  # go
                    self.walk(self.line_info, True)
                else:
                    self.walk_info = None  # modify_angle
                    self.walk(self.line_info, False)
        #time.sleep(0.3)
    
    def start_mission(self):
        if self.line_info['H_Y'][1] < 50:
            self.walk(self.line_info, True)
        else:
            self._motion.walk(dir='FORWARD', loop = 2)
            self._motion.set_head(dir=self.direction, angle=45)
            self._motion.set_head(dir="DOWN", angle=45)
            time.sleep(0.5)
            if self.recognize_area_color():
                self.mode = 'detect_room_alphabet'
            self._motion.set_head(dir="LEFTRIGHT_CENTER")
            time.sleep(0.2)
            
    def detect_room_alphabet(self):
        self._motion.set_head("DOWN", angle=self.curr_head4room_alphabet[0])
        if self.detect_room_alphabet(edge_info=self.edge_info):
            print(f"현재 지역은 {self.curr_room_color}, 방 이름은 {self.alphabet}, 목표 색상은 {self.alphabet_color}")
            self.mode = "find_box"
            
            # 감염지역일때는 빠른 탐색을 위해 45도 정도 미리 몸을 틀어준다.
            if self.curr_room_color == 'BLACK':
                self.black_room.append(self.alphabet)
                self._motion.turn(dir=self.direction, loop=5)
                time.sleep(1)
        else:
            self.curr_head4room_alphabet.rotate(-1)
            print("방 이름 감지 실패")
            
    def find_box(self):
        self._motion.set_head("DOWN", self.curr_head4box[0])
        box_info = self._image_processor.get_milk_info(visualization=False, color=self.alphabet_color, edge_info = self.edge_info)
        if box_info:
            self.mode = "track_box"
            if self.curr_room_color == "GREEN":
                self.update_box_pos(edge_info=self.edge_info, box_info=box_info)
                print(f"BOX POS -> {self.box_pos}")
            
        else:
            if self.curr_head4box[0] == 35:
                if self.curr_room_color == "GREEN":
                    self._motion.turn(dir=self.direction, loop=4)
                else:
                    self._motion.turn(dir=self.direction, loop=2)
            self.curr_head4box.rotate(-1)
            
    def track_box(self):
        self._motion.set_head("DOWN", self.curr_head4box[0])
        box_info = self._image_processor.get_milk_info(visualization=False, color=self.alphabet_color, edge_info=self.edge_info)
        if box_info:
            (cx, cy) = box_info
            (dx, dy) = self.get_distance_from_baseline(box_info=box_info)


            if dy > 10:  # 기준선 보다 위에 있다면
                if -40 <= dx <= 40:
                    print("기준점에서 적정범위. 전진 전진")
                    if self.curr_head4box[0] == 75:
                        self._motion.walk(dir='FORWARD', loop=2)
                    else:
                        self._motion.walk(dir='FORWARD', loop=1)
                elif dx <= -90:
                    if self.curr_head4box[0] == 75:
                        self._motion.turn(dir='RIGHT', sleep=0.1, loop=2)
                    else:
                        self._motion.walk(dir='RIGHT', loop=1)
                elif -90 < dx <= -50:  # 오른쪽
                    print("기준점에서 오른쪽으로 많이 치우침. 조정한다")
                    if self.curr_head4box[0] == 75:
                        self._motion.walk(dir='RIGHT', loop=2)
                    else:
                        self._motion.walk(dir='RIGHT', loop=2)
                elif -50 < dx < -40:
                    if self.curr_head4box[0] == 75:
                        self._motion.walk(dir='RIGHT', loop=1)
                    else:
                        self._motion.walk(dir='RIGHT', loop=1)
                    print("기준점에서 오른쪽으로 치우침. 조정한다")
                elif 90 > dx >= 50:  # 왼쪽
                    print("기준점에서 왼쪽으로 많이 치우침. 조정한다")
                    if self.curr_head4box[0] == 75:
                        self._motion.walk(dir='LEFT', loop=2)
                    else:
                        self._motion.walk(dir='LEFT', loop=2)
                elif 50 > dx > 40:  # 왼쪽
                    print("기준점에서 왼쪽으로 치우침. 조정한다")
                    if self.curr_head4box[0] == 75:
                        self._motion.walk(dir='LEFT', loop=1)
                    else:
                        self._motion.walk(dir='LEFT', loop=2)

                elif dx >= 90:
                    if self.curr_head4box[0] == 75:
                        self._motion.turn(dir='LEFT', sleep=0.1, loop=2)
                    else:
                        self._motion.walk(dir='LEFT',loop=1)

            else:
                if self.curr_head4box[0] == 35:
                    self._motion.grab(switch=True)
                    if self.curr_room_color == "GREEN":
                        self.turn_to_green_area_after_box_tracking()
                    else:
                        self.turn_to_black_area_after_box_tracking()
                else:
                    self.curr_head4box.rotate(-1)
        else:
            self.mode = 'find_box'
        
    def catch_box(self):
        self.catch_box()
        
    def check_area(self):
        self.check_area(self.line_info, self.edge_info)
    
    def fit_area(self):
        self.fit_area(self.line_info, self.edge_info)
        
    def move_into_area(self):
        self.move_into_area(self.line_info, self.edge_info)
        
    def box_into_area(self):
        self.box_into_area(self.line_info, self.edge_info)
        
        if self.box_pos == 'LEFT':
            self._motion.turn(dir='RIGHT', sliding= True, wide=True, loop=4)
        elif self.box_pos == 'RIGHT':
            self._motion.turn(dir='LEFT', sliding= True, wide=True, loop=4)
            
        if self.curr_room_color == 'BLACK':
            self._motion.turn(dir=self.direction, sliding= True, wide=True, loop=6)
            
        self.mode = 'end_mission'
        self.color = 'YELLOW'
    
    def end_mission(self):
        self._motion.set_head(dir='DOWN', angle=60)
        time.sleep(0.2)

        if self.curr_room_color == 'GREEN':
            if self.box_pos == 'RIGHT':
                if self.line_info["ALL_X"][1] > 340:
                    if self.line_info["ALL_Y"][1] < 200 : # yellow 감지
                        self._motion.set_head(dir='DOWN', angle=60)
                        self.return_head = '60'
                        print(self.mode, ': 노란 색 영역 적음 -> 고개 ', self.return_head, '로 진행')
                    else:
                        self._motion.set_head(dir='DOWN', angle=45)
                        self.return_head = '45'
                        print(self.mode, ': 노란 색 영역 넓음 -> 고개 ', self.return_head, '로 진행')
                    self.mode = 'find_edge'
                else:
                    if self.curr_room_color == 'BLACK':
                        self._motion.turn(dir=self.direction, loop=1, grab=True)
                    else:
                        self._motion.turn(dir='LEFT', loop=1)
            else:
                if self.line_info["ALL_X"][0] < 300:
                    if self.line_info["ALL_Y"][1] < 215 : # yellow 감지
                        self._motion.set_head(dir='DOWN', angle=60)
                        self.return_head = '60'
                        print(self.line_info["ALL_Y"][1], self.mode, ': 노란 색 영역 적음 -> 고개 ', self.return_head, '로 진행')
                    else:
                        self._motion.set_head(dir='DOWN', angle=45)
                        self.return_head = '45'
                        print(self.line_info["ALL_Y"][1], self.mode, ': 노란 색 영역 넓음 -> 고개 ', self.return_head, '로 진행')
                    self.mode = 'find_edge'

                else:
                    if self.curr_room_color == 'BLACK':
                        self._motion.turn(dir=self.direction, loop=1, grab=True)
                    else:
                        self._motion.turn(dir='RIGHT', loop=1)
        else:
            if (self.direction == 'RIGHT' and 0 < self.line_info["ALL_X"][0] < 300) or (self.direction == 'LEFT' and self.line_info["ALL_X"][1] > 340):
                if self.direction == 'RIGHT':
                    print('영역 충분히 보이는 시점: ', self.direction, '으로 돌다가 왼쪽 끝 ', self.line_info["ALL_X"][0] ,' 에 닿음')
                else:
                    print('영역 충분히 보이는 시점: ', self.direction, '으로 돌다가 오른쪽 끝 ', self.line_info["ALL_X"][1] ,' 에 닿음')
                if self.line_info["ALL_Y"][1] < 215 :  # yellow 감지
                    self._motion.set_head(dir='DOWN', angle=60)
                    self.return_head = '60'
                    print(self.mode, ': 노란 색 영역 적음 -> 고개 ', self.return_head, '로 진행')
                else:
                    self._motion.set_head(dir='DOWN', angle=45)
                    self.return_head = '45'
                    print(self.mode, ': 노란 색 영역 넓음 -> 고개 ', self.return_head, '로 진행')
                self.mode = 'find_edge'
            else:
                if self.curr_room_color == 'BLACK':
                    self._motion.turn(dir=self.direction, loop=1, grab=True)
                else:
                    self._motion.turn(dir='RIGHT', loop=1)
        #time.sleep(1)
    
    def find_edge(self):
        if self.edge_info["EDGE_POS"]: # yellow edge 감지
            if 280 < self.edge_info["EDGE_POS"][0] < 360 : # yellow edge x 좌표 중앙 O # 360
                print('yellow edge 중앙 O --> ', self.edge_info["EDGE_POS"][0])
                self.mode = 'return_line'# --> find_corner
            else: # yellow edge 중앙 X
                print('yellow edge 감지 중앙 X --> ', self.edge_info["EDGE_POS"][0])
                self.find_edge()

        else: # yellow edge 감지 X
            if self.line_info['DEGREE'] == 0 :
                print('yellow edge 감지 X --만약 edge 중앙인데', 'self.line_info[DEGREE]:', '가 0이면 노란 선이 존재하지 않음 return_head 값 높여주기')
            else:
                print('yellow edge 감지 X ','edge 중앙 값 다시 설정 필요함')
            self.mode = 'find_edge'# --> find_edge
            self.find_edge()
            
    def return_line(self):
        if self.return_head == '60':
            if self.line_info["ALL_Y"][1] >= 215 :
                self._motion.set_head(dir='DOWN', angle=45)
                self.return_head = '45'
                print(self.mode, ': 노란 색 영역 넓음 -> 고개 ', self.return_head, '로 진행')
                time.sleep(0.3)
                    
        elif self.return_head == '45':
            if self.line_info["ALL_Y"][1] >= 215 :
                self._motion.set_head(dir='DOWN', angle=35)
                self.return_head = '35'
                print(self.mode, ': 노란 색 영역 넓음 -> 고개 ', self.return_head, '로 진행')
                time.sleep(0.3)
        
        if self.curr_room_color == 'BLACK':
            if self.edge_info["EDGE_POS"]:
                print('self.edge_info[EDGE_POS][1]', self.edge_info["EDGE_POS"][1])
                if self.count < 3 and SAFETY :
                    if self.line_info["ALL_Y"][1] > 300:
                        self._motion.grab(switch=False)
                        self.count += 1
                        self._motion.walk(dir='FORWARD', loop=1)
                        self._motion.walk(dir=self.direction, wide= True, loop=2)
                        #if self.direction == 'LEFT':
                            #self._motion.turn(dir='RIGHT', sliding=True, loop=1)
                        #else:
                            #self._motion.turn(dir='LEFT', sliding=True, loop=1)
                        self._motion.set_head(dir='DOWN', angle=10)
                        time.sleep(0.5)
                        self.mode = 'find_corner'
                        time.sleep(0.3)
                    else:  
                        self._motion.walk(dir='FORWARD', loop=1, grab=True)
                    
                else:
                    if self.edge_info["EDGE_POS"][1] > 450:  # yellow edge y 좌표 가까이 O
                        self._motion.grab(switch=False)
                        self.count += 1
                        self._motion.turn(dir=self.direction, loop=1)
                        self.mode = 'find_corner'  # --> 걸을 직선 찾고 walk
                        time.sleep(0.3)
                    else:  # yellow edge y 좌표 가까이 X
                        self._motion.walk(dir='FORWARD', loop=1, grab=True)

        elif self.curr_room_color == 'GREEN':
            if self.edge_info["EDGE_POS"]:
                print('self.edge_info[EDGE_POS][1]', self.edge_info["EDGE_POS"][1])
                if self.count < 3 and SAFETY :
                    if self.line_info["ALL_Y"][1] > 300:
                        self._motion.walk(dir='FORWARD', loop=1)
                        self._motion.walk(dir=self.direction, wide= True, loop=2)
                        #if self.direction == 'LEFT':
                            #self._motion.turn(dir='RIGHT', sliding=True, loop=1)
                        #else:
                            #self._motion.turn(dir='LEFT', sliding=True, loop=1)
                        self._motion.set_head(dir='DOWN', angle=10)
                        time.sleep(0.5)
                        self.mode = 'find_corner'
                        time.sleep(0.3)
                    else: 
                        self._motion.walk(dir='FORWARD', loop=1)
                    
                else:
                    if self.edge_info["EDGE_POS"][1] > 450:  # yellow edge y 좌표 가까이 O
                        self._motion.walk(dir='FORWARD', loop=1)
                        self._motion.turn(dir=self.direction, loop=1)
                        self.mode = 'find_corner'  # --> 걸을 직선 찾고 walk
                        time.sleep(0.3)
                    else: # yellow edge y 좌표 가까이 X
                        self._motion.walk(dir='FORWARD', loop=1)

            else: # yellow edge 감지 X 
                self.mode = 'find_edge'  # --> return_line
                self.find_edge()
                
    def find_corner(self):
        if self.count < 3 and SAFETY :
            if self.line_info["H"]:
                self._motion.walk(dir=self.direction, wide= True, loop =4)
                self.mode = 'mission_line'
            else:
                if self.direction == 'LEFT':
                    self._motion.turn(dir='RIGHT', loop=1)
                else:
                    self._motion.turn(dir='LEFT', loop=1)
                time.sleep(0.3)
        else:
            if self.line_info["V"]:
                if 300 < self.line_info["V_X"][0] < 340:
                    self._motion.walk(dir='FORWARD', loop=2)
                    self.mode = 'walk'
                    self.walk_info = '│'
                elif self.line_info["V_X"][0] <= 300:
                    self._motion.walk(dir='LEFT', loop=1)
                else:
                    self._motion.walk(dir='RIGHT', loop=1)
            else:
                self._motion.turn(self.direction, 1)
                
    def mission_line(self):
        if self.line_info['compact_H']:
            if 170 <= self.line_info['H_Y'][1] < 250:
                print('입구 빠져 나가는 중', 'H:', self.line_info['H'], self.line_info['H_Y'][1])
        
                if self.line_info['V'] and self.line_info['H_X'][0] > 50:
                    self._motion.turn(self.direction, sliding= True, wide = True, loop = 3)
                    self.mode = 'walk'
                    self.walk_info = '│'
                else:
                    self._motion.walk(self.direction, wide= True, loop = 4)
                    
            elif self.line_info['H_Y'][1] < 170:
                print('입구 빠져 나가는 중 - H 멀어서 가까이 다가감', self.line_info['H'], self.line_info['H_Y'][1])
                self._motion.open_door_walk(dir='FORWARD') # 수정 완료
            else: # H가 너무 가깝다는 것, H 업다는 것
                print('입구 빠져 나가는 중 - H 가까워서 한발자국 뒤로', self.line_info['H'], self.line_info['H_Y'][1])
                self._motion.open_door_walk(dir='BACKWARD') # 수정 완료
                print('entrance :: H is so closed')
                time.sleep(1) #뒤로 가는 거 휘청거려서 넣음
        else:
            print('H:', self.line_info['H'], ', EDGE_R:', self.edge_info['EDGE_R'], ', EDGE_L:', self.edge_info['EDGE_L'])
            if self.edge_info['EDGE_R']:
                self._motion.open_door_turn(dir='LEFT')
            elif self.edge_info['EDGE_L']:
                self._motion.open_door_turn(dir='RIGHT')
            else:
                self._motion.open_door_walk(dir='BACKWARD')
                print('No H')
                
    def is_finish_line(self):
        if self.count < 3 and SAFETY:
            if self.line_info["H"]:
                self._motion.walk(dir='FORWARD')
            else:
                self.mode = 'walk'
                self.walk_info = '│'
        else:
            #self._motion.walk(dir='FORWARD')
            self.mode = 'finish'
            
    def finish(self):
        if self.direction == 'LEFT':
            self._motion.open_door(dir='LEFT', loop=15)
            print("left")
        else:
            self._motion.open_door(loop=15)
            print("right")
        self.mode = 'finish_notice'
        
    def finish_notice(self):
        if self.black_room:
            self._motion.notice_alpha(self.black_room)
            self.black_room.clear()
            return 0
        
    def run(self, in_method = 2):
        # in_method == 1 : 옆으로 걷기
        # in_method == 2 : 앞으로 걷기
        if self.mode_history != self.mode:
            if self.mode != 'walk':
                self.progress_of_robot.append(self.mode_history)
            self.mode_history = self.mode
            cv2.destroyAllWindows()