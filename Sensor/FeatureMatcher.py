import cv2
import numpy as np
import os

class FeatureMatcher():
    def __init__(self, path, mode=1):
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
        self.descripter_lst = self._find_descripter()

    def _set_descripter(self, mode):
        if mode == 1:
            return cv2.AKAZE_create()
        elif mode == 2:
            return cv2.ORB_create()
        else:
            return cv2.SIFT_create()

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
                    if m.distance < 0.75 * n.distance:
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
    from ImageProcessor import ImageProcessor
    image_processor = ImageProcessor()
    feature_matcher1 = FeatureMatcher(path="RoomName", mode=3)
    while True:
        src1 = image_processor.get_image()
        class_name1 = feature_matcher1.get_class_name(cv2.cvtColor(cv2.resize(src1,(320,240)), cv2.COLOR_BGR2GRAY))
        if class_name1 != -1 and class_name1 != None:
            src1 = cv2.putText(src1, f"Detected: {class_name1}", (0, 80), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 0), 3)
        else:
            src1 = cv2.putText(src1, f"Detected: None", (0, 80), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 3)

        cv2.imshow('img', src1)
        cv2.waitKey(1)