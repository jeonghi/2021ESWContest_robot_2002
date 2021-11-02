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
        self.loop_90 = 4
        self.loop_135 = 6
        self.loop_180 = 8
        # "start"("detect_room_alphabet") , "walk", "detect_direction", "start_mission",
        #self.mode = "catch_box"
        #self.direction = "LEFT" # "LEFT", "RIGHT"
        #self.color = "GREEN" # 노란색, 검정색, 초록색
        #self.box_pos = "LEFT"
        #self.curr_room_color = "GREEN"


        #self.mode = "detect_direction"
        #self.direction = None
        #self.color = "YELLOW"
        #self.box_pos = ""
        #self.curr_room_color =""
    
        #self.mode = "walk"
        #self.direction = "LEFT"
        #self.color = "YELLOW"
        #self.box_pos = None
        #self.curr_room_color = None
        #self.alphabet_color = None
        #self.alphabet = None
        #self.black_room = ["A", "C"]
        #self.count = 2
        
        #self.mode = 'start_mission'
        #self.direction = 'LEFT'
        #self.color = "GREEN"
        #self.box_pos = None
        #self.curr_room_color = "GREEN"

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
    def test(self):
        self._motion.turn(dir='LEFT', loop=4, grab=True)
    
    def reset_room_var(self):
        self.curr_room_color = None
        self.alphabet = None
        self.alphabet_color = None
        self.box_pos = None

    def set_basic_form(self):
        self._motion.basic_form()
        self.is_grab = False
        self.cube_grabbed = False

    def get_distance_from_baseline(self, box_info, baseline=(320, 370)):
        """
        :param box_info: 우유팩 위치 정보를 tuple 형태로 받아온다. 우유팩 영역 중심 x좌표와 y좌표 순서
        :param baseline: 우유팩 위치 정보와 비교할 기준점이다.
        :return: 우유팩이 지정한 기준점으로부터 떨어진 상대적 거리를 tuple로 반환한다.
        """
        (bx, by) = baseline
        (cx, cy) = box_info
        return (bx-cx, by-cy)

    def detect_door_alphabet(self) -> bool:
        """
        :return: 인식된 알파벳 정보가 있다면 성공(True), 없다면 실패(False)
        """
        self.alphabet = self._image_processor.get_door_alphabet()
        if self.alphabet:
            print("alphabet:", self.alphabet)
            self._motion.notice_direction(dir=self.alphabet)
            return True
        return False
    
    def update_box_pos(self, edge_info: dict, box_info: tuple):
        if edge_info["EDGE_DOWN"]:
            center_x = 320
            (cor_x, cor_y) = (edge_info["EDGE_DOWN_X"], edge_info["EDGE_DOWN_Y"])
            (box_x, box_y) = box_info
            dx = 30
            if cor_x - dx <= box_x <= cor_x + dx:
                
                self.box_pos = "MIDDLE"
                
                #if box_x <= cor_x :
                #    self.box_pos = "LEFT"
                #else:
                #    self.box_pos = "RIGHT"
            elif box_x < cor_x - dx :
                self.box_pos = "LEFT"
            else:
                self.box_pos = "RIGHT"
        elif self.direction == "RIGHT":
            self.box_pos = "LEFT"
        else:
            self.box_pos = "RIGHT"

    def detect_room_alphabet(self, edge_info) -> bool:
        """
        :param edge_info: 방 미션 지역의 경계선 정보로, 알파벳 인식 함수에서 필터링을 위한 정보로 사용된다.
        :return: 인식된 방 알파벳 정보가 있다면 성공(True), 없다면 실패(False)
        """
        alphabet_info = self._image_processor.get_alphabet_info4room(method="CONTOUR", edge_info=edge_info)
        if alphabet_info:
            self.alphabet_color, self.alphabet = alphabet_info
            return True
        return False

    def recognize_area_color(self) -> bool:
        time.sleep(1)
        self.color = 'GREEN'
        line_info, edge_info = self.line_tracing(line_visualization=False, edge_visualization=True)
        if edge_info['EDGE_DOWN']:
            self.curr_room_color = 'GREEN'
        else:
            self.curr_room_color = 'BLACK'

        if self.curr_room_color:
            self._motion.notice_area(area=self.curr_room_color)
            self.color = self.curr_room_color
            return True

        return False

    def line_tracing(self, line_visualization=False, edge_visualization=False, ROI= False):
        line_info, edge_info, result = self._image_processor.line_tracing(color=self.color, line_visualization = line_visualization, edge_visualization=edge_visualization, ROI=ROI)
        return line_info, edge_info

    def detect_direction(self) -> bool:
        self.direction = self._image_processor.get_arrow_direction()
        if self.direction:
            return True
        return False

    def turn_to_green_area_after_box_tracking(self) -> None:

        if self.box_pos == 'RIGHT':
                self._motion.turn(dir='LEFT', loop=self.loop_90, wide=True, sliding = True, grab=True)
        elif self.box_pos == 'LEFT':
            self._motion.turn(dir='RIGHT', loop=self.loop_90, wide=True, sliding = True, grab=True)

        self._motion.move_arm(dir='LOW')
        
        self.mode = 'check_area'

    def turn_to_black_area_after_box_tracking(self) -> None:
        self._motion.turn(dir=self.direction, loop=7, grab=True)
        # time.sleep(1)
        self.mode = 'end_mission'
        self.color = 'YELLOW'

    def walk(self, line_info, go: bool):
        """
         line_info = {
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

        if 85 < line_info["DEGREE"] < 95:
            if go:
                if 290 < line_info["V_X"][0] < 350:
                    if line_info["H"]:
                        self._motion.walk(dir='FORWARD', loop=1, grab=self.is_grab) # 팔뻗기
                    else:
                        self._motion.walk(dir='FORWARD', loop=2, grab=self.is_grab)  # 팔뻗기
                else:
                    if line_info["V_X"][0] < 290:
                        self._motion.walk(dir='LEFT', loop=1, wide=True, grab=self.is_grab) # 팔뻗기
                    elif line_info["V_X"][0] > 350:
                        self._motion.walk(dir='RIGHT', loop=1, wide=True, grab=self.is_grab) # 팔뻗기

        elif 0 < line_info["DEGREE"] <= 85:
            print('MODIFY angle --LEFT')
            self._motion.turn(dir='LEFT', loop=1, grab=self.is_grab) # 팔뻗기
       
        elif line_info["DEGREE"] == 0 :
            self._motion.walk(dir='BACKWARD')
            time.sleep(1) #뒤로 걷는 거 휘청거려서 sleep 넣음

        else:
            print('MODIFY angle --RIGHT')
            self._motion.turn(dir='RIGHT', loop=1, grab=self.is_grab) # 팔뻗기
        time.sleep(0.3)

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
                self._motion.turn(dir='LEFT', loop=self.loop_90, wide=True, sliding = True, grab=True)
            elif self.box_pos == 'LEFT':
                self._motion.turn(dir='RIGHT', loop=self.loop_90, wide=True, sliding = True, grab=True)
            self._motion.move_arm(dir='LOW')
            self.mode = 'check_area'
        else:
            self._motion.turn(dir=self.direction, loop=4, grab=True)
            self.mode = 'end_mission'
            self.color = 'YELLOW'
        time.sleep(0.5)

    def check_area(self, line_info, edge_info):
        print('line_info[H]:', line_info["H"], 'line_info[H_Y]:', line_info["H_Y"])
        if self.box_pos == 'RIGHT':
            if line_info["H"] and line_info["H_Y"][1] < 350:
                self.mode = 'fit_area'
            else:
                self._motion.turn(dir='LEFT', loop=1, grab=True)
        elif self.box_pos == 'LEFT':
            if line_info["H"] and line_info["H_Y"][1] < 350:
                self.mode = 'fit_area'
            else:
                self._motion.turn(dir='RIGHT', loop=1, grab=True)
        else:
            self.mode = 'fit_area'
        time.sleep(0.5)

    def fit_area(self, line_info, edge_info):
        if self.box_pos == 'RIGHT':
            if line_info["ALL_X"][1] > 360:
                if line_info["ALL_X"][0] < 200:
                    self._motion.set_head(dir='DOWN', angle=35)
                    time.sleep(0.3)
                    self._motion.move_arm(dir='HIGH')  # 잡은 상태로 팔 앞으로 뻗고 고개 내림
                    self.mode = 'move_into_area'
                else:
                    self._motion.walk(dir='RIGHT', loop=1, grab=True)
            else:
                self._motion.walk(dir='RIGHT', loop=1, grab=True)
        elif self.box_pos == 'LEFT':
            if line_info["ALL_X"][0] < 150:
                if line_info["ALL_X"][1] > 480:
                    self._motion.set_head(dir='DOWN', angle=35)
                    time.sleep(0.3)
                    self._motion.move_arm(dir='HIGH')  # 잡은 상태로 팔 앞으로 뻗고 고개 내림
                    self.mode = 'move_into_area'
                else:
                    self._motion.walk(dir='LEFT', loop=1)
            else:
                self._motion.walk(dir='LEFT', loop=1)
        else:
            self._motion.move_arm(dir='HIGH')  # 잡은 상태로 팔 앞으로 뻗고 고개 내림
            self.mode = 'move_into_area'
        print('line_info["ALL_X"][0]:', line_info["ALL_X"][0], 'line_info["ALL_X"][1]:', line_info["ALL_X"][1] )
        time.sleep(0.5)
                
    def move_into_area(self, line_info, edge_info):
        if self.box_pos:
            if line_info['ALL_Y'][1] > 460: # 발 나온다는 생각으로 절반 아래에 오면 발 앞이라고 생각할 것임 -- 수정 예정
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

    def run(self):

        if self.mode_history != self.mode:
            if self.mode != 'walk':
                self.progress_of_robot.append(self.mode_history)
            self.mode_history = self.mode
            cv2.destroyAllWindows()
            
        if self.mode == 'walk' and self.count < 3:
            line_info, edge_info = self.line_tracing(line_visualization=False, edge_visualization=False, ROI= False)
        else:
            if self.DEBUG:
                print(self.mode, self.walk_info)
                if self.color == 'YELLOW':
                    line_info, edge_info = self.line_tracing(line_visualization=False, edge_visualization=False)
                elif self.color == 'GREEN':
                    line_info, edge_info = self.line_tracing(line_visualization=False, edge_visualization=False)
                else:
                    line_info, edge_info = self.line_tracing()
            else:
                line_info, edge_info = self.line_tracing()

        # 0) 시작
        if self.mode in ['start'] :
            self.mode = 'detect_door_alphabet'  # --> walk

        # 1) 방위 인식 --> 성공시 2) 라인트레이싱
        elif self.mode in ['detect_door_alphabet']:
            self._motion.set_head(dir="DOWN", angle=self.curr_head4door_alphabet[0])
            if self.detect_door_alphabet():
                self._motion.set_head(dir="DOWN", angle=10)
                self._motion.walk(dir='FORWARD', loop=2)
                self._motion.walk(dir='RIGHT', wide=True, loop=1)
                self._motion.turn(dir='LEFT', loop=4, sliding= True)
                self.mode = "start_line"
                time.sleep(0.3)
            else:
                self.curr_head4door_alphabet.rotate(-1)
                
        elif self.mode in ['start_line']:
            if line_info['H_DEGREE'] > 174:
                if 150 <= line_info['H_Y'][1] < 250:
                    self.mode = 'entrance'
                elif line_info['H_Y'][1] < 150:
                    print('입구 빠져 나가는 중 - H 멀어서 가까이 다가감', line_info['H'], line_info['H_Y'][1])
                    self._motion.open_door_walk(dir='FORWARD')
                else:
                    print('입구 빠져 나가는 중 - H 가까워서 한발자국 뒤로', line_info['H'], line_info['H_Y'][1])
                    self._motion.open_door_walk(dir='BACKWARD')
                    time.sleep(1)
            else:
                print('H_DEGREE:', line_info['H_DEGREE'], ', EDGE_R:', edge_info['EDGE_R'], ', EDGE_L:', edge_info['EDGE_L'])
                if edge_info['EDGE_R']:
                    self._motion.open_door_turn(dir='LEFT', sliding = True)
                elif edge_info['EDGE_L']:
                    self._motion.open_door_turn(dir='RIGHT', sliding = True)
                else:
                    print('else 걸림 1')
        
        elif self.mode in ['entrance']:
            if not line_info['V']:
                if (edge_info['L_Y'][0]< 5 and edge_info['L_Y'][0] > 200) or (edge_info['R_Y'][0]< 5 and edge_info['R_Y'][0] > 200):
                    print('입구 빠져 나옴 -- 조정 필요', ', EDGE_R:', edge_info['EDGE_R'], ', EDGE_L:', edge_info['EDGE_L'])
                    self._motion.open_door_turn(dir='RIGHT', loop=3, sliding = True)
                    self.mode = 'direction_line'
                else:
                    self._motion.open_door(dir = 'RIGHT', loop = 1)
            else:
                print('입구 빠져 나옴', 'V:', line_info['V'], line_info["V_X"])
                self._motion.open_door_turn(dir='RIGHT', loop=4)
                self.mode = 'direction_line'

        elif self.mode in ['direction_line']:
            if line_info['H_DEGREE'] > 174:
                self._motion.basic_form()
                print('line_info[H_DEGREE]: ', line_info['H_DEGREE'])
                
                if line_info['H_Y'][1] < 100:
                    print('H랑 멀어서 가까이 다가감', line_info['H_Y'][1])
                    self._motion.walk(dir='FORWARD')
                    
                print('H 앞에 정지', line_info['H_DEGREE'])
                print('만약 H 앞이 아닌데 detect_direction 하면 기본 돌기 횟수 수정 필요 --윗줄 print문 중에 조정필요라 떴으면 378번줄, 안 떴으면 407번줄')
                
                self._motion.set_head(dir='DOWN', angle=90)
                time.sleep(1.2)
                self.mode = 'detect_direction'
            else:
                print('H 찾는 중', line_info['H_DEGREE'])
                self._motion.open_door_turn(dir='RIGHT')
                
        # 3) 화살표 방향 인식
        elif self.mode in ['detect_direction']:
            if self.detect_direction():
                self._motion.set_head(dir='DOWN', angle=10)
                time.sleep(0.3)
                self._motion.walk('FORWARD', 2)  # 너무 뒤에서 멈추면 추가
                self._motion.walk(self.direction, wide= True, loop = 5)
                self._motion.turn(self.direction, sliding= True, loop = self.loop_90)
                self.mode = 'mission_line'
            else:
                self._motion.walk("BACKWARD", 1)
                time.sleep(0.5)
        
        elif self.mode in ['mission_line']:
            if line_info['V'] and line_info['V_X'][1] > 300 :
                if line_info['H']:
                    if line_info['H_DEGREE'] > 174:
                        self.mode = 'start_mission'
                    else:
                        self._motion.turn(self.direction)
                else:
                    self._motion.walk(dir='BACKWARD')
                    
                print('line_info[H_DEGREE]: ', line_info['H_DEGREE'])
                self._motion.turn(self.direction, sliding= True, wide=True, loop = self.loop_90)
                self.mode = 'start_mission'
            else:
                self._motion.walk(self.direction, wide= True, sliding = True, loop = 1)
                

        elif self.mode in ['start_mission']:
            self._motion.set_head(dir=self.direction, angle=45)
            self._motion.set_head(dir="DOWN", angle=45)
            time.sleep(0.5)
            if self.recognize_area_color():
                self.mode = 'detect_room_alphabet'
            self._motion.set_head(dir="LEFTRIGHT_CENTER")
            time.sleep(0.2)

        elif self.mode in ['detect_room_alphabet']:
            self._motion.set_head("DOWN", angle=self.curr_head4room_alphabet[0])
            if self.detect_room_alphabet(edge_info=edge_info):
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

        elif self.mode in ['find_box']:
            self._motion.set_head("DOWN", self.curr_head4box[0])
            box_info = self._image_processor.get_milk_info(visualization=False, color=self.alphabet_color, edge_info = edge_info)
            if box_info:
                self.mode = "track_box"
                if self.curr_room_color == "GREEN":
                    self.update_box_pos(edge_info=edge_info, box_info=box_info)
                    print(f"BOX POS -> {self.box_pos}")
                
            else:
                if self.curr_head4box[0] == 35:
                    if self.curr_room_color == "GREEN":
                        self._motion.turn(dir=self.direction, loop=4)
                    else:
                        self._motion.turn(dir=self.direction, loop=2)
                self.curr_head4box.rotate(-1)

        elif self.mode in ['track_box']:
            self._motion.set_head("DOWN", self.curr_head4box[0])
            box_info = self._image_processor.get_milk_info(visualization=False, color=self.alphabet_color, edge_info=edge_info)
            if box_info:
                (cx, cy) = box_info
                (dx, dy) = self.get_distance_from_baseline(box_info=box_info)


                if dy > 10:  # 기준선 보다 위에 있다면
                    if -40 <= dx <= 40:
                        print("기준점에서 적정범위. 전진 전진")
                        if self.curr_head4box == 75:
                            self._motion.walk(dir='FORWARD', loop=4)
                        else:
                            self._motion.walk(dir='FORWARD', loop=1)
                    elif dx <= -90:
                        if self.curr_head4box == 75:
                            self._motion.turn(dir='RIGHT', loop=2)
                        else:
                            self._motion.turn(dir='RIGHT', loop=1)
                    elif -90 < dx <= -50:  # 오른쪽
                        print("기준점에서 오른쪽으로 많이 치우침. 조정한다")
                        if self.curr_head4box == 75:
                            self._motion.walk(dir='RIGHT', wide=True, loop=2)
                        else:
                            self._motion.walk(dir='RIGHT', loop=2)
                    elif -50 < dx < -40:
                        if self.curr_head4box == 75:
                            self._motion.walk(dir='RIGHT', wide=True, loop=1)
                        else:
                            self._motion.walk(dir='RIGHT', loop=1)
                        print("기준점에서 오른쪽으로 치우침. 조정한다")
                    elif 90 > dx >= 50:  # 왼쪽
                        print("기준점에서 왼쪽으로 많이 치우침. 조정한다")
                        if self.curr_head4box == 75:
                            self._motion.walk(dir='LEFT', wide=True, loop=2)
                        else:
                            self._motion.walk(dir='LEFT', loop=2)
                    elif 50 > dx > 40:  # 왼쪽
                        print("기준점에서 왼쪽으로 치우침. 조정한다")
                        if self.curr_head4box == 75:
                            self._motion.walk(dir='LEFT', wide=True, loop=1)
                        else:
                            self._motion.walk(dir='LEFT', loop=2)

                    elif dx >= 90:
                        if self.curr_head4box == 75:
                            self._motion.turn(dir='LEFT', loop=2)
                        else:
                            self._motion.turn(dir='LEFT', loop=1)

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

        elif self.mode in ['catch_box']:
            self.catch_box()

        # 3. 박스 구역의 평행선 H 기준으로 안으로 또는 밖으로 옮기기
        elif self.mode in ['check_area']:
            print('line_info[H]:', line_info["H"])
            if not line_info[H]:
                if self.box_pos == 'RIGHT':
                    self._motion.turn(dir='LEFT', loop=1, grab=True)
                elif self.box_pos == 'LEFT':
                    self._motion.turn(dir='RIGHT', loop=1, grab=True)
            else:
                self.mode = 'fit_area'
                time.sleep(0.5)
            
        elif self.mode in ['fit_area']:
            if self.box_pos == 'RIGHT':
                if line_info["ALL_X"][1] > 360:
                    if line_info["ALL_X"][0] < 200:
                        self._motion.set_head(dir='DOWN', angle=35)
                        time.sleep(0.3)
                        self._motion.move_arm(dir='HIGH')  # 잡은 상태로 팔 앞으로 뻗고 고개 내림
                        self.mode = 'move_into_area'
                    else:
                        self._motion.walk(dir='RIGHT', loop=1, grab=True)
                else:
                    self._motion.walk(dir='RIGHT', loop=1, grab=True)
            elif self.box_pos == 'LEFT':
                if line_info["ALL_X"][0] < 150:
                    if line_info["ALL_X"][1] > 480:
                        self._motion.set_head(dir='DOWN', angle=35)
                        time.sleep(0.3)
                        self._motion.move_arm(dir='HIGH')  # 잡은 상태로 팔 앞으로 뻗고 고개 내림
                        self.mode = 'move_into_area'
                    else:
                        self._motion.walk(dir='LEFT', loop=1)
                else:
                    self._motion.walk(dir='LEFT', loop=1)
            else:
                self._motion.move_arm(dir='HIGH')  # 잡은 상태로 팔 앞으로 뻗고 고개 내림
                self.mode = 'move_into_area'
            print('line_info["ALL_X"][0]:', line_info["ALL_X"][0], 'line_info["ALL_X"][1]:', line_info["ALL_X"][1] )
            time.sleep(0.5)
                    
            
        elif self.mode in ['move_into_area']:
            self.move_into_area(line_info, edge_info)

        elif self.mode in ['box_into_area']:
            self.box_into_area(line_info, edge_info)
            if self.box_pos == 'LEFT':
                self._motion.turn(dir='RIGHT', sliding= True, wide=True, loop=self.loop_135)
            elif self.box_pos == 'RIGHT':
                self._motion.turn(dir='LEFT', sliding= True, wide=True, loop=self.loop_135)
                
            if self.curr_room_color == 'BLACK':
                self._motion.turn(dir=self.direction, sliding= True, wide=True, loop=self.loop_180)
                
            self.mode = 'end_mission'
            self.color = 'YELLOW'

        elif self.mode in ['end_mission']:
            self._motion.set_head(dir='DOWN', angle=60)
            time.sleep(0.2)

        elif self.mode in ['find_edge']:
            if edge_info["EDGE_POS"]: # yellow edge 감지
                if 280 < edge_info["EDGE_POS"][0] < 360 : # yellow edge x 좌표 중앙 O # 360
                    print('yellow edge 중앙 O --> ', edge_info["EDGE_POS"][0])
                    self.mode = 'return_line'# --> find_corner
                else: # yellow edge 중앙 X
                    print('yellow edge 감지 중앙 X --> ', edge_info["EDGE_POS"][0])
                    self.find_edge()

            else: # yellow edge 감지 X
                if line_info['DEGREE'] == 0 :
                    print('yellow edge 감지 X --만약 edge 중앙인데', 'line_info[DEGREE]:', '가 0이면 노란 선이 존재하지 않음 return_head 값 높여주기')
                else:
                    print('yellow edge 감지 X ','edge 중앙 값 다시 설정 필요함')
                self.mode = 'find_edge'# --> find_edge
                self.find_edge()
        # 걷기 # 보정 추가로 넣기
        elif self.mode in ['walk']:

            self._motion.set_head(dir='DOWN', angle=10)
            #time.sleep(0.3)

            if self.walk_info in ['┐', '┌']:  # 코너에서
                if line_info["H"]:
                    #if line_info["H_Y"][1] > 90:  # 라인이 감지는 되는데 좀 위에 있으면 전진하고 방향 정보에 맞춰 모드 바꿔줌
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
                        #self.walk(line_info, True)
                else:  # 코너인데 라인 정보 감지가 안되면 멈춰야하는거 아닌가?
                    self.walk(line_info, True)

            else:  # 직진하면 그렇게 만들 수 있게
                if line_info["H"]:
                    if np.mean(line_info["H_X"]) < 320:
                        self.walk_info = '┐'
                    else:
                        self.walk_info = '┌'
                else:
                    if line_info["V"]:
                        self.walk_info = '│'  # go
                        self.walk(line_info, True)
                    else:
                        self.walk_info = None  # modify_angle
                        self.walk(line_info, False)
            #time.sleep(0.3)
            
        elif self.mode in ['return_line']:
            if self.return_head == '60':
                if line_info["ALL_Y"][1] >= 200 :
                    self._motion.set_head(dir='DOWN', angle=45)
                    self.return_head = '45'
                    print(self.mode, ': 노란 색 영역 넓음 -> 고개 ', self.return_head, '로 진행')
                    time.sleep(0.5)

            elif self.return_head == '45':
                if line_info["ALL_Y"][1] >= 200 :
                    self._motion.set_head(dir='DOWN', angle=35)
                    self.return_head = '35'
                    print(self.mode, ': 노란 색 영역 넓음 -> 고개 ', self.return_head, '로 진행')
                    time.sleep(0.5)

            if self.curr_room_color == 'BLACK':
                self._motion.walk(dir='FORWARD', loop=1, grab=True)
                if edge_info["EDGE_POS"]:
                    if edge_info["EDGE_POS"][1] > 400:  # yellow edge y 좌표 가까이 O
                        self._motion.grab(switch=False)
                        self.count += 1
                        if self.count < 3 :
                            if self.direction == 'LEFT':
                                self._motion.turn(dir='RIGHT', loop=1, sliding= True, wide = True)
                            else:
                                self._motion.turn(dir='LEFT', loop=1, sliding= True, wide = True)
                        else:
                            self._motion.turn(dir=self.direction , loop=1, sliding= True, wide = True)
                        self.mode = 'find_corner'  # --> 걸을 직선 찾고 walk
                    else:  # yellow edge y 좌표 가까이 X
                        self._motion.walk(dir='FORWARD', loop=1, grab=True)

            elif self.curr_room_color == 'GREEN':
                if edge_info["EDGE_POS"]:
                    if edge_info["EDGE_POS"][1] > 400:  # yellow edge y 좌표 가까이 O
                        self._motion.walk(dir='FORWARD', loop=1)
                        if self.count < 3 :
                            if self.direction == 'LEFT':
                                self._motion.turn(dir='RIGHT', loop=1, sliding= True, wide = True)
                            else:
                                self._motion.turn(dir='LEFT', loop=1, sliding= True, wide = True)
                        else:
                            self._motion.turn(dir=self.direction , loop=1, sliding= True, wide = True)
                        self.mode = 'find_corner'  # --> 걸을 직선 찾고 walk
                    else: # yellow edge y 좌표 가까이 X
                        self._motion.walk(dir='FORWARD', loop=1)
                else: # yellow edge 감지 X 
                    self.mode = 'find_edge'  # --> return_line
                    self.find_edge()

        elif self.mode in ['find_corner']:
            if line_info["V"]:
                if 85 < line_info["DEGREE"] < 95:
                    if line_info["H"]:
                        self.motion.walk(dir=direction, wide= True, sliding = True, loop = 2)
                        if self.count < 3 :
                            self.mode = 'walk_next'
                        else
                            self.mode = 'walk'
                    else:
                        self._motion.walk(dir='BACKWARD')

                elif 0 < line_info["DEGREE"] <= 85:
                    print('MODIFY angle --LEFT')
                    self._motion.turn(dir='LEFT', loop=1, grab=self.is_grab) # 팔뻗기

                else:
                    print('MODIFY angle --RIGHT')
                    self._motion.turn(dir='RIGHT', loop=1, grab=self.is_grab) # 팔뻗기
                time.sleep(0.3)
                    
            else:
                if self.count < 3 :
                    if self.direction == 'LEFT':
                        self._motion.turn(dir='RIGHT', loop=1, sliding= True, wide = True)
                    else:
                        self._motion.turn(dir='LEFT', loop=1, sliding= True, wide = True)
                else:
                    self._motion.turn(dir=self.direction , loop=1, sliding= True, wide = True)
            time.sleep(0.5)
            
        elif self.mode in ['walk_next']:
            if line_info['H_DEGREE'] > 174:
                if 150 <= line_info['H_Y'][1] < 250:
                    if not line_info['V']:
                        self.motion.walk(dir=direction, wide= True, sliding = True, loop = 2)
                    else:
                        self.mode = 'mission_line'
                elif line_info['H_Y'][1] < 150:
                    print('입구 빠져 나가는 중 - H 멀어서 가까이 다가감', line_info['H'], line_info['H_Y'][1])
                    self._motion.open_door_walk(dir='FORWARD')
                else:
                    print('입구 빠져 나가는 중 - H 가까워서 한발자국 뒤로', line_info['H'], line_info['H_Y'][1])
                    self._motion.open_door_walk(dir='BACKWARD')
                    time.sleep(1)
            else:
                print('H_DEGREE:', line_info['H_DEGREE'], ', EDGE_R:', edge_info['EDGE_R'], ', EDGE_L:', edge_info['EDGE_L'])
                if edge_info['EDGE_R']:
                    self._motion.open_door_turn(dir='LEFT', sliding = True)
                elif edge_info['EDGE_L']:
                    self._motion.open_door_turn(dir='RIGHT', sliding = True)
                else:
                    print('else 걸림 1')

        # 나가기
        elif self.mode in ['is_finish_line']:
            if self.count < 3:
                if line_info["H"]:
                    self._motion.walk(dir='FORWARD')
                else:
                    self.mode = 'walk'
                    self.walk_info = '│'
            else:
                #self._motion.walk(dir='FORWARD')
                self.mode = 'finish'

        # 나가기
        elif self.mode in ['finish']:
            if self.direction == 'LEFT':
                self._motion.open_door(dir='LEFT', loop=15)
                print("left")
            else:
                self._motion.open_door(loop=15)
                print("right")
            self.mode = 'finish_notice'
                
        elif self.mode in ['finish_notice']:
            if self.black_room:
                self._motion.notice_alpha(self.black_room)
                self.black_room.clear()
                return 0
            