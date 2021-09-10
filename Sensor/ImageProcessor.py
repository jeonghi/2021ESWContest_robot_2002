import cv2
import numpy as np
import time
import platform
import os
from imutils.video import WebcamVideoStream
from imutils.video import FileVideoStream
from imutils.video import FPS
from imutils import auto_canny
from Sensor.HashDetector import HashDetector
from Sensor.Target import Target, setLabel, non_maximum_suppression4targets
from Sensor.LineDetector import LineDetector
from Sensor.ColorChecker import check_color4roi, get_green_pixel_rate

class ImageProcessor:

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
            self.hash_detector4door = HashDetector(file_path='EWSN/')
            self.hash_detector4room = HashDetector(file_path='ABCD/')
            self.hash_detector4arrow = HashDetector(file_path='src/arrow/')
        else:

            self.hash_detector4door = HashDetector(file_path='Sensor/EWSN/')
            self.hash_detector4room = HashDetector(file_path='Sensor/ABCD/')
            self.hash_detector4arrow = HashDetector(file_path='Sensor/src/arrow/')
        #self.line_detector = LineDetector()

        shape = (self.height, self.width, _) = self.get_image().shape
        print(shape)  # 이미지 세로, 가로 (행, 열) 정보 출력
        time.sleep(2)

    def get_image(self, visualization=False):
        src = self._cam.read()
        if src is None:
            exit()
        if visualization:
            cv2.imshow("Src", src)
            cv2.waitKey(10)
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
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        canny = auto_canny(mask)
        cnts1, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts2, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in cnts1:
            approx = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True) * 0.02, True)
            vertice = len(approx)
            if vertice == 4 and cv2.contourArea(cnt) > 2500:
                target = Target(contour=cnt)
                no_canny_targets.append(target)
                if visualization:
                    setLabel(canvas, cnt, "no_canny")

        for cnt in cnts2:
            approx = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True) * 0.02, True)
            vertice = len(approx)
            if vertice == 4 and cv2.contourArea(cnt) > 2500:
                target = Target(contour=cnt)
                canny_targets.append(target)
                if visualization:
                    setLabel(canvas, cnt, "canny", color=(0,0,255))

        target = non_maximum_suppression4targets(canny_targets, no_canny_targets, threshold=0.7)

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
            roi_canvas[pos[1]:pos[1]+pos[3],pos[0]:pos[0]+pos[2]] = cv2.cvtColor(roi_mask, cv2.COLOR_GRAY2BGR)
            cv2.imshow("src", cv2.hconcat(
                [canvas, roi_canvas]))
            cv2.waitKey(1)
        return self.hash_detector4door.detect_alphabet_hash(roi_mask)

    def get_slope_degree(self, visualization: bool = False):
        src = self.get_image()
        return self.line_detector.get_slope_degree(src)

    def get_room_alphabet(self, visualization: bool = False):

        src = self.get_image()
        if visualization:
            canvas = src.copy()
        _, roi_mask = cv2.threshold(cv2.cvtColor(src, cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        canny = auto_canny(roi_mask)
        canny_targets = []
        cnts, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in cnts:
            approx = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True) * 0.02, True)
            vertice = len(approx)
            if vertice == 4 and 2000 <= cv2.contourArea(cnt):
                target = Target(contour=cnt)
                canny_targets.append(target)

        for candidate in canny_targets:
            roi = candidate.get_target_roi(src)
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, roi_mask = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            roi_thresholded = cv2.bitwise_and(roi,roi,mask=roi_mask)
            h_value = check_color4roi(roi_thresholded)
            result = self.hash_detector4room.detect_alphabet_hash(roi_mask, threshold=0.2)
            # if result is None:
            #     continue
            if visualization:
                color: str = None
                if 95 <= h_value <= 135:
                    color = "BLUE"
                elif h_value <= 20 or h_value >= 150 :
                    color = "RED"
                setLabel(canvas, candidate.get_pts(), f"{result}-hue:{color}", color=(0, 0, 255))
                cv2.imshow("mask", roi_thresholded)


        if visualization:
            cv2.imshow("src", cv2.hconcat([canvas, cv2.cvtColor(canny,cv2.COLOR_GRAY2BGR)]))
            cv2.waitKey(1)

    def get_arrow_direction(self):
        src = self.get_image()
        return self.hash_detector4arrow.detect_arrow(src)

    def ostu_thresholding(self, visualization: bool = False):
        src = self.get_image()
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        _, roi_mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        roi_mask = cv2.morphologyEx(roi_mask, cv2.MORPH_OPEN, kernel)
        roi_mask = cv2.morphologyEx(roi_mask, cv2.MORPH_CLOSE, kernel)
        #roi_mask = cv2.bitwise_not(roi_mask)
        roi_masked = cv2.bitwise_and(src, src, mask=roi_mask)
        if visualization:
            cv2.imshow("src", cv2.hconcat([src, cv2.cvtColor(roi_mask, cv2.COLOR_GRAY2BGR)]))
            cv2.waitKey(1)

    def get_area_color(self, threshold: float = 0.5, visualization: bool = False):
        src = self.get_image()
        area_color = get_green_pixel_rate(src=src, threshold=threshold, visualization=visualization)
        return area_color

        

if __name__ == "__main__":

    imageProcessor = ImageProcessor(video_path="src/green_room_test/green_area2.h264")
    imageProcessor.fps.start()
    #while imageProcessor.fps._numFrames < 200:
    while True:
        imageProcessor.get_image(visualization=True)
        #imageProcessor.ostu_thresholding(visualization=True)
        #imageProcessor.get_room_alphabet(visualization=True)
        print(imageProcessor.get_area_color())
        imageProcessor.fps.update()
    imageProcessor.fps.stop()
    print("[INFO] time : " + str(imageProcessor.fps.elapsed()))
    print("[INFO] FPS : " + str(imageProcessor.fps.fps()))



