import cv2
import numpy as np


class Target:

    def __init__(self, name=None, color=None, stats=None, centroid=None, contour=None):

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
        self._name = name


    def get_target_roi(self, src, pad:int=0, visualization:bool=False, label:str=None, color=(255,255,255)) -> np.ndarray:
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
            dst = cv2.circle(src.copy(), self._center_pos, 10, color, 10)
            cv2.rectangle(dst, (self.x, self.y), (self.x + self.width, self.y + self.height), color, 3)
            if pad > 0: cv2.rectangle(dst, (min_x, min_y), (max_x, max_y), color, 1)
            if label:
                pt1 = (self.x, self.y)
                pt2 = (self.x + self.width, self.y + self.height)
                cv2.rectangle(dst, pt1, pt2, color, 2)
                cv2.putText(dst, label, (pt1[0], pt1[1] - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color)
                cv2.imshow(label, roi)
            else:
                cv2.imshow("roi", roi)
            cv2.imshow("target", dst)
            cv2.waitKey(1)

        return roi

    def get_color(self):
        return self._color

    def get_center_pos(self):
        return self._center_pos

    def get_area(self):
        return self._area

    def get_pts(self):
        return self._pts

    def set_color(self, color:str):
        self._color = color
        return

    def set_name(self, name:str):
        self._name = name
        return

    def get_name(self):
        return self._name

    @staticmethod
    def compute_iou4target(box1, box2) -> float: # (box1 : Target, box2 : Target) -> return Target Object
            # box = (x1, y1, x2, y2)
            box1_area = (box1.width + 1) * (box1.height + 1)
            box2_area = (box2.width + 1) * (box2.height + 1)

            # obtain x1, y1, x2, y2 of the intersection
            x1 = max(box1.x, box2.x)
            y1 = max(box1.y, box2.y)
            x2 = min(box1.x+box1.width, box2.x+box2.width)
            y2 = min(box1.y+box1.height, box2.y+box2.height)

            # compute the width and height of the intersection
            w = max(0, x2 - x1 + 1)
            h = max(0, y2 - y1 + 1)

            inter = w * h
            iou = inter / (box1_area + box2_area - inter)
            return iou

    @staticmethod
    def non_maximum_suppression4targets(targets1:list, targets2:list, threshold:float): # -> return Target Object
        maximum_set = None
        if targets1 and targets2:
            for target1 in targets1:
                for target2 in targets2:
                    iou = Target.compute_iou4target(target1, target2)
                    if iou > threshold:
                        threshold = iou
                        maximum_set = (target1, target2)

        if maximum_set :
            t1: Target = maximum_set[0]
            t2: Target = maximum_set[1]
            # obtain x1, y1, x2, y2 of the intersection
            x1 = max(t1.x, t2.x)
            y1 = max(t1.y, t2.y)
            x2 = min(t1.x + t1.width, t2.x + t2.width)
            y2 = min(t1.y + t1.height, t2.y + t2.height)

            # compute the width and height of the intersection
            width = max(0, x2 - x1 + 1)
            height = max(0, y2 - y1 + 1)
            area = width * height
            centroid = (center_x, center_y) = (x1 + (width//2), y1 + (height//2))
            stats = (x1, y1, width, height, area)

            return Target(color=t1.get_color(), stats=stats, centroid=centroid)
        else:
            return None


def setLabel(src, pts, label=None, color=(0,255,0)):
    if type(pts) == type(np.array([])) :
        (x, y, w, h) = cv2.boundingRect(pts)
    else:
        (x, y, w, h) = pts
    pt1 = (x, y)
    pt2 = (x+w, y+h)
    cv2.rectangle(src, pt1, pt2, color, 2)
    if label is not None:
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
            print(hashDetector.detect_alphabet_hash(roi))

        #cv2.imshow("src", src)
        #cv2.imshow("mask", mask)
        #cv2.waitKey(1)


