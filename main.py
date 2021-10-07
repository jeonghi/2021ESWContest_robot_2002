from Actuator.Motion import Motion
from imutils import video
from Sensor.LineDetector import LineDetector
from Brain.Controller import Robot
from Sensor.ImageProcessor import ImageProcessor
from Sensor.VideoRecorder import VideoRecorder

import cv2
import kbhit # press any key to exit

VIDEO_PATH = "Sensor/src/debug/room_red_A.h264"    # test robot: -1    test video: [video path]
DEBUG = True # test robot: False    test local: True

def main():
    robot = Robot()
    #====================== debug ======================

    video_recorder = VideoRecorder()
    kb = kbhit.KBHit()

    print("Press ESC key to exit")
    while True:
        if kb.kbhit():
            key = ord(kb.getch())

            if key == 27: # ESC
                break

        frame = robot._image_processor.get_image()
        cv2.imshow("frame", frame)
        cv2.waitKey(10)
        video_recorder.record_frame(frame)

    #===================== function ======================
<<<<<<< HEAD
        robot._image_processor.get_room_alphabet(visualization=True)
=======
        robot.check_motion()
        #robot.setting_mode()
    

>>>>>>> parent of b6afb5d... escape room fix
    #=====================================================
    
    video_recorder.stop()
    robot.set_basic_form()

if __name__ == "__main__":
    main()