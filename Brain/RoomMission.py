from Brain.Robot import Robot

class RoomMission:
    def __init__(self, robot : Robot):
        self.robot = robot
        
    def reset_room_var(self):
        self.robot.curr_room_color = None
        self.robot.alphabet = None
        self.robot.alphabet_color = None
        self.robot.box_pos = None

    def set_basic_form(self):
        self.robot._motion.basic_form()
        self.robot.is_grab = False
        self.robot.cube_grabbed = False

    def get_distance_from_baseline(self, box_info, baseline=(320, 370)):
        """
        :param box_info: 우유팩 위치 정보를 tuple 형태로 받아온다. 우유팩 영역 중심 x좌표와 y좌표 순서
        :param baseline: 우유팩 위치 정보와 비교할 기준점이다.
        :return: 우유팩이 지정한 기준점으로부터 떨어진 상대적 거리를 tuple로 반환한다.
        """
        (bx, by) = baseline
        (cx, cy) = box_info
        return (bx-cx, by-cy)
    
    def update_box_pos(self, edge_info: dict, box_info: tuple):
        if edge_info["EDGE_DOWN"]:
            center_x = 320
            (cor_x, cor_y) = (edge_info["EDGE_DOWN_X"], edge_info["EDGE_DOWN_Y"])
            (box_x, box_y) = box_info
            dx = 30
            if cor_x - dx <= box_x <= cor_x + dx:
                
                self.robot.box_pos = "MIDDLE"
                
                #if box_x <= cor_x :
                #    self.robot.box_pos = "LEFT"
                #else:
                #    self.robot.box_pos = "RIGHT"
            elif box_x < cor_x - dx :
                self.robot.box_pos = "LEFT"
            else:
                self.robot.box_pos = "RIGHT"
        elif self.robot.direction == "RIGHT":
            self.robot.box_pos = "LEFT"
        else:
            self.robot.box_pos = "RIGHT"

    def detect_room_alphabet(self, edge_info) -> bool:
        """
        :param edge_info: 방 미션 지역의 경계선 정보로, 알파벳 인식 함수에서 필터링을 위한 정보로 사용된다.
        :return: 인식된 방 알파벳 정보가 있다면 성공(True), 없다면 실패(False)
        """
        alphabet_info = self.robot._image_processor.get_alphabet_info4room(method="CONTOUR", edge_info=edge_info)
        if alphabet_info:
            self.robot.alphabet_color, self.robot.alphabet = alphabet_info
            return True
        return False

    def recognize_area_color(self) -> bool:
        time.sleep(1)
        self.robot.color = 'GREEN'
        line_info, edge_info = self.robot.line_tracing(line_visualization=False, edge_visualization=True)
        if edge_info['EDGE_DOWN']:
            self.robot.curr_room_color = 'GREEN'
        else:
            self.robot.curr_room_color = 'BLACK'

        if self.robot.curr_room_color:
            self.robot._motion.notice_area(area=self.robot.curr_room_color)
            self.robot.color = self.robot.curr_room_color
            return True

        return False

    def line_tracing(self, line_visualization=False, edge_visualization=False, ROI= False):
        line_info, edge_info, result = self.robot._image_processor.line_tracing(color=self.robot.color, line_visualization = line_visualization, edge_visualization=edge_visualization, ROI=ROI)
        return line_info, edge_info

    def turn_to_green_area_after_box_tracking(self) -> None:

        if self.robot.box_pos == 'RIGHT':
            print('turn 3')
            self.robot._motion.turn(dir='LEFT', loop=4, wide=True, sliding = True, grab=True)
        elif self.robot.box_pos == 'LEFT':
            print('turn 3')
            self.robot._motion.turn(dir='RIGHT', loop=4, wide=True, sliding = True, grab=True)


        self.robot._motion.move_arm(dir='LOW')
        self.robot.mode = 'check_area'

    def turn_to_black_area_after_box_tracking(self) -> None:
        self.robot._motion.turn(dir=self.robot.direction, loop=6, wide=True, sliding = True, grab=True)
        # time.sleep(1)
        self.robot.mode = 'end_mission'
        self.robot.color = 'YELLOW'
    
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