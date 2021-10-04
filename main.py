from Actuator.Motion import Motion
from imutils import video
from Sensor.LineDetector import LineDetector
from Brain.Controller import Robot
from Sensor.ImageProcessor import ImageProcessor
from Sensor.VideoRecorder import VideoRecorder

import cv2
import kbhit # press any key to exit

def main():
    #robot = Robot()
    image_processor = ImageProcessor("Sensor/src/door_test/doortest_E.h264")
    #====================== debug ======================

    video_recorder = VideoRecorder()
    kb = kbhit.KBHit()

    print("Press ESC key to exit")
    while True:
        if kb.kbhit():
            key = ord(kb.getch())
        
            if key == 27: # ESC
                break

        #frame = robot._image_processor.get_image()
        #video_recorder.record_frame(frame)

    #===================== function ======================

        #robot.tracking_cube()
        #robot.find_yellow_corner_for_out_room()
        print(image_processor.get_door_alphabet(visualization=True))


    #=====================================================

    #video_recorder.stop()
    #robot.set_basic_form()

if __name__ == "__main__":
    main()
