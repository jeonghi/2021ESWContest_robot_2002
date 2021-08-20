import cv2
import numpy as np

class HashDetector:
    def __init__(self) -> None:
        self.east_hash = self.image_to_hash(cv2.imread('EWSN/E.png'))
        self.west_hash = self.image_to_hash(cv2.imread('EWSN/W.png'))
        self.north_hash = self.image_to_hash(cv2.imread('EWSN/N.png'))
        self.south_hash = self.image_to_hash(cv2.imread('EWSN/S.png'))
    
    @staticmethod
    def image_to_hash(img : np.ndarray) -> list:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (16, 16))
        avg = gray.mean()
        bin = 1 * (gray > avg)
        return bin
    
    @staticmethod
    def hamming_distance(src_hash : list, cmp_hash : list) -> int:
        src_hash = src_hash.reshape(1,-1)
        cmp_hash = cmp_hash.reshape(1,-1)
        # 같은 자리의 값이 서로 다른 것들의 합
        distance = (src_hash != cmp_hash).sum()
        return distance
    
     
    def detect_direction_hash(self, img : np.ndarray) -> str:
        img_hash = self.image_to_hash(img)
        direction_list = ['E', 'W', 'S', 'N']
        hash_list = [self.east_hash, self.west_hash, self.south_hash, self.north_hash]
        hdist_list = []
        
        for hash in hash_list:
            hdist_list.append(self.hamming_distance(img_hash, hash))
            
        result = hdist_list.index(min(hdist_list))
        
        return direction_list[result]


if __name__ == "__main__":
    from Sensor.ImageProcessor import ImageProcessor
    from imutils import auto_canny
    from Sensor.Target import Target
    imageProcessor = ImageProcessor(video_path='src/N.h264')
    hashDetector = HashDetector()
    while True:
        targets = []
        src = imageProcessor.get_image()
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        mask = auto_canny(mask)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in cnts:
            approx = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True)*0.02, True)
            vertice = len(approx)

            if vertice == 4 and cv2.contourArea(cnt)> 2500:
                targets.append(Target(contour=cnt))
        if targets:
            targets.sort(key= lambda x: x.get_area)
            roi = targets[0].get_target_roi(src = src, pad=10, visualization=True)
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            cv2.imshow("roi thresh", mask)
            cv2.waitKey(1)
            print(hashDetector.detect_direction_hash(roi))
