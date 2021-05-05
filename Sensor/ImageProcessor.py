import cv2
import numpy as np
import time
from imutils.video import WebcamVideoStream
from imutils.video import FileVideoStream
from imutils.video import FPS


class ImageProcessor:

    def __init__(self):
        #self.cam = WebcamVideoStream(-1).start()  # 이미지 공급 쓰레드 인자값 무적권 -1 줘야해 ! ( 라이브 용, 라즈베리파이 캠 용)

        # ****** 디버깅 영상용 이미지 공급 쓰레드 , 라즈베리파이 캠 키고 하려면 아래 주석처리
         video_path = "./src/green_area.mp4"
         self.cam = FileVideoStream(video_path).start()
        # ******

        self.fps = FPS()  # 개발때 알고리즘 fps 체크하기 위한 모듈. 실전에서는 필요없음
        shape = (self.height, self.width, _) = self.get_image().shape
        print(shape)  # 이미지 세로, 가로 (행, 열) 정보 출력
        time.sleep(2)  # 카메라 포트 여는 시간 반영해서 슬립 조금 줌.

    def get_image(self, visualization=False):
        src = self.cam.read().copy()
        if visualization:
            cv2.imshow("Src", src)
            cv2.waitKey(1)
        return src

    def canny(self, visualization=False):
        from imutils import auto_canny
        src = self.get_image()
        dst = auto_canny(src)
        if visualization:
            cv2.imshow("Canny", dst)
            cv2.waitKey(1)
        return dst


if __name__ == "__main__":

    imageProcessor = ImageProcessor()
    imageProcessor.fps.start()
    while imageProcessor.fps._numFrames < 200:
        _ = imageProcessor.get_image()
        imageProcessor.fps.update()
    imageProcessor.fps.stop()
    print("[INFO] time : " + str(imageProcessor.fps.elapsed()))
    print("[INFO] FPS : " + str(imageProcessor.fps.fps()))


