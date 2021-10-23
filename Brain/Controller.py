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
        self.direction: str = None
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

        self.return_head: str = ""  # return 할 때 고개 각도 바꿀 지 고민 중 10/08
        self.mode_history: str = self.mode

        # "start"("detect_room_alphabet") , "walk", "detect_direction", "start_mission",
        #self.mode = "start"
        #self.direction = "" # "LEFT", "RIGHT"
        #self.color = "YELLOW" # 노란색, 검정색, 초록색
        #self.box_pos = ""
        #self.curr_room_color = ""


        #self.mode = "detect_direction"
        #self.direction = None
        #self.color = "YELLOW"
        #self.box_pos = ""
        #self.curr_room_color =""
    
        self.mode = "walk"
        self.direction = "LEFT"
        self.color = "YELLOW"
        self.box_pos = None
        self.curr_room_color = None
        self.alphabet_color = None
        self.alphabet = None
        
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

    def reset_room_var(self):
        self.curr_room_color = None
        self.alphabet = None
        self.alphabet_color = None
        self.box_pos = None

    def set_basic_form(self):
        self._motion.basic_form()

    def get_distance_from_baseline(self, box_info, baseline=(320, 370)):
        # if bx - cx > 0: 왼쪽에 박스가 있는 것이므로 왼쪽으로 움직여야함
        # if bx - cx < 0: 오른쪽에 박스가 있는 것이므로 오른쪽으로 움직여야함
        # if by - cy > 0: 위쪽에 박스가 있는 것
        # if by - cy < 0: 아래쪽에 박스가 있는
        (bx, by) = baseline
        (cx, cy) = box_info
        return (bx-cx, by-cy)

    def detect_door_alphabet(self) -> bool :
        self.alphabet = self._image_processor.get_door_alphabet()
        if self.alphabet:
            self._motion.notice_direction(dir=self.alphabet)
            return True
        return False
    
    def update_box_pos(self, edge_info:dict, box_info:tuple):
        if edge_info["EDGE_DOWN"]:
            center_x = 320
            (cor_x, cor_y) = (edge_info["EDGE_DOWN_X"], edge_info["EDGE_DOWN_Y"])
            (box_x, box_y) = box_info
            dx = 100
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
        elif self.direction == "RIGHT":
            self.box_pos = "LEFT"
        else:
            self.box_pos = "RIGHT"

    def detect_room_alphabet(self, edge_info) -> bool:
        #self._motion.set_head(dir="LEFTRIGHT_CENTER")  # 알파벳을 인식하기 위해 고개를 다시 정면으로 향하게 한다.
        alphabet_info = self._image_processor.get_alphabet_info4room(method="CONTOUR", edge_info=edge_info)
        if alphabet_info:
            self.alphabet_color, self.alphabet = alphabet_info
            return True
        return False

    def recognize_area_color(self):
        self._motion.set_head(dir=self.direction, angle=45) # 화살표 방향과 동일한 방향으로 45도 고개를 돌린다
        time.sleep(0.5)
        self._motion.set_head(dir="DOWN", angle=45) # 아래로 45도 고개를 내린다
        time.sleep(0.5)
        self.color = 'GREEN'
        line_info, edge_info = self.line_tracing(line_visualization=False, edge_visualization=True)
        if edge_info['EDGE_DOWN']:
            self.color = 'GREEN'
        else:
            self.color = 'BLACK'
        self._motion.notice_area(area=self.color) # 지역에 대한 정보를 말한다
        self.curr_room_color = self.color
        time.sleep(0.5)
        self.mode = 'detect_room_alphabet' # 알파벳 인식 모드로 변경한다.
        return

    def line_tracing(self, line_visualization=False, edge_visualization=False):
        line_info, edge_info, result = self._image_processor.line_tracing(color=self.color, line_visualization = line_visualization, edge_visualization=edge_visualization)
        return line_info, edge_info

    def detect_direction(self) -> bool :
        self.direction = self._image_processor.get_arrow_direction()
        if self.direction:
            return True
        return False

    def turn_to_green_area_after_box_tracking(self) -> None:
        if self.box_pos == 'RIGHT':
            self._motion.turn(dir='LEFT', loop=7, grab=True)
            self._motion.move_arm(dir='LOW')
            # time.sleep(1)
            self.mode = 'check_area'
        elif self.box_pos == 'LEFT':
            self._motion.turn(dir='RIGHT', loop=7, grab=True)
            self._motion.move_arm(dir='LOW')
            # time.sleep(1)
            self.mode = 'check_area'
        else:
            self._motion.move_arm(dir='LOW')
            # time.sleep(1)
            self.mode = 'check_area'

    def turn_to_black_area_after_box_tracking(self) -> None:
        self._motion.turn(dir=self.direction, loop=7, grab=True)
        # time.sleep(1)
        self.mode = 'end_mission'
        self.color = 'YELLOW'

    def walk(self, line_info, walk_info):
        # line_info = {"DEGREE" : 0, "V" : False, "V_X" : [0 ,0], "V_Y" : [0 ,0], "H" : False, "H_X" : [0 ,0], "H_Y" : [0 ,0]}
        self._motion.set_head(dir='DOWN', angle=10)
        # 손을 들고 있지 않으면서 이전에 문열기, 끝내기 였다면 팔을 들고 변수를 수정해줌
        if not self.is_grab and self.progress_of_robot[-1] in ['detect_door_alphabet','finish']:
            #self._motion.grab()
            self.is_grab = True
            self._motion.move_arm(dir='HIGH')
            self._motion.set_head(dir='DOWN', angle=10)
            print('팔뻗기')
        #time.sleep(1)
        if walk_info == '│':
            if 85 < line_info["DEGREE"] < 95:
                if 290 < line_info["V_X"][0] <350:
                    print('walk')
                    print('│')
                    self._motion.walk(dir='FORWARD', loop=3, grab=self.is_grab) # 팔뻗기
                    #time.sleep(1)
                else:
                    if line_info["V_X"][0] < 290:
                        print('← ←', line_info["V_X"][0])
                        self._motion.walk(dir='LEFT', loop=1, grab=self.is_grab) # 팔뻗기
                        #time.sleep(1)
                    elif line_info["V_X"][0] > 350:
                        print('→ →', line_info["V_X"][0])
                        self._motion.walk(dir='RIGHT', loop=1, grab=self.is_grab) # 팔뻗기
                        #time.sleep(1)
            elif line_info["DEGREE"] <= 85:
                print('MODIFY angle --LEFT')
                self._motion.turn(dir='LEFT', loop=1, grab=self.is_grab) # 팔뻗기
                #time.sleep(1)
            elif line_info["DEGREE"] >= 95:
                print('MODIFY angle --RIGHT')
                self._motion.turn(dir='RIGHT', loop=1, grab=self.is_grab) # 팔뻗기
                #time.sleep(1)
            else:
                print('else')


        elif walk_info == None: # 'modify_angle'
            if line_info["DEGREE"] <= 85:
                print('MODIFY angle --LEFT')
                self._motion.turn(dir='LEFT', loop=1, grab=self.is_grab) # 팔뻗기
                #time.sleep(1)
            elif line_info["DEGREE"] >= 95:
                print('MODIFY angle --RIGHT')
                self._motion.turn(dir='RIGHT', loop=1, grab=self.is_grab) # 팔뻗기
                #time.sleep(1)
            else:
                print('else')

        else:
            print('walk_info is not │ or None ------------>', self.walk_info)

    def find_edge(self): #find_corner_for_outroom
        if self.curr_room_color=='BLACK':
            self._motion.turn(dir=self.direction, loop=1, grab=True) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
            time.sleep(1)

        elif self.curr_room_color == 'GREEN':
            if self.direction == 'LEFT':
                if self.box_pos == 'RIGHT':
                    self._motion.turn(dir='LEFT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
                    time.sleep(1)
                if self.box_pos == 'LEFT':
                    self._motion.turn(dir='RIGHT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
                    time.sleep(1)
            elif self.direction == 'RIGHT':
                if self.box_pos == 'LEFT':
                    self._motion.turn(dir='RIGHT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
                    time.sleep(1)
                if self.box_pos == 'RIGHT':
                    self._motion.turn(dir='LEFT', loop=1) # 박스 위치 감지하고 들어오는 방향 기억해서 넣어주기
                    time.sleep(1)
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
            if line_info["H"] :
                self.mode = 'fit_area'
                time.sleep(1)
            else:
                self._motion.turn(dir='LEFT', loop=1, grab=True)
                time.sleep(1)
        elif self.box_pos == 'LEFT':
            if line_info["H"] :
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
                
    def move_into_area(self, line_info, edge_info):
        if self.box_pos:
            if line_info['ALL_Y'][1] > 460: # 발 나온다는 생각으로 절반 아래에 오면 발 앞이라고 생각할 것임 -- 수정 예정
                self.mode = 'box_into_area'
            else:
                self._motion.walk(dir='FORWARD', loop=1, grab=True)
                time.sleep(1)
        else:
            print("self.box_pos is None, Please check it")

    def box_into_area(self, line_info, edge_info):
        self._motion.walk(dir='FORWARD', loop=2, grab=True)
        self._motion.grab(switch=False) # 앉고 잡은 박스 놓는 모션 넣기
        self.color = 'YELLOW'
        self.count += 1

    def run(self):

        if self.DEBUG:
            if self.color == 'YELLOW':
                line_info, edge_info = self.line_tracing(line_visualization=True, edge_visualization=False)
            elif self.color == 'GREEN':
                line_info, edge_info = self.line_tracing(line_visualization=False, edge_visualization=True)
            else:
                line_info, edge_info = self.line_tracing()
        else:
            line_info, edge_info = self.line_tracing()

        # 0) 시작
        if self.mode in ['start'] :
            self.mode = 'detect_door_alphabet' # --> walk

        # 1) 방위 인식 --> 성공시 2) 라인트레이싱
        elif self.mode in ['detect_door_alphabet']:
            self._motion.set_head(dir="DOWN", angle=self.curr_head4door_alphabet[0])
            time.sleep(0.3)
            if self.detect_door_alphabet():
                self._motion.set_head(dir="DOWN", angle=10)
                self.mode = "walk"
                time.sleep(2)
            else:
                self.curr_head4door_alphabet.rotate(n=-1)

        # 3) 화살표 방향 인식
        elif self.mode in ['detect_direction']:
            self._motion.set_head(dir='DOWN', angle=90)
            if self.detect_direction():
                self._motion.walk("BACKWARD", 1)
                time.sleep(1)
            else:
                self._motion.set_head(dir='DOWN', angle=10)
                time.sleep(1.5)
                # if line_info['DEGREE'] != 0:
                # self.walk(line_info, '│')
                # else:
                self._motion.walk('FORWARD', 4)  # 너무 뒤에서 멈추면 추가
                self._motion.walk(self.direction, 4)
                self._motion.turn(self.direction, 8)
                self.mode = 'walk'
                self.walk_info = '│'

        # 걷기 # 보정 추가로 넣기
        elif self.mode in ['walk'] :
            self._motion.set_head(dir='DOWN', angle=10)
            # 디폴트 슬립때문에 느림..
            if self.walk_info not in ['┐','┌'] :
                time.sleep(0.5)
                if line_info["H"]:
                    print(line_info["H_X"])
                    if line_info["H_X"][0] <= 170 and line_info["H_X"][1] >= 430:
                        self.walk_info = 'T'
                        print(line_info["H_Y"][1])
                        # if line_info["H_Y"][1] > 190:
                        self.mode = 'detect_direction'
                        self.set_basic_form()
                        self.is_grab = False
                        # else:
                        # self._motion.walk("FORWARD", 1, grab=True)
                        # time.sleep(0.5)

                    else:
                        if line_info["H_X"][0] < 170 and line_info["H_X"][1] < 430:
                            self.walk_info = '┐'

                        elif line_info["H_X"][0] > 170 and line_info["H_X"][1] > 430:
                            self.walk_info = '┌'

                        else:
                            print('out of range')

                else:
                    if line_info["V"]:
                        print('go')
                        self.walk_info = '│'
                        self.walk(line_info, self.walk_info)
                    else:
                        print('modify_angle')
                        self.walk_info = None  # 'modify_angle'
                        self.walk(line_info, self.walk_info)

            elif self.walk_info =='┌':
                # time.sleep(1)
                if line_info["H_Y"][1] > 90:
                    self._motion.walk("FORWARD", 1)
                    # time.sleep(1)
                    if self.direction == 'RIGHT':
                        self.mode = 'is_finish_line'  # --> end_mission --> return_line
                    elif self.direction == 'LEFT':
                        self.mode = 'start_mission'  # --> walk / finish
                    else:
                        print('The Robot has not direction, Please Set **self.direction**')
                else:
                    self.walk(line_info, '│')
                    # time.sleep(1)

            # 미션 진입 판별
            elif self.walk_info == '┐':
                # time.sleep(1)
                if line_info["H_Y"][1] > 90:
                    self._motion.walk("FORWARD", 1)
                    # time.sleep(1)
                    if self.direction == 'RIGHT':
                        self.mode = 'start_mission'  # --> end_mission --> return_line
                    elif self.direction == 'LEFT':
                        self.mode = 'is_finish_line'  # --> walk / finish
                    else:
                        print('The Robot has not direction, Please Set **self.direction**')
                else:
                    self.walk(line_info, '│')
                    # time.sleep(1)
    
        # 0. 확진 / 안전 구역 확인 : self.color 바꿔주세요, self.mode = 'box_tracking'로 바꿔주세요.
        elif self.mode in ['start_mission']:
            self.recognize_area_color()
            self._motion.set_head("LEFTRIGHT_CENTER")

        # 1. red, blue 알파벳 구별
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

        # 2. 박스 트래킹 : self.alphabet_color 기준으로 edge_info["EDGE_UP_Y"] 아래 공간, self.box_pos박스 위치 바꿔주세요 (LEFT, MIDDLE, RIGHT)
        ## grap on 과 동시에 self.mode = 'box_into_area'로 바꾸기
        ## # 1) 박스 grap on 하면 손 내리고 고개든다 (MIDDLE이면 고개 좀 많이 내려주기, LEFT RIGHT는 30 정도면 될 듯?아마??)
        elif self.mode in ['find_box']:
            ### 계속해서 안전/확진지역 영역의 코너 정보를 기반으로 현재 로봇이 방에서 어디에서 활동하고 있는지를 업데이트 해줍니다.
            self._motion.set_head("DOWN", self.curr_head4box[0])
            box_info = self._image_processor.get_milk_info(color=self.alphabet_color, edge_info = edge_info)
            if box_info:
                self.mode = "track_box"
                print(f"BOX POS -> {self.box_pos}")
                if self.curr_room_color == "GREEN":
                    self.update_box_pos(edge_info=edge_info, box_info=box_info)
            else:
                if self.curr_head4box[0] == 35:
                    if self.curr_room_color == "GREEN":
                        self._motion.turn(dir=self.direction, loop=4)
                    else:
                        self._motion.turn(dir=self.direction, loop=2)
                self.curr_head4box.rotate(-1)

        elif self.mode in ['track_box']:
            self._motion.set_head("DOWN", self.curr_head4box[0])
            box_info = self._image_processor.get_milk_info(color=self.alphabet_color, edge_info=edge_info)
            if box_info:
                (cx, cy) = box_info
                (dx, dy) = self.get_distance_from_baseline(box_info=box_info)


                if dy > 10:  # 기준선 보다 위에 있다면
                    if -40 <= dx <= 40:
                        print("기준점에서 적정범위. 전진 전진")
                        self._motion.walk(dir='FORWARD', loop=1)
                    elif dx <= -90:
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
            self.check_area(line_info, edge_info)
            
        elif self.mode in ['fit_area']:
            self.fit_area(line_info, edge_info)
            
        elif self.mode in ['move_into_area']:
            self.move_into_area(line_info, edge_info)

        elif self.mode in ['box_into_area']:
            self.box_into_area(line_info, edge_info)
            if self.box_pos == 'LEFT':
               self._motion.turn(dir = 'RIGHT', loop=9 )
            elif self.box_pos == 'RIGHT':
               self._motion.turn(dir = 'LEFT', loop=9 )

            self.mode = 'end_mission'
            self.color = 'YELLOW'

        elif self.mode in ['end_mission']:

            self._motion.set_head(dir ='DOWN', angle = 60)
            time.sleep(0.5)

            if self.curr_room_color == 'GREEN':
                if self.box_pos == 'RIGHT':
                    if line_info["ALL_X"][1] > 340:
                        if line_info["ALL_Y"][1] < 100 : # yellow 감지
                            self._motion.set_head(dir ='DOWN', angle = 60)
                            self.return_head = '60'
                        else:
                            self._motion.set_head(dir ='DOWN', angle = 45)
                            self.return_head = '45'
                        time.sleep(0.5)
                        self.mode = 'find_edge'
                    else:
                        if self.curr_room_color == 'BLACK':
                            self._motion.turn(dir=self.direction, loop=1, grab=True)
                        else:
                            self._motion.turn(dir='LEFT', loop=1)
                        time.sleep(0.5)
                else:
                    if line_info["ALL_X"][0] < 300:
                        if line_info["ALL_Y"][1] < 100 : # yellow 감지
                            self._motion.set_head(dir ='DOWN', angle = 60)
                            self.return_head = '60'
                        else:
                            self._motion.set_head(dir ='DOWN', angle = 45)
                            self.return_head = '45'

                        self.mode = 'find_edge'
                        time.sleep(0.5)
                    else:
                        if self.curr_room_color == 'BLACK':
                            self._motion.turn(dir=self.direction, loop = 1, grab = True)

                        else:
                            self._motion.turn(dir='RIGHT', loop = 1)
                            time.sleep(0.5)
                        time.sleep(0.5)
            else:
                if (self.direction == 'RIGHT' and 0 < line_info["ALL_X"][0] < 300) or (self.direction == 'LEFT' and line_info["ALL_X"][1] > 340):
                        if line_info["ALL_Y"][1] < 100 : # yellow 감지
                            self._motion.set_head(dir ='DOWN', angle = 60)
                            self.return_head = '60'

                        else:
                            self._motion.set_head(dir ='DOWN', angle = 45)
                            self.return_head = '45'

                        self.mode = 'find_edge'
                        time.sleep(0.5)
                      
                else:
                    if self.curr_room_color == 'BLACK':
                        self._motion.turn(dir = self.direction, loop = 1, grab = True)
                        time.sleep(1)
                    else:
                        self._motion.turn(dir = 'RIGHT', loop = 1)
                        time.sleep(1)

        elif self.mode in ['find_edge']:
            if edge_info["EDGE_POS"] : # yellow edge 감지
                if 280 < edge_info["EDGE_POS"][0] < 360 : # yellow edge x 좌표 중앙 O
                    self.mode = 'return_line' # --> find_corner
                else: # yellow edge 중앙 X
                    print('yellow edge 감지 중앙 X')
                    self.find_edge()

            else: # yellow edge 감지 X
                print('yellow edge 감지 X ')
                self.mode = 'find_edge' # --> find_edge
                self.find_edge()

        elif self.mode == 'return_line':
            if self.return_head == '60':
                if line_info["ALL_Y"][1] > 100 :
                    self._motion.set_head(dir='DOWN', angle=45)
                    self.return_head = '45'
                    time.sleep(0.5)
                        
            elif self.return_head == '45':
                if line_info["ALL_Y"][1] > 100 :
                    self._motion.set_head(dir='DOWN', angle=35)
                    self.return_head = '35'
                    time.sleep(0.5)
            
            if self.curr_room_color == 'BLACK':
                self._motion.walk(dir='FORWARD', loop=1, grab=True)
                if edge_info["EDGE_POS"]:
                    if edge_info["EDGE_POS"][1] > 450: # yellow edge y 좌표 가까이 O
                        self._motion.grab(switch = False)
                        self._motion.turn(dir=self.direction, loop = 2)
                        self.mode = 'find_corner' # --> 걸을 직선 찾고 walk
                    else: # yellow edge y 좌표 가까이 X
                        self.mode = 'return_line' # --> find_V
                time.sleep(0.5)

            elif self.curr_room_color == 'GREEN':
                if edge_info["EDGE_POS"]:
                    if edge_info["EDGE_POS"][1] > 450: # yellow edge y 좌표 가까이 O
                        self._motion.walk(dir='FORWARD', loop=1)
                        self._motion.turn(dir=self.direction, loop = 2)
                        self.mode = 'find_corner' # --> 걸을 직선 찾고 walk

                    else: # yellow edge y 좌표 가까이 X
                        self.mode = 'return_line' # --> find_V
                        # self.return_line()
                        self._motion.walk(dir='FORWARD', loop=1)
                    time.sleep(0.5)

                else: # yellow edge 감지 X 
                    self.mode = 'find_edge' # --> return_line
                    self.find_edge()

        elif self.mode == 'find_corner':
            if line_info["V"]:
                if 300 < line_info["V_X"][0] < 340:
                    self._motion.walk(dir='FORWARD', loop=2)
                    self.mode = 'walk'
                    self.walk_info = '│'
                elif line_info["V_X"][0] <= 300:
                    self._motion.walk(dir='LEFT', loop=1)
                else:
                    self._motion.walk(dir='RIGHT', loop=1)
                time.sleep(1)
            else:
                self._motion.turn(self.direction, 1)
                time.sleep(1)

        # 나가기
        elif self.mode == 'is_finish_line':
            if line_info['H']:
                self.walk(line_info, '│')
                time.sleep(1)
            else: #line_info['H'] == False
                if self.count < 3:
                     self.mode = 'walk'
                     self.walk_info = '│'
                     #self.count += 1 # count 방식 미션 grap_off 기준으로 count하면 좋을 듯 :: 중요
                else:
                    self.mode = 'finish' # --> stop!
                    self._motion.turn(dir=self.direction, loop =10)
                    time.sleep(1)

        # 나가기
        elif self.mode == 'finish':
            self.mode = 'walk'
            self.walk_info = '│'
            if self.black_room :
                self._motion.notice_direction(self.black_room)
                self.black_room.clear()
            
        if self.mode_history != self.mode:
            if self.mode != 'walk':
                self.progress_of_robot.append(self.mode_history)
            self.mode_history = self.mode
            cv2.destroyAllWindows()