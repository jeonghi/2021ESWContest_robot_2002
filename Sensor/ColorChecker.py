import cv2
import numpy as np

red_upper = 145
red_lower = 30

green_upper = 85
green_lower = 35

blue_upper = 135
blue_lower = 95


def get_mean_value_for_non_zero(src: np.array) -> int:
    src_mean = np.true_divide(src.sum(), (src != 0).sum())
    return int(np.mean(src_mean))

# background 가 흰색이라 hue 값만으로 pixel rate 판단하면 위험할 수 있기때문에 테스트 해보고 수정할 것

def get_red_mask(hue: np.array, visualization:bool = False):
    if hue.dtype != np.uint8:
        hue = hue.astype(dtype=np.uint8)
    red_mask_a = np.where(hue > red_upper, hue, 0)
    red_mask_b = np.where(hue < red_lower, hue, 0)
    red_mask = cv2.bitwise_or(red_mask_a, red_mask_b)
    red_mask = np.where(red_mask == 0, red_mask, 255)
    return red_mask


def get_blue_mask(hue: np.array, visualization:bool = False):
    if hue.dtype != np.uint8:
        hue = hue.astype(dtype=np.uint8)
    blue_mask = np.where(hue > blue_lower, hue, 0)
    blue_mask = np.where(hue < blue_upper, blue_mask, 0)
    blue_mask = np.where(blue_mask == 0, blue_mask, 255)
    return blue_mask

def get_green_mask(hue: np.array, visualization:bool = False):
    if hue.dtype != np.uint8:
        hue = hue.astype(dtype=np.uint8)
    green_mask = np.where(hue > green_lower, hue, 0)
    green_mask = np.where(hue < green_upper, green_mask, 0)
    green_mask = np.where(green_mask == 0, green_mask, 255)
    return green_mask

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
        get_green_pixel_rate(src)
