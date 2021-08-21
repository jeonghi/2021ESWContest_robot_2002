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
from Sensor.Target import Target, IoU, setLabel


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
        shape = (self.height, self.width, _) = self.get_image().shape
        print(shape)  # 이미지 세로, 가로 (행, 열) 정보 출력
        time.sleep(2)

    def get_image(self, visualization=False):
        src = self._cam.read()
        if src is None:
            exit()
        if visualization:
            cv2.imshow("Src", src)
            cv2.waitKey(1)
        return src

    def get_door_alphabet(self, visualization: bool = False) -> str:
        src = self.get_image()
        targets = []
        # 그레이스케일화
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        # ostu이진화, 어두운 부분이 true(255) 가 되도록 THRESH_BINARY_INV
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        canny = auto_canny(mask)
        cnts1, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts2, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.imshow("mask", mask)
        cv2.imshow("canny", canny)
        for cnt in cnts1:
            approx = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True) * 0.02, True)
            vertice = len(approx)
            if vertice == 4 and cv2.contourArea(cnt) > 2500:
                target = Target(contour=cnt)
                targets.append(target)
                setLabel(src, cnt, "no_canny")

        for cnt in cnts2:
            approx = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True) * 0.02, True)
            vertice = len(approx)
            if vertice == 4 and cv2.contourArea(cnt) > 2500:
                target = Target(contour=cnt)
                targets.append(target)
                setLabel(src, cnt, "canny", color=(0,0,255))

        cv2.imshow("target", src)
        cv2.waitKey(30)
        if len(targets)>=2:
            targets.sort(key=lambda x: x.get_area())
            iou = IoU(targets[0],targets[1])
            if iou > 0.9:
                roi = targets[0].get_target_roi(src=src, visualization=visualization, label="left")
                _ = targets[1].get_target_roi(src=src, visualization=visualization, label="right")
                roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                _, roi_mask = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                roi_mask = cv2.cvtColor(roi_mask, cv2.COLOR_GRAY2BGR)
                if visualization:
                    cv2.imshow("roi_mask", roi_mask)
                    cv2.waitKey(1)
                return self.hash_detector.detect_direction_hash(roi_mask)
            else: # fail to find proper roi
                return None

        else: # fail to find proper roi
            return None







if __name__ == "__main__":

    imageProcessor = ImageProcessor(video_path="src/W.h264")
    imageProcessor.fps.start()
    #while imageProcessor.fps._numFrames < 200:
    while True:
        src = imageProcessor.get_image(visualization=False)
        print(imageProcessor.get_door_alphabet(visualization=False))
        imageProcessor.fps.update()
    imageProcessor.fps.stop()
    print("[INFO] time : " + str(imageProcessor.fps.elapsed()))
    print("[INFO] FPS : " + str(imageProcessor.fps.fps()))


