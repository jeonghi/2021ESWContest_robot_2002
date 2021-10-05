from Actuator.Motion import Motion
from imutils import video
from Sensor.LineDetector import LineDetector
from Brain.Controller import Robot
from Sensor.ImageProcessor import ImageProcessor
from Sensor.VideoRecorder import VideoRecorder
from collections import deque
import cv2
import kbhit # press any key to exit
import time


def main():
    robot = Robot()
    #====================== debug ======================

    video_recorder = VideoRecorder()
    kb = kbhit.KBHit()
    grabbed_head_moving = ["begin", "HIGH", "LOW", "MIDDLE", "end"]
    flag = -1
    dq = deque(grabbed_head_moving)
    dq.rotate(flag)

    print("Press ESC key to exit")
    while True:
        if kb.kbhit():
             key = ord(kb.getch())

             if key == 27: # ESC
                 break

        frame = robot._image_processor.get_image()
        video_recorder.record_frame(frame)

    #===================== function ======================

        #robot.tracking_cube()
        #robot.find_yellow_corner_for_out_room()


        if dq[0] == "begin":
            flag = -1
            robot._motion.turn(dir="LEFT", grab=True, loop=2)
            time.sleep(1)
        elif dq[0] == "end":
            flag = 1
            robot._motion.turn(dir="LEFT", grab=True, loop=2)
            time.sleep(1)
        else:
            robot._motion.move_arm(dir=dq[0])
            time.sleep(1)
        dq.rotate(flag)



    #=====================================================

    video_recorder.stop()
    robot.set_basic_form()

if __name__ == "__main__":
    main()
