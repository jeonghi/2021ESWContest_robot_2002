import cv2
import numpy as np
from Constant import const
# background 가 흰색이라 hue 값만으로 pixel rate 판단하면 위험할 수 있기때문에 테스트 해보고 수정할 것


COLORS = {
    "RED_ABCD": {
        "SCHOOL": {
            "lower": [[0, 15, 48], [160, 15, 48]],
            "upper": [[30, 222, 184], [180, 222, 184]]
        }
    },
    "BLUE_ABCD": {
        "SCHOOL": {
            "lower": [[98, 134, 76], [98, 134, 76]],
            "upper": [[132, 255, 190], [132, 255, 190]]
        }
    }
}

class ColorPreProcessor():

    @classmethod
    def get_blue_mask4hue(cls, hue: np.array) -> np.array:
        blue_upper = 124
        blue_lower = 90
        if hue.dtype != np.uint8:
            hue = hue.astype(dtype=np.uint8)
        blue_mask = np.where(hue > blue_lower, hue, 0)
        blue_mask = np.where(hue < blue_upper, blue_mask, 0)
        blue_mask = np.where(blue_mask == 0, blue_mask, 255)
        return blue_mask

    @classmethod
    def get_red_mask4hue(cls, hue: np.array) -> np.array:
        red_upper = 155
        red_lower = 30
        if hue.dtype != np.uint8:
            hue = hue.astype(dtype=np.uint8)
        red_mask_a = np.where(hue > red_upper, hue, 0)
        red_mask_b = np.where(hue < red_lower, hue, 0)
        red_mask = cv2.bitwise_or(red_mask_a, red_mask_b)
        red_mask = np.where(red_mask == 0, red_mask, 255)
        return red_mask

    @classmethod
    def get_color_mask(cls, src:np.array, const:list):
        k = cv2.getStructuringElement(cv2.MORPH_CROSS, (5,5))
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        lower = np.array(const[0])
        upper = np.array(const[1])
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
        return mask

    @classmethod
    def get_alphabet_mask(cls, src: np.array) -> np.array:
        red_mask = cls.get_red_mask(src)
        blue_mask = cls.get_blue_mask(src)
        return cv2.bitwise_or(red_mask, blue_mask)

    @classmethod
    def get_blue_mask(cls, src: np.array) -> np.array:
        return cls.get_color_mask(src, const=const.BLUE_RANGE)

    @classmethod
    def get_green_mask(cls, src: np.array) -> np.array:
        return cls.get_color_mask(src, const=const.GREEN_RANGE)

    @classmethod
    def get_mean_value_for_non_zero(cls, src: np.array) -> int:
        src_mean = np.true_divide(src.sum(), (src != 0).sum())
        return int(np.mean(src_mean))

    @classmethod
    def get_red_or_blue4hue(cls, src: np.array) -> str:
        hls = cv2.cvtColor(src, cv2.COLOR_BGR2HLS)
        h, l, s = cv2.split(hls)
        _, mask = cv2.threshold(s, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        h = cv2.bitwise_and(h, h, mask=mask)
        red_mask = ColorPreProcessor.get_red_mask4hue(h)
        blue_mask = ColorPreProcessor.get_blue_mask4hue(h)
        answer = "RED" if np.count_nonzero(red_mask) > np.count_nonzero(blue_mask) else "BLUE"
        return answer

    @classmethod
    def get_red_or_blue(cls, src: np.array) -> str:
        red_mask = ColorPreProcessor.get_red_mask(src)
        blue_mask = ColorPreProcessor.get_blue_mask(src)
        answer = "RED" if np.count_nonzero(red_mask) > np.count_nonzero(blue_mask) else "BLUE"
        return answer
    
    @classmethod
    def get_red_mask(cls, src: np.array) -> np.array:
        mask1 = cls.get_color_mask(src, const=const.RED_RANGE1)
        mask2 = cls.get_color_mask(src, const=const.RED_RANGE2)
        return cv2.bitwise_or(mask1, mask2)

    @classmethod
    def get_yellow_mask(cls, src:np.array) -> np.array:
        return cls.get_color_mask(src, const=const.YELLOW_RANGE)

    @classmethod
    def get_black_mask(cls, src:np.array) -> np.array:
        return cls.get_color_mask(src, const=const.BLACK_RANGE)
