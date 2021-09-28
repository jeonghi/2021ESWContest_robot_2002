import cv2
import numpy as np
from matplotlib import pyplot as plt

if __name__ == "__main__":
    video = cv2.VideoCapture("./Sensor/src/line_test/return_line.h264")
    while True:
        ret, src = video.read()
        if not ret:
            video = cv2.VideoCapture("./Sensor/src/line_test/return_line.h264")
            continue
        origin_image = cv2.resize(src, dsize=(640,480))
        hsv_image = cv2.cvtColor(origin_image, cv2.COLOR_BGR2HSV)

        val_S = 0
        val_V = 100
        array = np.full(hsv_image.shape, (0,val_S,val_V), dtype=np.uint8)

        val_add_image = cv2.add(hsv_image, array)

        print('BGR : \t',origin_image[55,116,:])
        print('hsv : \t',hsv_image[55,116,:])
        print('hsv 밝기(v) 증가 : \t',val_add_image[55,116,:])

        val_add_image = cv2.cvtColor(val_add_image, cv2.COLOR_HSV2BGR)
        image = np.concatenate((origin_image,val_add_image), axis=1)
        cv2.imshow('result',image)
        key = cv2.waitKey(1)
        if key == 27:
            break
    video.release()
    cv2.destroyAllWindows()