import cv2
import numpy as np
import time
import platform
import os
from imutils.video import WebcamVideoStream
from imutils.video import FileVideoStream
from imutils.video import FPS

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
        return src.copy()




if __name__ == "__main__":

    imageProcessor = ImageProcessor(video_path="")
    imageProcessor.fps.start()
    #while imageProcessor.fps._numFrames < 200:
    while True:
        src = imageProcessor.get_image(visualization=True)
        imageProcessor.fps.update()
    imageProcessor.fps.stop()
    print("[INFO] time : " + str(imageProcessor.fps.elapsed()))
    print("[INFO] FPS : " + str(imageProcessor.fps.fps()))


