from Sensor.LineDetector import LineDetector
from Brain.Controller import Robot
from Sensor.ImageProcessor import ImageProcessor
import cv2

def main():
    robot = Robot(video_path="./Sensor/src/ewsn.mp4")
    #robot.detect_alphabet()
    robot.line_tracing()

def test():
    imageProcessor = ImageProcessor(video_path="Sensor/src/ewsn.mp4")
    imageProcessor.fps.start()
    #while imageProcessor.fps._numFrames < 200:
    while True:
        src = imageProcessor.get_image(visualization=True)
        #print(imageProcessor.get_door_alphabet(visualization=True))
        print(imageProcessor.get_slope_degree())
        imageProcessor.fps.update()
    imageProcessor.fps.stop()
    print("[INFO] time : " + str(imageProcessor.fps.elapsed()))
    print("[INFO] FPS : " + str(imageProcessor.fps.fps()))

if __name__ == "__main__":
        main()
    #test()
    
    # imageProcessor = ImageProcessor(video_path="Sensor/src/t.mp4")
    # lineDetector = LineDetector()

    # while True:
    #     src = imageProcessor.get_image(visualization=False)
    #     src = cv2.resize(src, dsize=(480, 640))
    #     answer, src = lineDetector.get_all_lines(src)
    #     print(answer)
        
    #     cv2.imshow('src', src)
    #     cv2.waitKey(100)
    #     #print(imageProcessor.get_slope_degree())
    #     imageProcessor.fps.update()