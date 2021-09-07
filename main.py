from Actuator.Motion import Motion
from imutils import video
from Sensor.LineDetector import LineDetector
from Brain.Controller import Robot
from Sensor.ImageProcessor import ImageProcessor
import cv2

def main():
    robot = Robot()
    #robot.detect_alphabet()
    robot.line_tracing()
    

def test():
    imageProcessor = ImageProcessor(video_path="Sensor/src/ewsn.mp4")
    imageProcessor.fps.start()
    #while imageProcessor.fps._numFrames < 200:
    while True:
        src = imageProcessor.get_image(visualization=True)
        print(imageProcessor.get_door_alphabet(visualization=True))
        imageProcessor.fps.update()
    imageProcessor.fps.stop()
    print("[INFO] time : " + str(imageProcessor.fps.elapsed()))
    print("[INFO] FPS : " + str(imageProcessor.fps.fps()))

if __name__ == "__main__":
    main()
