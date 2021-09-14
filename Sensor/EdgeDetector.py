import cv2
import numpy as np
import math

class LineDetector:
    def __init__(self):
        pass

    def draw_lines(self, src, lines, mode = 'all', thickness=2):
        if mode == 'all':
            thickness = 2
            color=[0,255,0]
            for line in lines:
                for x1,y1,x2,y2 in line:
                    cv2.line(src, (x1, y1), (x2, y2), color, thickness)

        if mode == 'fit':
            thickness = 10
            color=[0,255,255]
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
            print("None")
            return [], [], []
        elif len(lines.shape) == 1 :
            print("shape 1")
            return [], [], []
        else:
            print("shape more than 1")

            edge_lines = lines[:,None]
    
            slope_degree = (np.arctan2(lines[:,1] - lines[:,3], lines[:,0] - lines[:,2]) * 180) / np.pi

            vertical_lines = lines[np.abs(slope_degree) < 95]
            vertical_slope_degree = slope_degree[np.abs(slope_degree)<95]
            vertical_lines = vertical_lines[np.abs(vertical_slope_degree) > 85]
            vertical_slope_degree = vertical_slope_degree[np.abs(vertical_slope_degree)>85] 
            vertical_lines = vertical_lines[:,None]
    
            return edge_lines, vertical_lines

    def get_fitline(self, src, f_lines, size):
        lines = np.squeeze(f_lines)
        lines = lines.reshape(size,2)
        output = cv2.fitLine(lines,cv2.DIST_L2,0, 0.01, 0.01)
        vx, vy, x, y = output[0], output[1], output[2], output[3]
        x1, y1 = int(((src.shape[0]-1)-y)/vy*vx + x) , src.shape[0]-1
        x2, y2 = int(((src.shape[0]/2+200)-y)/vy*vx + x) , int(src.shape[0]/2)
        result = [x1,y1,x2,y2]
        return result

    def get_edgeline(self, src, f_lines, size, what_line):
        lines = np.squeeze(f_lines)
        lines = lines.reshape(size,2)
        middle=int(lines.max(axis=0)[1])
        min_x = int(lines.min(axis=0)[0]) 
        max_x = int(lines.max(axis=0)[0]) 
        result = [max_x, middle, min_x, middle] 
        return result

    def find_edge(self, src):
        answer = [None, 0, 0, None]
        edge_lines, vertical_lines= self.get_lines(src)
        temp = np.zeros((src.shape[0], src.shape[1], 3), dtype=np.uint8)
    
        if len(edge_lines)!=0:
            size = int(edge_lines.shape[0]*edge_lines.shape[2]/2)
            edge_line = self.get_edgeline(src, edge_lines, size, 'edge')
            answer[0] = 'edge'
            answer[1] = len(edge_lines)
            answer[2] = edge_line[1]
            self.draw_lines(temp, edge_lines)
            self.draw_lines(temp, edge_line, 'fit')
            src = cv2.addWeighted(src, 1, temp, 1., 0.)
    
        if len(vertical_lines)!=0:
            print('vertical_lines', len(vertical_lines.shape)) 
            size = int(vertical_lines.shape[0]*vertical_lines.shape[2]/2)
            vertical_fit_line = self.get_fitline(src, vertical_lines, size)
            answer[3] = 'vertical'
            self.draw_lines(temp, vertical_lines)
            self.draw_lines(temp, vertical_fit_line, 'fit')
            src = cv2.addWeighted(src, 1, temp, 1., 0.)

        return answer, src
