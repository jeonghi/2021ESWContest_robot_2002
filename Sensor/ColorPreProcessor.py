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
    def get_blue_mask4alphabet(cls, src: np.array):
        return cls.get_color_mask(src, const=const.BLUE_ALPHABET_RANGE)


    @classmethod
    def get_blue_mask4box(cls, src: np.array):
        return cls.get_color_mask(src, const=const.BLUE_BOX_RANGE)

    @classmethod
    def get_red_mask4alphabet(cls, src: np.array):
        l = cls.get_color_mask(src, const=const.RED_ALPHABET_RANGE1)
        r = cls.get_color_mask(src, const=const.RED_ALPHABET_RANGE2)
        return cv2.bitwise_or(l, r)

    @classmethod
    def get_red_mask4box(cls, src: np.array):
        l = cls.get_color_mask(src, const=const.RED_BOX_RANGE1)
        r = cls.get_color_mask(src, const=const.RED_BOX_RANGE2)
        return cv2.bitwise_or(l, r)


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
        red_mask = cls.get_red_mask4alphabet(src)
        blue_mask = cls.get_blue_mask4alphabet(src)
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
        red_mask = ColorPreProcessor.get_red_mask4alphabet(src)
        blue_mask = ColorPreProcessor.get_blue_mask4alphabet(src)
        answer = "RED" if np.count_nonzero(red_mask) > np.count_nonzero(blue_mask) else "BLUE"
        return answer

    @classmethod
    def get_red_or_blue(cls, src: np.array) -> str:
        red_mask = ColorPreProcessor.get_red_mask4alphabet(src)
        blue_mask = ColorPreProcessor.get_blue_mask4alphabet(src)
        answer = "RED" if np.count_nonzero(red_mask) > np.count_nonzero(blue_mask) else "BLUE"
        return answer


    @classmethod
    def get_yellow_mask(cls, src:np.array) -> np.array:
        return cls.get_color_mask(src, const=const.YELLOW_RANGE)

    @classmethod
    def get_black_mask(cls, src:np.array) -> np.array:
        return cls.get_color_mask(src, const=const.BLACK_RANGE)
