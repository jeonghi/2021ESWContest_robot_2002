import cv2
import numpy as np
import os

class FeatureMatcher():
    def __init__(self, path, mode=3):
        self.descripter = self._set_descripter(mode=mode)
        self.path = path
        self.images = []
        self.class_names = []
        self.lst = os.listdir(path)
        if '.DS_Store' in self.lst:
            self.lst.remove('.DS_Store')
        for cl in self.lst:
            img_cur = cv2.imread(f'{self.path}/{cl}',0)
            self.images.append(img_cur)
            self.class_names.append(os.path.splitext(cl)[0])
        self.descripter_lst = self._find_descripter() #  비교기준들에 대한 디스크립터들을 미리 구해놓는다.
        print(self.class_names)

    def _set_descripter(self, mode):
        if mode == 0:
            return cv2.KAZE_create()
        elif mode == 1:
            return cv2.BRISK_create()
        elif mode == 2:
            return cv2.ORB_create()
        elif mode == 3:
            return cv2.SIFT_create() # parameter : contrastThreshold

    def _find_descripter(self):
        tmp = []
        for img in self.images:
            kp, des = self.descripter.detectAndCompute(img, None)
            tmp.append(des)
        return tmp

    def _find_class_idx(self, img, thres):
        kp2, des2 = self.descripter.detectAndCompute(img, None)
        bf = cv2.BFMatcher()
        match_lst = []
        idx = -1
        try:
            for des1 in self.descripter_lst:
                matches = bf.knnMatch(des1,des2,k=2)
                good = []
                for m, n in matches:
                    if m.distance < 0.65 * n.distance:
                        good.append([m])
                match_lst.append(len(good))
        except:
            pass
        if len(match_lst) != 0 :
            if max(match_lst) > thres:
                idx = match_lst.index(max(match_lst))

        return idx

    def get_class_name(self, img, thres=9):
        idx = self._find_class_idx(img,thres)
        if idx != -1:
            return self.class_names[idx]
        else: return None

if __name__ == "__main__":
    from Sensor.ImageProcessor import ImageProcessor
    from Sensor.Target import Target
    from imutils import auto_canny
    imageProcessor = ImageProcessor(video_path="src/S.h264")
    feature_matcher1 = FeatureMatcher(path="EWSN", mode=3)
    while True:
        targets = []
        src = imageProcessor.get_image()
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        mask = auto_canny(mask)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in cnts:
            approx = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True) * 0.02, True)
            vertice = len(approx)

            if vertice == 4 and cv2.contourArea(cnt) > 2500:
                targets.append(Target(contour=cnt))
        if not targets :
            continue
        targets.sort(key=lambda x: x.get_area)
        roi = targets[0].get_target_roi(src=src, pad=10, visualization=True)
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        #mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        cv2.imshow("roi thresh", mask)
        cv2.waitKey(1)

        class_name1 = feature_matcher1.get_class_name(mask)
        #class_name1 = feature_matcher1.get_class_name(cv2.cvtColor(cv2.resize(src1,(320,240)), cv2.COLOR_BGR2GRAY))
        if class_name1 != -1 and class_name1 != None:
            src1 = cv2.putText(src, f"Detected: {class_name1[0]}", (0, 80), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 0), 3)
        else:
            src1 = cv2.putText(src, f"Detected: None", (0, 80), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 3)
            pass
        cv2.imshow('img', src)
        cv2.waitKey(1)