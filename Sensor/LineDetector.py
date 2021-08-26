import cv2
import numpy as np

class LineDetector:
    def __init__(self):
        pass
    
    def mask_color(self, img):
        yellow_lower = np.array([18, 94, 140])
        yellow_upper = np.array([48, 255, 255])
        
        img = cv2.GaussianBlur(img, (5, 5), 0)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
            
        return mask
    
    def get_line(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        yellow_mask = self.mask_color(img)
        yellow_edges = cv2.Canny(yellow_mask, 75, 150)
        
        line_arr = cv2.HoughLinesP(yellow_edges, 1, 1 * np.pi/180, 30, np.array([]), minLineLength=100, maxLineGap=150)
        line_arr = np.squeeze(line_arr)

        temp = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        lines = line_arr[:,None]
        
        return lines
    
    def get_fitline(self, img, f_lines):
        lines = np.squeeze(f_lines)
        lines = lines.reshape(lines.shape[0] * 2, 2) 
        
        height, width = img.shape[:2]
        output = cv2.fitLine(lines, cv2.DIST_L2, 0, 0.01, 0.01)
        vx, vy, x, y = output[0], output[1], output[2], output[3]
        x1, y1 = int(((height - 1) - y) / vy * vx + x), height - 1
        x2, y2 = int(((height / 2 + 200) - y) / vy * vx + x), int(height / 2 + 200)
        
        result = [x1, y1, x2, y2]
        return result