from Sensor.ImageProcessor import ImageProcessor, COLORS
from Actuator.Motion import Motion, MOTION
import numpy as np
import cv2
import time
import sys


class Robot:

    def __init__(self):
        self.imageProcessor = ImageProcessor()
        self.motion = Motion()
        self.motion.head()
        # self.motion.head(view=MOTION["VIEW"]["DOWN30"], direction=MOTION["DIR"]["CENTER"])

        self.direction = "LEFT"
        self.curr_room = None  # 지금있는 방 이름 저장
        self.curr_mission = "GREEN"  # BLACK 또는 GREEN 이 저장됨 (확진구역 미션이냐, 안전지역 미션이냐)
        self.curr_target_color = None  # 지금 방 이름의 색깔이자 추적 대상의 색상 빨간색 우유나 파란색 우유
        self.black_rooms = []  # 확진구역일때 방이름 담아 놓기 위한 리스트
        self.curr_target_position = "RIGHT"  # 지금 방에서 초기 우유곽이 어디에 있었는지 위치 정보(안전지역 미션에서 필요).
        # 확진지역, 안전지역으로 회전할때 효율적 빠르게 회전하기 위해 필요함.

    def fast_turn(self):
        if self.direction is "LEFT":
            if self.curr_target_position is "RIGHT":
                turn = "LEFT"
            else:
                turn = "RIGHT"
        else:
            if self.curr_target_position is "LEFT":
                turn = "RIGHT"
            else:
                turn = "LEFT"
        return turn

    def trace_milk(self, find="UP-DOWN"):
        # self.motion.head()
        baseline = (bx, by) = (320, 420)
        VIEWS = ["DOWN45", "DOWN30"]
        idx = 0
        while True:
            print("타깃 탐색한다")
            target = self.imageProcessor.detect_front_target(color=COLORS[self.curr_target_color]["MILK"])
            if target is None:  # 만약에 객체가 없거나 이탈하면, 다시 객체를 찾아야한다.
                print("타깃이 없다 재탐색한다")
                VIEW = self.find_milk(color=COLORS[self.curr_target_color]["MILK"], turn="LEFT", find=find)
                idx = VIEWS.index(VIEW)
                continue
            (dx, dy) = target.get_distance_from_baseline(baseline=baseline)
            print("타깃을 추적한다. 기준점으로부터 가로로 {} 세로로 {} 만큼 차이가 난다".format(dx, dy))
            if dy > 10:  # 기준선 보다 위에 있다면
                if -40 <= dx <= 40:
                    print("기준점에서 적정범위. 전진 전진")
                    self.motion.walk()
                elif dx <= -50:  # 오른쪽
                    print("기준점에서 오른쪽으로 치우침. 조정한다")
                    self.motion.move(direction="RIGHT", repeat=3)
                elif -50 < dx < -40:
                    print("기준점에서 오른쪽으로 치우침. 조정한다")
                    self.motion.move(direction="RIGHT", repeat=1)
                elif dx >= 50:  # 왼쪽
                    print("기준점에서 왼쪽으로 치우침. 조정한다")
                    self.motion.move(direction="LEFT", repeat=3)
                elif 50 > dx > 40:  # 왼쪽
                    print("기준점에서 왼쪽으로 치우침. 조정한다")
                    self.motion.move(direction="LEFT", repeat=1)
            elif dy <= 10:
                if idx < len(VIEWS) - 1:  # 대가리를 다 내린게 아닌데 기준선보다 아래이면
                    print("타깃에 근접했다. 목을 내려 아래 시야를 확보한다.")
                    self.motion.head(view=MOTION["VIEW"][VIEWS[idx]])
                    idx += 1
                    idx = idx % len(VIEWS)  # 인덱스 초과시
                elif idx == len(VIEWS) - 1:  # 대가리를 다 내린 상태에서 기준선 보다 아래이면 잡기 시전
                    print("타깃을 집는다")
                    self.motion.grab()
                    distance = self.motion.check_distance()
                    print("거리 센서 값은 {} 입니다".format(distance))
                    if distance >= 90:
                        print("성공적으로 잡았다")
                        cv2.destroyAllWindows()
                        return
                    else:
                        self.motion.grab(switch="OFF")
                        print("잡기 실패! 다시 탐색한다")
                        idx = 0

    #  타깃이 발견될때까지 대가리 상하 좌우 & 몸 틀기 시전
    def find_milk(self, color, turn, find):
        if find is "UP-DOWN":
            VIEWS = ["DOWN45", "DOWN30"]
        elif find is "DOWN-UP":
            VIEWS = ["DOWN30", "DOWN45"]
        else:
            VIEWS = ["DOWN45", "DOWN30"]

        HEADS = ["CENTER"]
        HEAD_MOVING = [(VIEW, HEAD) for HEAD in HEADS for VIEW in VIEWS]
        print("{}색 우유곽을 {}방향으로 탐색합니다".format(color["color"], find))

        for VIEW, HEAD in HEAD_MOVING:  # 센터 위아래 -> 왼쪽 위아래 -> 오른쪽 위아래 순으로 탐색
            self.motion.head(view=MOTION["VIEW"][VIEW], direction=MOTION["DIR"][HEAD])
            target = self.imageProcessor.detect_front_target(color=color)
            if target is None:  # 해당 방향에 타깃이 없다면
                continue
            else:  # 해당 방향에 타깃이 있다면 , 방향으로 몸을 틀고
                if "LEFT" in VIEW:  # 왼쪽에서 발견했으면 왼쪽으로 틀고
                    self.motion.turn(direction="LEFT", repeat=4)
                    self.motion.head(view=MOTION["VIEW"][VIEW],
                                     direction=MOTION["DIR"]["CENTER"])  # 대가리 바로
                    print("find left Target, turn left")
                elif "RIGHT" in VIEW:  # 오른쪽에서 발견했으면 오른쪽으로 틀고
                    self.motion.turn(direction="RIGHT", repeat=4)  # 대가리 바로
                    self.motion.head(view=MOTION["VIEW"][VIEW],
                                     direction=MOTION["DIR"]["CENTER"])  # 대가리 왼쪽 아래 45도틀기
                    print("find right Target, turn right")
                else:
                    print("find center Target, not turn")
                cv2.destroyAllWindows()
                return VIEW

        # 모든 탐색을 했지만 아무도 없다면 왼쪽 또는 오른 쪽으로 몸을 틀고 재탐색
        print("{}색 우유곽을 찾지 못했습니다 {}턴 하고 재탐색합니다".format(color["color"], turn))
        self.motion.turn(direction=turn, repeat=4)
        cv2.destroyAllWindows()
        return self.find_milk(color=color, turn="LEFT", find=find)

    def check_room_mission(self):  # 왼쪽방향으로 진행시에 지역에 대한 판단
        self.motion.head()
        self.motion.head(view=MOTION["VIEW"]["DOWN45"], direction=MOTION["DIR"]["LEFT45"])  # 대가리 왼쪽 아래 45도틀기
        self.curr_mission = self.imageProcessor.check_area_color()

    def turn_to_yellow_line_corner(self, turn):

        baseline = (bx, by) = (320, 420)
        self.motion.head(view=MOTION["VIEW"]["DOWN54"], direction=MOTION["DIR"]["CENTER"])

        if self.curr_mission is "GREEN":  # 안전 지역에서 빠져 나간다면 물건을 집지 않고 그냥 회전
            self.motion.turn(direction=turn, repeat=3)
            while True:
                corner_pos = self.imageProcessor.get_yellow_line_corner_pos()
                if corner_pos:
                    (cx, cy) = corner_pos
                    if bx - 50 <= cx <= bx + 50:  # 적정범위 이내이면 물건 들고 전진, 리턴
                        print("코너가 적정 범위에 들어왔습니다. 코너로 전진합니다")
                        self.motion.walk()
                        cv2.destroyAllWindows()
                        return
                    elif bx - 80 <= cx < bx - 50:  # 적정범위밖 왼쪽으로 치우쳐있다면요
                        print("코너가 범위에서 왼쪽으로 벗어났습니다. 오른쪽으로 ")
                        self.motion.turn(direction="RIGHT")
                    elif bx + 50 < cx <= bx + 80:  # 적정범위밖 오른쪽으로 치우쳐있다면
                        print("코너가 범위에서 오쪽으로 벗어났습니다. 왼쪽으로 턴")
                        self.motion.turn(direction="LEFT")
                    else:
                        print("걍 범위에 들지도 않아 지정 방향으로 턴")
                        self.motion.turn(direction=turn)
                else:
                    print("코너가 검출되지 않았습니다 지정 방향으로 턴")
                    self.motion.turn(direction=turn)

        elif self.curr_mission is "BLACK":  # 감염 지역에서 빠져 나간다면 물건을 집고 그냥 회전
            self.motion.turn(grab="GRAB", direction=turn, repeat=3)
            while True:
                corner_pos = self.imageProcessor.get_yellow_line_corner_pos()
                if corner_pos:
                    (cx, cy) = corner_pos
                    if bx - 50 <= cx <= bx + 50:  # 적정범위 이내이면 물건 들고 전진, 리턴
                        self.motion.walk(grab="GRAB")
                        cv2.destroyAllWindows()
                        return
                    elif bx - 80 <= cx < bx - 50:  # 적정범위밖 왼쪽으로 치우쳐있다면
                        self.motion.turn(grab="GRAB", direction="RIGHT", repeat=1)
                    elif bx + 50 < cx <= bx + 80:  # 적정범위밖 오른쪽으로 치우쳐있다면
                        self.motion.turn(grab="GRAB", direction="LEFT", repeat=1)
                        cv2.destroyAllWindows()
                        return
                    else:
                        self.motion.turn(grab="GRAB", direction=turn, repeat=1)
                else:
                    self.motion.turn(grab="GRAB", direction=turn, repeat=1)

            pass

    # 45도 회전
    def turn45_to_black_area(self, turn):
        self.motion.turn(direction=turn, repeat=3)

    def turn90_to_next_alphabet(self, turn):
        self.motion.turn(direction=turn, repeat=6)

    def rescue_to_nonblack_area(self):

        turn = self.fast_turn()
        self.motion.head(view=MOTION["VIEW"]["DOWN60"],
                         direction=MOTION["DIR"]["CENTER"])

        self.turn_to_yellow_line_corner(turn=turn)
        self.motion.head(view=MOTION["VIEW"]["DOWN10"], direction=MOTION["DIR"]["CENTER"])  # 대가리 왼쪽 아래 45도틀기
        is_not_in_black = False
        while is_not_in_black is False:
            self.motion.walk(grab="GRAB")
            roi = self.imageProcessor.get_checker_roi4stop()
            black_rate = self.imageProcessor.count_color_pixel(color=COLORS["BLACK"]["HOME"], img=roi)
            if black_rate <= 50:
                print("감염지역을 벗어났습니다")
                is_not_in_black = True
        self.motion.walk(grab="GRAB")
        print("시민을 내려놓습니다")
        self.motion.grab(switch="OFF")
        cv2.destroyAllWindows()

    def rescue_to_green_area(self):
        turn = self.fast_turn()
        self.motion.head(view=MOTION["VIEW"]["DOWN45"],
                         direction=MOTION["DIR"]["CENTER"])
        flag = False
        self.motion.turn(grab="GRAB", direction=turn, repeat=6)
        while flag is False:  # 초록색이 roi 에서 감지될때까지 회전한다.
            roi = self.imageProcessor.get_checker_roi4turn()
            green_rate = self.imageProcessor.count_color_pixel(color=COLORS["GREEN"]["HOME"], img=roi)
            if green_rate >= 80:
                print("전방에 안전지역이 감지되었습니다. 전진합니다.")
                flag = True
            else:
                self.motion.turn(grab="GRAB", direction=turn, repeat=2)

        flag = False
        self.motion.head(view=MOTION["VIEW"]["DOWN10"], direction=MOTION["DIR"]["CENTER"])
        while flag is False:  # 마찬가지로 초록색이 roi에서 감지될때까지 회전한다.
            self.motion.walk(grab="GRAB")
            roi = self.imageProcessor.get_checker_roi4stop()
            green_rate = self.imageProcessor.count_color_pixel(color=COLORS["GREEN"]["HOME"], img=roi)
            if green_rate >= 60:
                self.motion.walk(grab="GRAB")
                flag = True

        # 안전빵으로 한발자국 더 가서 내려놓기
        self.motion.walk(grab="GRAB")
        self.motion.grab(switch="OFF")
        self.turn_to_yellow_line_corner(turn=turn)
        cv2.destroyAllWindows()

    def detect_alphabet(self):
        self.motion.head(view=MOTION["VIEW"]["DOWN70"])
        target, img = self.imageProcessor.detect_last_target()
        if target is None:
            print("감지된 알파벳 없음")
            cv2.destroyAllWindows()
            return False
        self.curr_target_color = target.color
        print("알파벳으로 추정되는 타깃의 색상은 {}색입니다.".format(self.curr_target_color))
        if self.curr_mission is "BLACK":
            print("확진지역 미션이므로, 방 이름을 인식합니다.")
            while True:
                target, img = self.imageProcessor.detect_last_target()
                roi = target.get_target_img(img=img, pad=10)
                if roi is None:
                    continue
                cv2.imshow("roi", roi)
                cv2.waitKey(1)
                recognized_text = self.imageProcessor.recognize_text_from_roi(roi=roi)
                for t in "ABCD":
                    if t in recognized_text:
                        print("이 방은{} 입니다 ".format(t))
                        self.curr_room = t
                        self.black_rooms.append(t)
                        cv2.destroyAllWindows()
                        return True
                print("방문자 잘못인식했습니다. 잘못인식된 문자: {} ".format(recognized_text))

        else:
            print("안전지역 미션이므로, 이름 인식을 생략하고 바로 추적합니다")
        cv2.destroyAllWindows()
        return True

    def find_target_at_green(self):

        ########## 1) 위 ##########
        self.motion.head(view=MOTION["VIEW"]["DOWN75"], direction=MOTION["DIR"]["CENTER"])
        targets = self.imageProcessor.detect_color_targets(color=COLORS[self.curr_target_color]["MILK"])
        if targets is not None and len(targets) >= 2:
            if self.direction is "LEFT":
                self.curr_target_position = "RIGHT"
            else:
                self.curr_target_position = "LEFT"
            print("{}쪽 \"정면\"에서 추적 대상 색상이 2개 이상 감지되었습니다. 가까운 객체를 추적합니다".format(self.curr_target_position))
            cv2.destroyAllWindows()
            return self.trace_milk(find="UP-DOWN")
        ########## 2) 아래 (알파벳 안보이는 시야) ###########
        self.motion.head(view=MOTION["VIEW"]["DOWN30"], direction=MOTION["DIR"]["CENTER"])
        targets = self.imageProcessor.detect_color_targets(color=COLORS[self.curr_target_color]["MILK"])

        if targets:
            if self.direction is "LEFT":
                self.curr_target_position = "RIGHT"
            else:
                self.curr_target_position = "LEFT"
            print("{}쪽 \"아래\"에서 추적 대상이 감지되었습니다. 객체를 추적합니다".format(self.curr_target_position))
            cv2.destroyAllWindows()
            return self.trace_milk(find="DOWN-UP")

        ######### 현재 방향에서는 없음 턴해서 다른 알파벳쪽을 확인 ########
        self.turn90_to_next_alphabet(turn=self.direction)

        ######### 3) 반대측 아래 (알파벳 안보이는 시야) ###########
        self.motion.head(view=MOTION["VIEW"]["DOWN30"], direction=MOTION["DIR"]["CENTER"])
        targets = self.imageProcessor.detect_color_targets(color=COLORS[self.curr_target_color]["MILK"])
        if targets and len(targets) >= 1:
            if self.direction is "LEFT":
                self.curr_target_position = "LEFT"
            else:
                self.curr_target_position = "RIGHT"
            print("{}쪽 \"아래\"에서 추적 대상 색상이 감지되었습니다. 가까운 객체를 추적합니다".format(self.curr_target_position))
            cv2.destroyAllWindows()
            return self.trace_milk(find="DOWN-UP")

        # 료######## 4) 반대측 정면 위 #################
        self.motion.head(view=MOTION["VIEW"]["DOWN75"], direction=MOTION["DIR"]["CENTER"])
        targets = self.imageProcessor.detect_color_targets(color=COLORS[self.curr_target_color]["MILK"])
        if targets and len(targets) >= 1:
            if self.direction is "LEFT":
                self.curr_target_position = "LEFT"
            else:
                self.curr_target_position = "RIGHT"
            print("{}쪽 \"정면\"에서 추적 대상 색상이 1개 이상 감지되었습니다. 가까운 객체를 추적합니다".format(self.curr_target_position))
            cv2.destroyAllWindows()
            return self.trace_milk(find="UP-DOWN")

        print("추적 대상이 없습니다 코드 수정이 필요합니다. 프로그램 종")
        exit()