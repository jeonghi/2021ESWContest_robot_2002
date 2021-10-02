import cv2
import numpy as np
import math

class Black:
    def __init__(self):
        pass

    def mask_color(self, src, color = 'YELLOW'):
        if color == 'YELLOW':
            hls = cv2.cvtColor(src, cv2.COLOR_BGR2HLS)
            h, l, s = cv2.split(hls)
            ret, mask = cv2.threshold(s, 70, 255, cv2.THRESH_BINARY)
            src = cv2.bitwise_and(src, src, mask = mask)
            match_lower = np.array([10,40,95]) #yellow_lower
            match_upper = np.array([40, 220, 220]) #yellow_upper

        if color == 'GREEN':
            hls = cv2.cvtColor(src, cv2.COLOR_BGR2HLS)
            h, l, s = cv2.split(hls)
            ret, mask = cv2.threshold(s, 70, 255, cv2.THRESH_BINARY)
            src = cv2.bitwise_and(src, src, mask = mask)
            match_lower = np.array([20, 20, 20]) #green_lower
            match_upper = np.array([80,  255, 255]) #green_upper  

        if color == 'BLACK': 
            hls = cv2.cvtColor(src, cv2.COLOR_BGR2HLS)
            h, l, s = cv2.split(hls)
            ret, mask = cv2.threshold(s, 70, 255, cv2.THRESH_BINARY)
            src = cv2.bitwise_and(src, src, mask = mask)
            match_lower = np.array([20, 20, 20]) #green_lower
            match_upper = np.array([80,  255, 255]) #green_upper 

        src = cv2.GaussianBlur(src, (5, 5), 0)
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, match_lower, match_upper)
        return mask


    def get_mask(self, src, color= 'YELLOW'):
        mask = self.mask_color(src, color)
        edges = cv2.Canny(mask, 75, 150)

        return mask, edges

if __name__ == "__main__":
    video = cv2.VideoCapture("./Sensor/src/green_room_test/case2.h264")
    black = Black()
    while True:
        ret, src = video.read()
        if not ret:
            video = cv2.VideoCapture("./Sensor/src/green_room_test/case2.h264")
            continue
        src = cv2.resize(src, dsize=(640, 480))

        hsv_image = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        #val_S = 10
        #val_V = 30
        #array = np.full(hsv_image.shape, (0, val_S, val_V), dtype=np.uint8)
        #val_add_image = cv2.add(hsv_image, array)
        #src = cv2.cvtColor(val_add_image, cv2.COLOR_HSV2BGR)

        mask, edges = black.get_mask(src, color = 'BLACK')
        cv2.imshow('src', src)
        cv2.imshow('mask', mask)
        cv2.imshow('yellow_edges', edges)
        key = cv2.waitKey(1)
        if key == 27:
            break
    video.release()
    cv2.destroyAllWindows()