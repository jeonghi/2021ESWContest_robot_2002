import cv2
import numpy as np
from Actuator.Motion import Motion

class LineDetector:
    def __init__(self):
        pass

    def draw_lines(self, src, lines, what_line, mode = 'all', thickness=2):
        if mode == 'all':
            thickness = 2
            if what_line == 'vertical':
                color=[0, 0, 255]
            elif what_line == 'horizontal':
                color=[0,255,0]
            else:
                color=[255,255,255]
            for line in lines:
                for x1,y1,x2,y2 in line:
                    cv2.line(src, (x1, y1), (x2, y2), color, thickness)
    
        if mode == 'fit':
            thickness = 10
            if what_line == 'vertical':
                color=[255, 0, 255]
            elif what_line == 'horizontal':
                color=[0,255,255]
            else:
                color=[255,255,255]
            for line in lines:
                cv2.line(src, (lines[0], lines[1]), (lines[2], lines[3]), color, thickness)

    def mask_color(self, src):
        yellow_lower = np.array([18, 94, 140])
        yellow_upper = np.array([48, 255, 255])
        src = cv2.GaussianBlur(src, (5, 5), 0)
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
        return mask

    def get_lines(self, src):
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        yellow_mask = self.mask_color(src)
        yellow_edges = cv2.Canny(yellow_mask, 75, 150)
        lines = cv2.HoughLinesP(yellow_edges, 1, 1 * np.pi/180, 30, np.array([]), minLineLength=100, maxLineGap=150)
        lines = np.squeeze(lines)
    
        if len(lines.shape) == 0:
            return [], [], []
        elif len(lines.shape) == 1 :
            return [], [], []
        else:
            slope_degree = (np.arctan2(lines[:,1] - lines[:,3], lines[:,0] - lines[:,2]) * 180) / np.pi
        
            horizontal_lines = lines[np.abs(slope_degree) > 160]
            horizontal_slope_degree = slope_degree[np.abs(slope_degree)>160]
            horizontal_lines = horizontal_lines[:,None]
    
            lines = lines[np.abs(slope_degree) < 150]
            slope_degree = slope_degree[np.abs(slope_degree)< 150]
    
            vertical_lines = lines[np.abs(slope_degree) < 100]
            vertical_slope_degree = slope_degree[np.abs(slope_degree)<100]
            vertical_lines = vertical_lines[np.abs(vertical_slope_degree) > 80]
            vertical_slope_degree = vertical_slope_degree[np.abs(vertical_slope_degree)>80] 
            vertical_lines = vertical_lines[:,None]
            lines = lines[:,None]
            return lines, horizontal_lines, vertical_lines
    
    def get_fitline(self, src, f_lines, size, what_line):
        lines = np.squeeze(f_lines)
        lines = lines.reshape(size,2)
        if what_line == 'vertical':
            output = cv2.fitLine(lines,cv2.DIST_L2,0, 0.01, 0.01)
            vx, vy, x, y = output[0], output[1], output[2], output[3]
            x1, y1 = int(((src.shape[0]-1)-y)/vy*vx + x) , src.shape[0]-1
            x2, y2 = int(((src.shape[0]/2+200)-y)/vy*vx + x) , int(src.shape[0]/2)
            result = [x1,y1,x2,y2]
        else:
            middle=int(lines.mean(axis=0)[1])
            max_x = int(lines.max(axis=0)[0])
            result = [max_x, middle, 0, middle]
        return result
    
    def get_fitline__(self, img, f_lines): # 대표선 구하기   
        lines = np.squeeze(f_lines)
        if len(lines.shape) == 1:
            lines = lines.reshape(int(lines.shape[0]/2),2)
        else:
            lines = lines.reshape(lines.shape[0]*2,2)
        output = cv2.fitLine(lines,cv2.DIST_L2,0, 0.01, 0.01)
        vx, vy, x, y = output[0], output[1], output[2], output[3]
        x1, y1 = int(((img.shape[0]-1)-y)/vy*vx + x) , img.shape[0]-1
        x2, y2 = int(((img.shape[0]/2+200)-y)/vy*vx + x) , int(img.shape[0]/2+200)
    
        result = [x1,y1,x2,y2]
        return result


    def get_all_lines(self, src):
        answer = [0, None, 0, None, 0, 0] # 현재 방향(동작 보정 각도), vertical, vertical-x, horizontal, horizontal-y, horizontal-endx
        lines, horizontal_lines, vertical_lines = self.get_lines(src)

        temp = np.zeros((src.shape[0], src.shape[1], 3), dtype=np.uint8)

        if len(lines)!=0:
            size = int(lines.shape[0]*2)
            fit_line = self.get_fitline__(src, lines)
            self.draw_lines(temp, fit_line, 'lines', 'fit')
            robot_degree = (np.arctan2(fit_line[1] - fit_line[3], fit_line[0] - fit_line[2]) * 180) / np.pi
            answer[0] = robot_degree
            src = cv2.addWeighted(src, 1, temp, 1., 0.)
    
        if len(vertical_lines)!=0:
            size = int(vertical_lines.shape[0]*vertical_lines.shape[2]/2)
            vertical_fit_line = self.get_fitline(src, vertical_lines, size, 'vertical')
            answer[1] = 'vertical'
            answer[2] = vertical_fit_line[0]
            self.draw_lines(temp, vertical_lines, 'vertical')
            self.draw_lines(temp, vertical_fit_line, 'vertical', 'fit')
            src = cv2.addWeighted(src, 1, temp, 1., 0.)
    
        if len(horizontal_lines)!=0:
            size = int(horizontal_lines.shape[0]*horizontal_lines.shape[2]/2)
            horizontal_fit_line = self.get_fitline(src, horizontal_lines, size, 'horizontal')
            answer[3] = 'horizontal'
            answer[4] = horizontal_fit_line[1]
            answer[5] = horizontal_fit_line[0]
            self.draw_lines(temp, horizontal_lines, 'horizontal')
            self.draw_lines(temp, horizontal_fit_line, 'horizontal', 'fit')
            src = cv2.addWeighted(src, 1, temp, 1., 0.)
        return answer, src


