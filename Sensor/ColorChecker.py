import cv2
import numpy as np


def check_color4roi(src:np.array) -> int:
    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    h_mean = np.true_divide(h.sum(), (h != 0).sum())
    return int(np.mean(h_mean))

# background 가 흰색이라 hue 값만으로 pixel rate 판단하면 위험할 수 있기때문에 테스트 해보고 수정할 것
def get_pixel_rate4green(src:np.array) -> int:
    # ostu threshold 적용 background: White target: Black, Green
    # white -> true 가 되므로 inv 해줘야함
    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)


    width, height = src.shape[:2]

    green_upper = 85
    green_lower = 35

    red_upper = 145
    red_lower = 30

    blue_upper = 135
    blue_lower = 95

    h = h.astype(v.dtype)
    # red mask
    red_mask_a = np.where(h>red_upper, h, 0)
    red_mask_b = np.where(h<red_lower, h, 0)
    red_mask = cv2.bitwise_or(red_mask_a, red_mask_b)
    red_mask = np.where(red_mask==0, red_mask, 255)

    # blue mask
    blue_mask = np.where(h > blue_lower, h, 0)
    blue_mask = np.where(h < blue_upper, blue_mask, 0)
    blue_mask = np.where(blue_mask==0, blue_mask, 255)

    # mask denoise
    mask = cv2.bitwise_or(red_mask, blue_mask)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.bitwise_not(mask)

    # ostu thresholding
    _, roi_mask = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    roi_mask = cv2.morphologyEx(roi_mask, cv2.MORPH_OPEN, kernel)
    roi_mask = cv2.morphologyEx(roi_mask, cv2.MORPH_CLOSE, kernel)

    # masking
    roi_mask = cv2.bitwise_and(mask, roi_mask)

    h = cv2.bitwise_and(h, h, mask=roi_mask)
    h_mean = np.true_divide(h.sum(), (h != 0).sum())
    # pixel_rate = int(np.count_nonzero(h)/(width*height)*100)
    # return pixel_rate
    #dst = cv2.bitwise_and(src, src, mask=roi_mask)
    #cv2.imshow("dst", dst)
    #cv2.waitKey(1)
    if green_lower <= h_mean <= green_upper:
        return "GREEN"
    else:
        return "BLACK"

def check_alphabet_color(src:np.array) -> str:
    pass

def check_in_black(src:np.array):

    pass

def check_in_green(src:np.array):
    pass



if __name__ == "__main__":
    from Sensor.ImageProcessor import ImageProcessor
    imageProcessor = ImageProcessor(video_path="src/old/green_area.mp4")
    while True:
        src = imageProcessor.get_image(visualization=True)
        get_pixel_rate4green(src)
