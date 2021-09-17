import cv2
import numpy as np

class VideoRecorder:
    def __init__(self):
        fourcc = cv2.VideoWriter_fourcc(*"DIVX")
        self.video_recorder = cv2.VideoWriter('debug_vedio.avi', fourcc, 30.0, (640, 480))

    def record_frame(self, frame):
        self.video_recorder.write(frame)
        #cv2.waitKey(60)

    def stop(self):
        self.video_recorder.release()