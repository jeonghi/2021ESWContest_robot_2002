from Actuator.Motion import Motion
from imutils import video
from Sensor.LineDetector import LineDetector
from Brain.Controller_new import Robot
from Sensor.ImageProcessor import ImageProcessor
import cv2

def main():
    robot = Robot()
    robot.return_line()

if __name__ == "__main__":
    main()
