from Brain.Controller import Robot
from Sensor.ImageProcessor import ImageProcessor

def main():
    robot = Robot(video_path='./Sensor/src/S.h264')
    #robot.detect_alphabet()
    robot.line_trace()


if __name__ == "__main__":
    main()
    #imageProcessor = ImageProcessor(video_path="Sensor/src/E.h264")
    #imageProcessor.fps.start()
    ##while imageProcessor.fps._numFrames < 200:
    #while True:
    #    src = imageProcessor.get_image(visualization=False)
    #    print(imageProcessor.get_door_alphabet(visualization=True))
    #    imageProcessor.fps.update()
    #imageProcessor.fps.stop()
    #print("[INFO] time : " + str(imageProcessor.fps.elapsed()))
    #print("[INFO] FPS : " + str(imageProcessor.fps.fps()))