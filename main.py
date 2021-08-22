from Brain.Controller import Robot

def main():
    robot = Robot(video_path='./Sensor/src/S.h264')
    robot.detect_alphabet()


if __name__ == "__main__":

    main()