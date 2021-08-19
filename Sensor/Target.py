import cv2
import numpy as np

class Target:
    def __init__(self, img : np.ndarray, color : str = None, target : str = None) -> None:
        self.img = img
        self.color = color
        self.target = target
    
    def get_target_roi(self, pad = 0) -> np.ndarray:
        #self.img = cv2.resize(self.img, None)
        img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        _, img_binary = cv2.threshold(img_gray, 40, 255, cv2.THRESH_BINARY_INV)
        
        _, _, stats, centrois = cv2.connectedComponentsWithStats(img_binary, connectivity=4, ltype=cv2.CV_32S)
        
        stats = sorted(stats, key=lambda x : x[4], reverse=True)
        if stats is None:
            cv2.imshow("asd", self.img)
        
        x, y, w, h, area = stats[1]
        
        min_x = x - pad
        max_x = x + w + pad
        min_y = y - pad
        max_y = y + h + pad
        if min_x <= 0:
            min_x = 0
        if max_x >= w-1:
            max_x = w-1
        if min_y <= 0:
            min_y = 0
        if max_y >= h-1:
            max_y = h-1
            
        #cv2.rectangle(self.img, (x, y), (x + w, y + h), (255, 0, 0))
        #print(x, y, w, h, area)
    
        return self.img[min_y : y + h + pad, min_x : x + w + pad]
        
    

if __name__ == "__main__":
    cap = cv2.VideoCapture("src/E.h264")
    while True:
        ret, frame = cap.read()
        #frame = cv2.imread("src/labeling_sample.jpg")
        
        if not ret:
            break
        
        target = Target(frame, "red")
        roi = target.get_target_roi(pad = 10)
        cv2.imshow("frame", roi)
        
        if cv2.waitKey(1) == 27:
            break