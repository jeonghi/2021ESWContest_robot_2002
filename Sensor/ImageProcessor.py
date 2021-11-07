import cv2
import numpy as np
import time
import platform
import os

from imutils.video import WebcamVideoStream
from imutils.video import FileVideoStream
from imutils.video import FPS
from imutils import auto_canny, grab_contours

if __name__ == "__main__":
    from HashDetector import HashDetector
    from Target import Target, setLabel
    from LineDetector import LineDetector
    from ColorChecker import ColorPreProcessor
    from CornerFinder import CornerFinder
else:
    from Sensor.HashDetector import HashDetector
    from Sensor.Target import Target, setLabel
    from Sensor.LineDetector import LineDetector
    from Sensor.ColorChecker import ColorPreProcessor
    from Sensor.CornerFinder import CornerFinder


class ImageProcessor:

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, video_path : str = ""):
        if video_path and os.path.exists(video_path):
            self._cam = FileVideoStream(path=video_path).start()
        else:
            if platform.system() == "Linux":
                self._cam = WebcamVideoStream(src=-1).start()
            else:
                self._cam = WebcamVideoStream(src=0).start()
        # 개발때 알고리즘 fps 체크하기 위한 모듈. 실전에서는 필요없음
        self.fps = FPS()
        if __name__ == "__main__":
            self.hash_detector4room = HashDetector(file_path='ABCD/')
            self.hash_detector4arrow = HashDetector(file_path='src/arrow/')

        else:

            self.hash_detector4door = HashDetector(file_path='Sensor/EWSN/')
            self.hash_detector4room = HashDetector(file_path='Sensor/ABCD/')
            self.hash_detector4arrow = HashDetector(file_path='Sensor/src/arrow/')

        self.line_detector = LineDetector()
        self.color_preprocessor = ColorPreProcessor()

        shape = (self.height, self.width, _) = self.get_image().shape
        print(shape)  # 이미지 세로, 가로 (행, 열) 정보 출력
        time.sleep(2)

    def get_image(self, visualization=False):
        src = self._cam.read()
        if src is None:
            exit()
        if visualization:
            cv2.imshow("src", src)
            cv2.waitKey(1)
        return src


    def get_door_alphabet(self, visualization: bool = False) -> str:
        src = self.get_image()
        if visualization:
            canvas = src.copy()
            roi_canvas = canvas.copy()
        no_canny_targets = []
        canny_targets = []
        # 그레이스케일화
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        # ostu이진화, 어두운 부분이 true(255) 가 되도록 THRESH_BINARY_INV
        _, mask = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        #cv2.imshow("mask",mask)
        
        canny = auto_canny(mask)
        cnts1, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts2, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in cnts1:

            (_, _, width, height) = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)
            approx = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True) * 0.02, True)
            vertice = len(approx)
            # roi의 가로 세로 종횡비를 구한 뒤 1:1의 비율에 근접한 roi만 통과
            area_ratio = width / height if height < width else height / width
            area_ratio = round(area_ratio, 2)

            if not ( 3500 < area  and area_ratio <= 1.4 and vertice == 4):
                continue

            target = Target(contour=cnt)
            no_canny_targets.append(target)
            if visualization:
                setLabel(canvas, cnt, "no_canny")

        for cnt in cnts2:
            (_, _, width, height) = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)
            approx = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True) * 0.02, True)
            vertice = len(approx)
            # roi의 가로 세로 종횡비를 구한 뒤 1:1의 비율에 근접한 roi만 통과
            area_ratio = width / height if height < width else height / width
            area_ratio = round(area_ratio, 2)

            if not (3500 < area and area_ratio <= 1.4 and vertice == 4):
                continue
            target = Target(contour=cnt)
            canny_targets.append(target)
            if visualization:
                setLabel(canvas, cnt, "canny", color=(0,0,255))


        target = Target.non_maximum_suppression4targets(canny_targets, no_canny_targets, threshold=0.7)

        if visualization:
            cv2.imshow("src", cv2.hconcat([canvas, roi_canvas]))
            # cv2.imshow("mask", mask)
            # cv2.imshow("canny", canny)
            # cv2.imshow("canvas", canvas)
            cv2.waitKey(1)

        if target is None:
            return None
        roi = target.get_target_roi(src=src)
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, roi_mask = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if visualization:
            pos = target.get_pts()
            setLabel(roi_canvas, target.get_pts(), label="roi", color=(255,0,0))
            mask = HashDetector.image_resize_with_pad(img=roi_mask, size=HashDetector.dim)
            roi_canvas[pos[1]:pos[1]+pos[3],pos[0]:pos[0]+pos[2]] = cv2.cvtColor(roi_mask, cv2.COLOR_GRAY2BGR)
            cv2.imshow("src", cv2.hconcat(
                [canvas, roi_canvas]))
            cv2.imshow('mask', mask)
            cv2.waitKey(1)
        answer, _ = self.hash_detector4door.detect_alphabet_hash(roi_mask, threshold=0.6)
        return answer

    def get_arrow_direction(self, visualization: bool = False):
        src = self.get_image()
        dst = src.copy()

        kernel = np.ones((5, 5), np.uint8)

        gray = cv2.cvtColor(src, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        edge = auto_canny(binary)

        contours, _ = cv2.findContours(edge, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        contour = max(contours, key=lambda x:cv2.contourArea(x))

        leftmost = tuple(contour[contour[:,:,0].argmin()][0])
        rightmost = tuple(contour[contour[:,:,0].argmax()][0])
        topmost = tuple(contour[contour[:,:,1].argmin()][0])
        bottommost = tuple(contour[contour[:,:,1].argmax()][0])
        
        result = [leftmost[0], topmost[1], rightmost[0]-leftmost[0], bottommost[1]-topmost[1]]
        if result[2] < 10 or result[3] < 10:
            roi_mask = src
        else:
            #print(result)
            roi_mask = src[result[1] : result[1] + result[3], result[0] : result[0] + result[2]]

        cv2.drawContours(dst, [contour], -1, (255, 0, 0), 2)
        if visualization:
            cv2.imshow("src", src)
            #cv2.imshow("binary", edge)
            #cv2.imshow("dst", dst)
            cv2.imshow("roi_mask", roi_mask)
            cv2.waitKey(10)
            
        direction = self.hash_detector4arrow.detect_arrow(roi_mask)
        print(direction)
        
        return direction

    def get_alphabet_info4room(self, edge_info={}, method="CONTOUR", visualization=False) -> tuple:
        src = self.get_image()
        if visualization:
            canvas = src.copy()
        alphabet_info = None
        candidates = []
        mask = self.color_preprocessor.get_alphabet_mask(src=src)

        if method == "LABEL":
            _, _, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
            for idx, centroid in enumerate(centroids):  # enumerate 함수는 순서가 있는 자료형을 받아 인덱스와 데이터를 반환한다.
                if stats[idx][0] == 0 and stats[idx][1] == 0:
                    continue

                if np.any(np.isnan(centroid)): # 배열에 하나이상의 원소라도 참이라면 true (즉, 하나이상의 중심점이 숫자가 아니면)
                    continue
                _, _, width, height, area = stats[idx]

                # roi의 가로 세로 종횡비를 구한 뒤 1:1의 비율에 근접한 roi만 통과
                area_ratio = width / height if height < width else height / width
                area_ratio = round(area_ratio, 2)
                if not (1500 < area < 8000 and area_ratio <= 1.4):
                    continue

                candidate = Target(stats=stats[idx], centroid=centroid)
                roi = candidate.get_target_roi(src, pad=15)
                candidate.set_color(self.color_preprocessor.check_red_or_blue(roi))
                ycrcb = cv2.cvtColor(roi, cv2.COLOR_BGR2YCrCb)
                y, cr, cb = cv2.split(ycrcb)

                normalizing = cr if candidate.get_color() == "RED" else cb
                normalized = cv2.normalize(normalizing, None, 0, 255, cv2.NORM_MINMAX)
                _, roi_mask = cv2.threshold(normalized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

                ### 정확도 향상을 위해 아래 함수 수정 요망 ###
                candidate_alphabet, _ = self.hash_detector4room.detect_alphabet_hash(roi_mask, threshold=0.4)
                ####################################

                #if visualization:
                #   cv2.imshow("thresh", cv2.hconcat([thresholding, roi_mask]))

                if candidate_alphabet is None:
                    continue
                candidate.set_name(candidate_alphabet)
                if visualization:

                    setLabel(canvas, candidate.get_pts(), label=f"{candidate.get_name()}", color=(255, 255, 255))
                candidates.append(candidate)
        else:
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:  # enumerate 함수는 순서가 있는 자료형을 받아 인덱스와 데이터를 반환한다.

                (_, _, width, height) = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)

                # roi의 가로 세로 종횡비를 구한 뒤 1:1의 비율에 근접한 roi만 통과
                area_ratio = width / height if height < width else height / width
                area_ratio = round(area_ratio, 2)
                if not (1000 < area and area_ratio <= 1.4):
                    continue

                candidate = Target(contour=contour)
                roi = candidate.get_target_roi(src, pad=10)
                candidate.set_color(self.color_preprocessor.check_red_or_blue(roi))
                ycrcb = cv2.cvtColor(roi, cv2.COLOR_BGR2YCrCb)
                y, cr, cb = cv2.split(ycrcb)
                normalizing = cr if candidate.get_color() == "RED" else cb
                normalized = cv2.normalize(normalizing, None, 0, 255, cv2.NORM_MINMAX)
                _, roi_mask = cv2.threshold(normalized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

                ### 정확도 향상을 위해 아래 함수 수정 요망 ###
                candidate_alphabet, _ = self.hash_detector4room.detect_alphabet_hash(roi_mask, threshold=0.8)
                ####################################

                # if visualization:
                #   cv2.imshow("thresh", cv2.hconcat([thresholding, roi_mask]))

                if candidate_alphabet is None:
                    continue
                candidate.set_name(candidate_alphabet)
                if visualization:
                    setLabel(canvas, candidate.get_pts(), label=f"{candidate.get_name()}", color=(255, 255, 255))

                candidates.append(candidate)

        if candidates:
            if edge_info:
                if edge_info["EDGE_UP"] :
                    #print("필터 적용전", candidates)
                    candidates = list(filter(lambda candidate: candidate.y + candidate.height < edge_info["EDGE_UP_Y"], candidates))
                    #print("적용 후", candidates)


        if candidates:
            selected = max(candidates, key=lambda candidate: candidate.get_center_pos()[1])
            alphabet_info = (selected.get_color(), selected.get_name())
            if visualization:
                setLabel(canvas, selected.get_pts(), label=f"{selected.get_name()}:{selected.get_color()}", color=(0, 0, 255))
                pos = selected.get_pts()
                roi = selected.get_target_roi(src)
                selected.set_color(self.color_preprocessor.check_red_or_blue(roi))
                ycrcb = cv2.cvtColor(roi, cv2.COLOR_BGR2YCrCb)
                y, cr, cb = cv2.split(ycrcb)
                normalizing = cr if selected.get_color() == "RED" else cb
                normalized = cv2.normalize(normalizing, None, 0, 255, cv2.NORM_MINMAX)
                _, roi_mask = cv2.threshold(normalized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                resized_mask = HashDetector.image_resize_with_pad(img=roi_mask, size=HashDetector.dim)
                canvas[pos[1]:pos[1] + pos[3], pos[0]:pos[0] + pos[2]] = cv2.cvtColor(roi_mask, cv2.COLOR_GRAY2BGR)
                cv2.imshow("resized", resized_mask)

        if visualization:
            mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            debug = cv2.hconcat([mask, canvas])
            cv2.imshow("debug", debug)
            cv2.waitKey(1)

        return alphabet_info


    def get_milk_info(self, color:str, edge_info:dict, visualization=False) -> tuple:
        src = self.get_image()
        if visualization:
            canvas = src.copy()
        candidates = []
        selected = None
        hls = cv2.cvtColor(src, cv2.COLOR_BGR2HLS)
        h, l, s = cv2.split(hls)
        k = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
        _, mask = cv2.threshold(s, 20, 255, cv2.THRESH_BINARY)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
        color_mask = None

        ### 색상 이진화를 이용한 마스킹 과정 ###
        if color == "BLUE":
            color_mask = self.color_preprocessor.get_blue_mask(h)
        elif color == "RED":
            color_mask = self.color_preprocessor.get_red_mask(h)
        else:
            color_mask = mask

        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, k)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, k)
        mask = cv2.bitwise_and(mask, color_mask)
        ###############################
        ###############################

        ### 라벨링을 이용한 객체 구별 ###############
        _, y, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)

        for idx, centroid in enumerate(centroids):  # enumerate 함수는 순서가 있는 자료형을 받아 인덱스와 데이터를 반환한다.
            if stats[idx][0] == 0 and stats[idx][1] == 0:
                continue

            if np.any(np.isnan(centroid)):  # 배열에 하나이상의 원소라도 참이라면 true (즉, 하나이상의 중심점이 숫자가 아니면)
                continue

            _, y, width, height, area = stats[idx]

            ### roi의 가로 세로 종횡비를 구한 뒤 1:1의 비율에 근접한 라벨만 남기도록 필터링
            area_ratio = width / height if height < width else height / width
            area_ratio = round(area_ratio, 2)
            #print(area_ratio)

            if not (1000 < width*height and area_ratio <= 1.7):
                continue
            ############################################################

            ### 초록색 영역 또는 검정색 영역 위쪽 라인위의 라벨은 무시하도록 필터링
            #if edge_info:
            #    if edge_info["EDGE_UP_Y"] > (y+height)//2 :
            #       continue
            ########################################

            ### 필터링에서 살아남은 후보 라벨만 Target 객체화 시켜 후보 리스트에 추가
            candidate = Target(stats=stats[idx], centroid=centroid)
            ########################################################

            if visualization:
                setLabel(canvas, candidate.get_pts(), label=f"MILK POS x:{candidate.x}, y:{candidate.y}", color=(255, 255, 255))
            candidates.append(candidate)

        if candidates:
            if edge_info:
                if edge_info["EDGE_UP"] :
                    #print("필터 적용전", candidates)
                    candidates = list(filter(lambda candidate: candidate.y + candidate.height > edge_info["EDGE_UP_Y"], candidates))
                    #print("적용 후", candidates)

        ### 후보 라벨이 있다면 그중에서 가장 큰 크기 객체의 중심 좌표를 반환
        if candidates:
            selected = max(candidates, key=lambda candidate:candidate.get_area())
            if visualization:
                setLabel(canvas, selected.get_pts(), label=f"MILK POS x:{selected.x}, y:{selected.y}",
                         color=(0, 0, 255))
        ### 시각화 ############################
        if visualization:
            cv2.imshow("src", canvas)
            #cv2.imshow("mask", mask)
            cv2.waitKey(1)
        #####################################
        #####################################

        ### 선택된 타깃의 중심 좌표 반환 ###########
        if selected:
            return selected.get_center_pos()
        ### 없다면 None 리턴
        return None



    def line_tracing(self, color: str = "YELLOW", line_visualization:bool=False, edge_visualization:bool=False, ROI:bool=False):
        if ROI:
            src = self.get_image()
            src = src[:][200:400]
        else:
            src = self.get_image()
        result = (line_info, edge_info, dst) = self.line_detector.get_all_lines(src=src, color=color, line_visualization = line_visualization, edge_visualization = edge_visualization)
        #print(line_info)
        #print(edge_info)
        if line_visualization or edge_visualization :
            cv2.imshow("line", dst)
            cv2.waitKey(1)
            #print(line_info["H_Y"])
        return result
    
    def get_yellow_line_corner(self, visualization=False):
        """

        :return: if corner exist return (cx, cy) else return None
        """
        src = self.get_image()
        corner = CornerFinder.get_yellow_line_corner_pos(src=src, visualization=visualization)

        return corner


        

if __name__ == "__main__":

    imageProcessor = ImageProcessor(video_path="src/old/green_area.mp4")
    #imageProcessor = ImageProcessor("")
    #imageProcessor = ImageProcessor(video_path="")
    # imageProcessor.fps.start()
    while True:
        #imageProcessor.get_arrow_direction()
        #_, info, _ = imageProcessor.line_tracing(color ="GREEN", line_visualization=False, edge_visualization=True)
        #alphabet = imageProcessor.get_door_alphabet(visualization=True)
        #print(alphabet)
        #src = imageProcessor.get_image(visualization=True)
        #imageProcessor.get_milk_info(color="RED", edge_info=info, visualization=True)
        #print(imageProcessor.get_green_area_corner(visualization=True))
        #imageProcessor.line_tracing(color="GREEN", edge_visualization=True)
        #result = imageProcessor.get_alphabet_info4room(edge_info = info, visualization=True)
        #imageProcessor.room_test()
        imageProcessor.get_yellow_line_corner(visualization=True)
