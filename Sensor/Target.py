import cv2
import numpy as np


class Target:

    def __init__(self, color=None, stats=None, centroid=None, contour=None):

        if centroid is not None and stats is not None:
            (self.x, self.y, self.width, self.height, self._area) = stats
            self._center_pos = (self._center_x, self._center_y) = int(centroid[0]), int(centroid[1])
        elif contour is not None:
            (self.x, self.y, self.width, self.height) = cv2.boundingRect(contour)
            self._area = cv2.contourArea(contour)
            self._center_pos = (self._center_x, self._center_y) = (
            self.x + (self.width // 2), self.y + (self.height // 2))
        self._color = color
        self._pts = (self.x, self.y, self.width, self.height)


    def get_target_roi(self, src, pad:int=0, visualization:bool=False, label:str=None) -> np.ndarray:
        shape = (h,w) = src.shape[:2]
        min_x = self.x - pad
        max_x = self.x + self.width + pad
        min_y = self.y - pad
        max_y = self.y + self.height + pad

        min_x = 0 if min_x <= 0 else min_x
        max_x = w-1 if max_x >= w-1 else max_x
        min_y = 0 if min_y <= 0 else min_y
        max_y = h-1 if max_y >= h-1 else max_y

        roi = src[min_y:max_y, min_x:max_x]

        if visualization:
            dst = cv2.circle(src.copy(), self._center_pos, 10, (255, 255, 255), 10)
            cv2.rectangle(dst, (self.x, self.y), (self.x + self.width, self.y + self.height), (0, 0, 255))
            if pad > 0: cv2.rectangle(dst, (min_x, min_y), (max_x, max_y), (255, 255, 255))
            cv2.imshow("target", dst)
            if label:
                cv2.imshow(label, roi)
            else:
                cv2.imshow("roi", roi)
            cv2.waitKey(1)

        return roi

    def get_center_pos(self):
        return self._center_pos

    def get_area(self):
        return self._area

    def get_pts(self):
        return self._pts

def IoU(box1:Target, box2:Target) -> float:
        # box = (x1, y1, x2, y2)
        box1_area = (box1.width + 1) * (box1.height + 1)
        box2_area = (box2.width + 1) * (box2.height + 1)

        # obtain x1, y1, x2, y2 of the intersection
        x1 = max(box1.x, box2.x)
        y1 = max(box1.y, box2.y)
        x2 = min(box1.x+box1.width, box2.x+box2.width)
        y2 = min(box1.y+box1.height, box2.y+box1.height)

        # compute the width and height of the intersection
        w = max(0, x2 - x1 + 1)
        h = max(0, y2 - y1 + 1)

        inter = w * h
        iou = inter / (box1_area + box2_area - inter)
        return iou

def setLabel(src, pts, label, color=(0,255,0)):
    (x, y, w, h) = cv2.boundingRect(pts)
    pt1 = (x, y)
    pt2 = (x+w, y+h)
    cv2.rectangle(src, pt1, pt2, color, 2)
    cv2.putText(src, label, (pt1[0], pt1[1]-3), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color)

if __name__ == "__main__":
    from Sensor.ImageProcessor import ImageProcessor
    from imutils import auto_canny
    from Sensor.HashDetector import HashDetector
    imageProcessor = ImageProcessor(video_path='src/S.h264')
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

        #cv2.imshow("src", src)
        #cv2.imshow("mask", mask)
        #cv2.waitKey(1)


