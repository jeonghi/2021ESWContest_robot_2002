import cv2
import numpy as np

def get_color_mask(src:np.array, const:list):
    k = cv2.getStructuringElement(cv2.MORPH_CROSS, (5,5))
    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    lower = np.array(const[0])
    upper = np.array(const[1])
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
    return mask

video = cv2.VideoCapture("Sensor/src/1116_slow0.5/black_B.mp4")
while True:
    ret, src = video.read()
    if not ret:
        video = cv2.VideoCapture("Sensor/src/1116_slow0.5/black_B.mp4")
        continue
    src = cv2.resize(src, dsize=(640, 480))
    const = [ [92, 0, 0], [124, 255, 50] ] # H S V
    mask = get_color_mask(src=src, const=const)
    cv2.imshow('src', src)
    cv2.imshow('result', mask)
    key = cv2.waitKey(1)
    if key == 27:
        break
video.release()
cv2.destroyAllWindows()