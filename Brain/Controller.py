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
    
        #self.mode = "walk"
        #self.direction = "LEFT"
        #self.color = "YELLOW"
        #self.box_pos = None
        #self.curr_room_color = None
        #self.alphabet_color = None
        #self.alphabet = None
        
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
            self._motion.notice_direction(dir=self.alphabet)
            return True
        return False
    
    def update_box_pos(self, edge_info: dict, box_info: tuple):
        if edge_info["EDGE_DOWN"]:
            center_x = 320
            (cor_x, cor_y) = (edge_info["EDGE_DOWN_X"], edge_info["EDGE_DOWN_Y"])
            (box_x, box_y) = box_info
            dx = 100
            if cor_x - dx <= box_x <= cor_x + dx:
                if box_y <= cor_y:
                    self.box_pos = "MIDDLE"
                else:
                    if box_x <= cor_x :
                        self.box_pos = "RIGHT"
                    else:
                        self.box_pos = "LEFT"
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

    def line_tracing(self, line_visualization=False, edge_visualization=False):
        line_info, edge_info, result = self._image_processor.line_tracing(color=self.color, line_visualization = line_visualization, edge_visualization=edge_visualization)
        return line_info, edge_info

    def detect_direction(self) -> bool:
        self.direction = self._image_processor.get_arrow_direction()
        if self.direction:
            return True
        return False

    def turn_to_green_area_after_box_tracking(self) -> None:

        if self.box_pos == 'RIGHT':
            self._motion.turn(dir='LEFT', loop=7, grab=True)

        elif self.box_pos == 'LEFT':
            self._motion.turn(dir='RIGHT', loop=7, grab=True)

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
                        self._motion.walk(dir='FORWARD', loop=4, grab=self.is_grab)  # 팔뻗기
                else:
                    if line_info["V_X"][0] < 290:
                        self._motion.walk(dir='LEFT', loop=1, grab=self.is_grab) # 팔뻗기
                    elif line_info["V_X"][0] > 350:
                        self._motion.walk(dir='RIGHT', loop=1, grab=self.is_grab) # 팔뻗기

        elif line_info["DEGREE"] <= 85:
            print('MODIFY angle --LEFT')
            self._motion.turn(dir='LEFT', loop=1, grab=self.is_grab) # 팔뻗기

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
                self._motion.turn(dir='LEFT', loop=5, grab=True)
            elif self.box_pos == 'LEFT':
                self._motion.turn(dir='RIGHT', loop=5, grab=True)
            self._motion.move_arm(dir='LOW')
            self.mode = 'check_area'
        else:
            self._motion.turn(dir=self.direction, loop=5, grab=True)
            self.mode = 'end_mission'
            self.color = 'YELLOW'
        time.sleep(0.5)

    def check_area(self, line_info, edge_info):
        if self.box_pos == 'RIGHT':
            if line_info["H"]:
                self.mode = 'fit_area'
            else:
                self._motion.turn(dir='LEFT', loop=1, grab=True)
        elif self.box_pos == 'LEFT':
            if line_info["H"]:
                self.mode = 'fit_area'
            else:
                self._motion.turn(dir='RIGHT', loop=1, grab=True)
        else:
            self.mode = 'fit_area'
        time.sleep(0.5)

    def fit_area(self, line_info, edge_info):
        self._motion.set_head(dir='DOWN', angle=35)
        time.sleep(0.3)
        if self.box_pos == 'RIGHT':
            if line_info["ALL_X"][1] > 440:
                if line_info["ALL_X"][0] < 180:
                    self._motion.move_arm(dir='HIGH')  # 잡은 상태로 팔 앞으로 뻗고 고개 내림
                    self.mode = 'move_into_area'
                else:
                    self._motion.walk(dir='RIGHT', loop=1, grab=True)
            else:
                self._motion.walk(dir='RIGHT', loop=1, grab=True)
        elif self.box_pos == 'LEFT':
            if line_info["ALL_X"][0] < 150:
                if line_info["ALL_X"][1] > 440:
                    self._motion.move_arm(dir='HIGH')  # 잡은 상태로 팔 앞으로 뻗고 고개 내림
                    self.mode = 'move_into_area'
                else:
                    self._motion.walk(dir='LEFT', loop=1)
            else:
                self._motion.walk(dir='LEFT', loop=1)
        else:
            if edge_info["EDGE_DOWN_X"] < 300:
                self._motion.walk(dir='RIGHT', loop=1, grab=True)
            elif edge_info["EDGE_DOWN_X"] > 340:
                self._motion.walk(dir='LEFT', loop=1, grab=True)
            else:
                self._motion.move_arm(dir='HIGH')  # 잡은 상태로 팔 앞으로 뻗고 고개 내림
                self.mode = 'move_into_area'
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

        if self.DEBUG:
            print(self.mode)
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
            self.mode = 'detect_door_alphabet'  # --> walk

        # 1) 방위 인식 --> 성공시 2) 라인트레이싱
        elif self.mode in ['detect_door_alphabet']:
            self._motion.set_head(dir="DOWN", angle=self.curr_head4door_alphabet[0])
            if self.detect_door_alphabet():
                self._motion.set_head(dir="DOWN", angle=10)
                self._motion.walk(dir='FORWARD', loop=2)
                self._motion.walk(dir='RIGHT', loop=4)
                self._motion.turn(dir='SLIDING_LEFT', loop=4)
                self.mode = "entrance_1"
                time.sleep(0.3)
            else:
                self.curr_head4door_alphabet.rotate(-1)

        elif self.mode in ['entrance_1']:
            if line_info['H']:
                self._motion.open_door()  # 팔올린 채로
            else:
                self._motion.turn(dir='LEFT')

            if line_info['V']:
                self._motion.basic_form()
                self._motion.turn(dir='SLIDING_RIGHT', loop=4)
                self._motion.walk(dir='BACKWARD')
                self.mode = 'entrance_2'

        elif self.mode in ['entrance_2']:
            if line_info['H']:
                
                self.mode = 'detect_direction'
            else:
                self._motion.turn(dir='RIGHT')

            
        # 3) 화살표 방향 인식
        elif self.mode in ['detect_direction']:

            self._motion.set_head(dir='DOWN', angle=90)
            if self.detect_direction():
                self._motion.set_head(dir='DOWN', angle=10)
                time.sleep(0.3)
                # if line_info['DEGREE'] != 0:
                # self.walk(line_info, True)
                # else:
                self._motion.walk('FORWARD', 4)  # 너무 뒤에서 멈추면 추가
                self._motion.walk(self.direction, 4)
                self._motion.turn(self.direction, 8)
                self.mode = 'walk'
                self.walk_info = '│'
            else:
                self._motion.walk("BACKWARD", 1)
                time.sleep(0.5)
                


        # 3) 화살표 방향 인식
        #elif self.mode in ['detect_direction']:
            #self._motion.set_head(dir='DOWN', angle=90)
            #if self.detect_direction():
                #self._motion.walk("BACKWARD", 1)
                #time.sleep(0.5)
            #else:
                #self._motion.set_head(dir='DOWN', angle=10)
                #time.sleep(0.3)
                # if line_info['DEGREE'] != 0:
                # self.walk(line_info, True)
                # else:
                #self._motion.walk('FORWARD', 4)  # 너무 뒤에서 멈추면 추가
                #self._motion.walk(self.direction, 4)
                #self._motion.turn(self.direction, 8)
                #self.mode = 'walk'
                #self.walk_info = '│'

        # 걷기 # 보정 추가로 넣기
        elif self.mode in ['walk']:

            self._motion.set_head(dir='DOWN', angle=10)
            time.sleep(0.3)

            if self.walk_info in ['┐', '┌']:  # 코너에서
                if line_info["H"]:
                    if line_info["H_Y"][1] > 90:  # 라인이 감지는 되는데 좀 위에 있으면 전진하고 방향 정보에 맞춰 모드 바꿔줌
                        self._motion.walk("FORWARD", 1)
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
                    else:
                        self.walk(line_info, True)
                else:  # 코너인데 라인 정보 감지가 안되면 멈춰야하는거 아닌가?
                    self.walk(line_info, True)

            else:  # 직진하면 그렇게 만들 수 있게
                if line_info["H"]:
                    if line_info["H_X"][0] <= 170:
                        if line_info["H_X"][1] >= 430:
                            self.walk_info = 'T'
                            self.set_basic_form()
                            self.mode = 'detect_direction'
                        else:
                            self.walk_info = '┐'
                    else:
                        if line_info["H_X"][1] >= 430:
                            self.walk_info = '┌'
                        else:
                            print('out of range')

                else:
                    if line_info["V"]:
                        self.walk_info = '│'  # go
                        self.walk(line_info, True)
                    else:
                        self.walk_info = None  # modify_angle
                        self.walk(line_info, False)
            time.sleep(0.3)

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
               self._motion.turn(dir='RIGHT', loop=9)
            elif self.box_pos == 'RIGHT':
               self._motion.turn(dir='LEFT', loop=9)

            self.mode = 'end_mission'
            self.color = 'YELLOW'

        elif self.mode in ['end_mission']:

            self._motion.set_head(dir='DOWN', angle=60)
            time.sleep(0.2)

            if self.curr_room_color == 'GREEN':
                if self.box_pos == 'RIGHT':
                    if line_info["ALL_X"][1] > 340:
                        if line_info["ALL_Y"][1] < 100 : # yellow 감지
                            self._motion.set_head(dir='DOWN', angle=60)
                            self.return_head = '60'
                        else:
                            self._motion.set_head(dir='DOWN', angle=45)
                            self.return_head = '45'
                        self.mode = 'find_edge'
                    else:
                        if self.curr_room_color == 'BLACK':
                            self._motion.turn(dir=self.direction, loop=1, grab=True)
                        else:
                            self._motion.turn(dir='LEFT', loop=1)
                else:
                    if line_info["ALL_X"][0] < 300:
                        if line_info["ALL_Y"][1] < 100 : # yellow 감지
                            self._motion.set_head(dir='DOWN', angle=60)
                            self.return_head = '60'
                        else:
                            self._motion.set_head(dir='DOWN', angle=45)
                            self.return_head = '45'
                        self.mode = 'find_edge'

                    else:
                        if self.curr_room_color == 'BLACK':
                            self._motion.turn(dir=self.direction, loop=1, grab=True)

                        else:
                            self._motion.turn(dir='RIGHT', loop=1)
            else:
                if (self.direction == 'RIGHT' and 0 < line_info["ALL_X"][0] < 300) or (self.direction == 'LEFT' and line_info["ALL_X"][1] > 340):
                        if line_info["ALL_Y"][1] < 100 :  # yellow 감지
                            self._motion.set_head(dir='DOWN', angle=60)
                            self.return_head = '60'

                        else:
                            self._motion.set_head(dir='DOWN', angle=45)
                            self.return_head = '45'

                        self.mode = 'find_edge'
                else:
                    if self.curr_room_color == 'BLACK':
                        self._motion.turn(dir=self.direction, loop=1, grab=True)
                    else:
                        self._motion.turn(dir='RIGHT', loop=1)
            time.sleep(1)

        elif self.mode in ['find_edge']:
            if edge_info["EDGE_POS"]: # yellow edge 감지
                if 280 < edge_info["EDGE_POS"][0] < 360 : # yellow edge x 좌표 중앙 O
                    self.mode = 'return_line'# --> find_corner
                else: # yellow edge 중앙 X
                    print('yellow edge 감지 중앙 X')
                    self.find_edge()

            else: # yellow edge 감지 X
                print('yellow edge 감지 X ')
                self.mode = 'find_edge'# --> find_edge
                self.find_edge()

        elif self.mode in ['return_line']:
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
                    if edge_info["EDGE_POS"][1] > 450:  # yellow edge y 좌표 가까이 O
                        self._motion.grab(switch=False)
                        self._motion.turn(dir=self.direction, loop=2)
                        self.mode = 'find_corner'  # --> 걸을 직선 찾고 walk
                    else:  # yellow edge y 좌표 가까이 X
                        self.mode = 'return_line'  # --> find_V
                time.sleep(0.5)

            elif self.curr_room_color == 'GREEN':
                if edge_info["EDGE_POS"]:
                    if edge_info["EDGE_POS"][1] > 450:  # yellow edge y 좌표 가까이 O
                        self._motion.walk(dir='FORWARD', loop=1)
                        self._motion.turn(dir=self.direction, loop=2)
                        self.mode = 'find_corner'  # --> 걸을 직선 찾고 walk

                    else: # yellow edge y 좌표 가까이 X
                        self.mode = 'return_line'  # --> find_V
                        # self.return_line()
                        self._motion.walk(dir='FORWARD', loop=1)
                    time.sleep(0.5)

                else: # yellow edge 감지 X 
                    self.mode = 'find_edge'  # --> return_line
                    self.find_edge()

        elif self.mode in ['find_corner']:
            if line_info["V"]:
                if 300 < line_info["V_X"][0] < 340:
                    self._motion.walk(dir='FORWARD', loop=2)
                    self.mode = 'walk'
                    self.walk_info = '│'
                elif line_info["V_X"][0] <= 300:
                    self._motion.walk(dir='LEFT', loop=1)
                else:
                    self._motion.walk(dir='RIGHT', loop=1)
            else:
                self._motion.turn(self.direction, 1)
            time.sleep(0.5)

        # 나가기
        elif self.mode in ['is_finish_line']:
            if line_info['H'] and line_info['H_Y'][0] < 150:
                self.walk(line_info, True)
            else:
                if self.count < 3:
                    self.mode = 'walk'
                    self.walk_info = '│'
                else:
                    self.mode = 'finish'
            time.sleep(0.5)

        # 나가기
        elif self.mode in ['finish']:
            if self.direction == 'LEFT':
                self._motion.open_door(dir='LEFT', loop=8)
            else:
                self._motion.open_door(loop=8)

            if self.black_room:
                self._motion.notice_direction(self.black_room)
                self.black_room.clear()
            