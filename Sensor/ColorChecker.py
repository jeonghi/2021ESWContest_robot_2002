import cv2
import numpy as np



# background 가 흰색이라 hue 값만으로 pixel rate 판단하면 위험할 수 있기때문에 테스트 해보고 수정할 것
class ColorPreProcessor():
    COLORS = {

        ## usage : from Colorchecker import ColorPreProcessor
        ## COLORS = ColorPreProcessor.COLORS
        "GREEN" : {
            "AREA" : {
                "upper": [[82, 212, 255], [82, 212, 255], [82, 212, 255]],
                "lower": [[21, 53, 35], [21, 53, 35], [21, 53, 35]],
            }
        },
        "BLUE" : {
            "MILK" : {
                "upper": [[121, 255, 255], [101, 255, 255], [101, 255, 255]],
                "lower": [[101, 95, 63], [81, 95, 63], [81, 95, 63]],
            },
            "ABCD" : {
                "upper": [[55, 94, 149], [55, 94, 149], [55, 94, 149]],
                "lower": [[139, 145, 186], [139, 145, 186], [139, 145, 186]],
            },
        },
        "RED" : {
            "MILK":
                {
                    "upper": [[55, 94, 149], [55, 94, 149], [55, 94, 149]],
                    "lower": [[139, 145, 186], [139, 145, 186], [139, 145, 186]],

                },
            "ABCD":
                {
                    "upper": [[55, 94, 149], [55, 94, 149], [55, 94, 149]],
                    "lower": [[139, 145, 186], [139, 145, 186], [139, 145, 186]],
                }
        }
    }





    @staticmethod
    def get_color_binary_image(src:np.array, color:dict):  # 인자로 넘겨 받은 색상만 남기도록 이진화한뒤 원본 이미지와 이진 이미지 반
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        upper1, upper2, upper3 = color["upper"]
        lower1, lower2, lower3 = color["lower"]
        img_mask1 = cv2.inRange(hsv, np.array(lower1), np.array(upper1))
        img_mask2 = cv2.inRange(hsv, np.array(lower2), np.array(upper2))
        img_mask3 = cv2.inRange(hsv, np.array(lower3), np.array(upper3))
        temp = cv2.bitwise_or(img_mask1, img_mask2)
        mask = cv2.bitwise_or(img_mask3, temp)
        k = (11, 11)
        kernel = np.ones(k, np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        return src, mask

    @staticmethod
    def get_red_mask(hue: np.array) -> np.array:
        red_upper = 145
        red_lower = 30
        if hue.dtype != np.uint8:
            hue = hue.astype(dtype=np.uint8)
        red_mask_a = np.where(hue > red_upper, hue, 0)
        red_mask_b = np.where(hue < red_lower, hue, 0)
        red_mask = cv2.bitwise_or(red_mask_a, red_mask_b)
        red_mask = np.where(red_mask == 0, red_mask, 255)
        return red_mask

    @staticmethod
    def get_blue_mask(hue: np.array) -> np.array:

        blue_upper = 135
        blue_lower = 95
        if hue.dtype != np.uint8 :
            hue = hue.astype(dtype=np.uint8)
        blue_mask = np.where(hue > blue_lower, hue, 0)
        blue_mask = np.where(hue < blue_upper, blue_mask, 0)
        blue_mask = np.where(blue_mask == 0, blue_mask, 255)
        return blue_mask

    @staticmethod
    def get_green_mask(hue: np.array) -> np.array:
        green_upper = 80
        green_lower = 20
        if hue.dtype != np.uint8:
            hue = hue.astype(dtype=np.uint8)
        green_mask = np.where(hue > green_lower, hue, 0)
        green_mask = np.where(hue < green_upper, green_mask, 0)
        green_mask = np.where(green_mask == 0, green_mask, 255)
        return green_mask

    @staticmethod
    def get_mean_value_for_non_zero(src: np.array) -> int:
        src_mean = np.true_divide(src.sum(), (src != 0).sum())
        return int(np.mean(src_mean))






if __name__ == "__main__":
    from Sensor.ImageProcessor import ImageProcessor
    imageProcessor = ImageProcessor(video_path="src/old/green_area.mp4")
    while True:
        src = imageProcessor.get_image(visualization=True)
