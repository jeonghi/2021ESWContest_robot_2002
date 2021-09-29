import cv2
import imutils
import numpy as np

class GreenLineDetector:
    def __init__(self):
        pass


    def draw_lines(self, src, lines, mode = 'all', thickness=2):
        if mode == 'all':
            thickness = 2
            color=[0,255,0]
            for line in lines:
                for x1, y1, x2, y2 in line:
                    cv2.line(src, (x1, y1), (x2, y2), color, thickness)
        if mode == 'fit':
            thickness = 10
            color=[0,255,0]
            for line in lines:
                cv2.line(src, (lines[0], lines[1]), (lines[2], lines[3]), color, thickness)

    def get_fitline(self, f_lines, size):
        lines = np.squeeze(f_lines)
        lines = lines.reshape(size,2)
        #middle=int(lines.mean(axis=0)[1])
        min_x = int(lines.min(axis=0)[0])
        max_x = int(lines.max(axis=0)[0])
        min_y = int(lines.min(axis=0)[1])
        max_y = int(lines.max(axis=0)[1])
        #H = [max_x, middle, min_x, middle]
        fitline = [max_x, max_y, min_x, min_y]
        fitline_degree = (np.arctan2(fitline[1] - fitline[3], fitline[0] - fitline[2]) * 180) / np.pi
        return fitline, fitline_degree
            
                    
    def get_green_H_lines(self, src):
        
        green_lower = np.array([25, 52, 72])
        green_upper = np.array([102, 255, 255])

        kernel = np.ones((5, 5), np.uint8)

        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        hue, saturation, value = cv2.split(hsv)

        green_mask = cv2.inRange(hsv, green_lower, green_upper)
        green_mask = cv2.erode(green_mask, kernel, iterations=2)
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
        green_mask = cv2.dilate(green_mask, kernel, iterations=1)
        
        _, binary = cv2.threshold(saturation, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        green_area_mask = cv2.bitwise_and(green_mask, binary)
        
        edge = imutils.auto_canny(green_area_mask)
        
        lines = cv2.HoughLinesP(edge, 1, np.pi / 180, 90, minLineLength = 50, maxLineGap = 30)
        lines = np.squeeze(lines)
        
        if len(lines.shape) == 0:
            return []
        elif len(lines.shape) == 1:
            slope_degree = (np.arctan2(lines[1] - lines[3], lines[0] - lines[2]) * 180) / np.pi
        else:
            slope_degree = (np.arctan2(lines[:,1] - lines[:,3], lines[:,0] - lines[:,2]) * 180) / np.pi
            
        H = lines[np.abs(slope_degree) > 160]
        H_degree = slope_degree[np.abs(slope_degree)>160]
        H = H[:,None]

        return H

    def get_green_lines(self, src):
        green_H_info = {"IS_GREEN_H": True , "MAX": [0 , 0], "MIN": [0, 0]}
        H = self.get_green_H_lines(src)

        if len(H) != 0:
            size = int(H.shape[0]*H.shape[2]/2)
            fit_H, fit_H_degree = self.get_fitline(H, size)
            #self.draw_lines(src, H)
            self.draw_lines(src, fit_H, 'fit')
            # print(fit_H_degree) # 0 ~ 0.5 사이면 평행

        return green_H_info, src
        #cv2.imshow("edge", edge)
        #cv2.imshow("and_mask", green_area_mask)

if __name__ == "__main__":
    video = cv2.VideoCapture("./Sensor/src/line_test/debug_video.avi")
    green_detector = GreenLineDetector()
    while True:
        ret, src = video.read()
        if not ret:
            video = cv2.VideoCapture("./Sensor/src/line_test/debug_video.avi")
            continue
        src = cv2.resize(src, dsize=(640,480))
        green_H_info, result = green_detector.get_green_lines(src)
        cv2.imshow('result',result)
        key = cv2.waitKey(1)
        if key == 27:
            break
    video.release()
    cv2.destroyAllWindows()