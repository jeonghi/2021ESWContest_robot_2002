import cv2
import numpy as np

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


    @staticmethod
    def get_color_binary_image(src:np.array, color:dict):  # 인자로 넘겨 받은 색상만 남기도록 이진화한뒤 원본 이미지와 이진 이미지 반
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        upper1, upper2 = color["upper"]
        lower1, lower2 = color["lower"]
        img_mask1 = cv2.inRange(hsv, np.array(lower1), np.array(upper1))
        img_mask2 = cv2.inRange(hsv, np.array(lower2), np.array(upper2))
        mask = cv2.bitwise_or(img_mask1, img_mask2)
        k = (5, 5)
        kernel = np.ones(k, np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        return mask

    @staticmethod
    def get_alphabet_mask(src: np.array) -> np.array:
        red_mask = ColorPreProcessor.get_color_binary_image(src=src, color=COLORS["RED_ABCD"]["SCHOOL"])
        blue_mask = ColorPreProcessor.get_color_binary_image(src=src, color=COLORS["BLUE_ABCD"]["SCHOOL"])
        mask = cv2.bitwise_or(red_mask, blue_mask)
        #cv2.imshow("mask", mask)
        #cv2.waitKey(1)
        return mask

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
        #print(src)
        src_mean = np.true_divide(src.sum(), (src != 0).sum())
        #print(src_mean)
        return int(np.mean(src_mean))

    @staticmethod
    def check_red_or_blue(src: np.array) -> str:

        hls = cv2.cvtColor(src, cv2.COLOR_BGR2HLS)
        h, l, s = cv2.split(hls)
        _, mask = cv2.threshold(s, 30, 255, cv2.THRESH_BINARY)
        h = cv2.bitwise_and(h, h, mask=mask)
        red_mask = ColorPreProcessor.get_red_mask(h)
        cv2.imshow("red", red_mask)
        blue_mask = ColorPreProcessor.get_blue_mask(h)
        cv2.imshow("blue", blue_mask)
        answer = "RED" if np.count_nonzero(red_mask) > np.count_nonzero(blue_mask) else "BLUE"
        return answer
    
    @staticmethod
    def get_red_box_mask(src: np.array) -> np.array:
        mask = ColorPreProcessor.get_color_binary_image(src=src, color=COLORS["RED_ABCD"]["SCHOOL"])
        return mask
        

    @staticmethod
    def get_yellow_mask4hue(hue: np.array) -> np.array:
        yellow_upper = 60
        yellow_lower = 10
        if hue.dtype != np.uint8:
            hue = hue.astype(dtype=np.uint8)
        yellow_mask = np.where(hue > yellow_lower, hue, 0)
        yellow_mask = np.where(hue < yellow_upper, yellow_mask, 0)
        yellow_mask = np.where(yellow_mask == 0, yellow_mask, 255)
        return yellow_mask

    @staticmethod
    def get_yellow_mask4hsv(src:np.array) -> np.array:
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        yellow_lower = np.array([12, 26, 116])
        yellow_upper = np.array([48, 128, 182])
        mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
        return mask

    @staticmethod
    def get_black_mask(src:np.array) -> np.array:
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        black_lower = np.array([0,0,0])
        black_upper = np.array([180,255,70])
        mask = cv2.inRange(hsv, black_lower, black_upper)
        return mask





if __name__ == "__main__":
    from ImageProcessor import ImageProcessor
    imageProcessor = ImageProcessor(video_path="src/old/green_area.mp4")
    while True:
        src = imageProcessor.get_image()
        ColorChecker.get_alphabet_mask(src=src)
