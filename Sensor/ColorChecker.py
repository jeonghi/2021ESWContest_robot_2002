import cv2
import numpy as np


def check_color4roi(src:np.array) -> int:
    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    h_mean = np.true_divide(h.sum(), (h != 0).sum())
    return int(np.mean(h_mean))

# background 가 흰색이라 hue 값만으로 pixel rate 판단하면 위험할 수 있기때문에 테스트 해보고 수정할 것
def get_pixel_rate4green(src:np.array) -> int:

    width, height = src.shape[:2]
    green_upper = 85
    green_lower = 35
    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    h = np.where(h>green_lower, h, 0)
    h = np.where(h<green_upper, h, 0)
    pixel_rate = int(np.count_nonzero(h)/(width*height)*100)
    if pixel_rate > 20 :
        print("안전구역")
    else:
        print("확진구역")
    return pixel_rate

def check_alphabet_color(src:np.array) -> str:
    pass

def check_in_black(src:np.array):

    pass

def check_in_green(src:np.array):
    pass



if __name__ == "__main__":
    from Sensor.ImageProcessor import ImageProcessor
    imageProcessor = ImageProcessor(video_path="src/green_area.mp4")
    while True:
        src = imageProcessor.get_image(visualization=True)
        get_pixel_rate4green(src)
