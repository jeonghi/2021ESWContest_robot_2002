import cv2
import numpy as np
import math

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
            elif what_line == 'lines':
                color=[255,0,0]
            elif what_line == 'edge':
                color=[255, 255,0]
            elif what_line == 'edge_L':
                color=[255,0,255]
            elif what_line == 'edge_R':
                color=[0,255,255]
            else:
                color=[255,255,255]
            for line in lines:
                for x1,y1,x2,y2 in line:
                    cv2.line(src, (x1, y1), (x2, y2), color, thickness)

        if mode == 'fit':
            thickness = 10
            if what_line == 'vertical':
                color=[0, 0, 255]
            elif what_line == 'horizontal':
                color=[0,255,0]
            elif what_line == 'lines':
                color=[255,0,0]
            elif what_line == 'edge':
                color=[255, 255,0]
            elif what_line == 'edge_L':
                color=[255,0,255]
            elif what_line == 'edge_R':
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
            return [], [], [], [], [], []
        elif len(lines.shape) == 1 :
            return [], [], [], [], [], []
        else:
            slope_degree = (np.arctan2(lines[:,1] - lines[:,3], lines[:,0] - lines[:,2]) * 180) / np.pi
            
            edge_lines = lines[:,None]

            edge_lines_L = lines[(slope_degree) < 0]
            edge_lines_L_degree = slope_degree[(slope_degree)<0]
            edge_lines_L = edge_lines_L[:,None]
        
            edge_lines_R = lines[(slope_degree) > 0]
            edge_lines_R_degree = slope_degree[(slope_degree)>0] 
            edge_lines_R = edge_lines_R[:,None]

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

            return lines, horizontal_lines, vertical_lines, edge_lines, edge_lines_L,edge_lines_R

    def get_fitline(self, src, f_lines, size, what_line):
        lines = np.squeeze(f_lines)
        lines = lines.reshape(size,2)
        if what_line == 'vertical':
            output = cv2.fitLine(lines,cv2.DIST_L2,0, 0.01, 0.01)
            vx, vy, x, y = output[0], output[1], output[2], output[3]
            x1, y1 = int(((src.shape[0]-1)-y)/vy*vx + x) , src.shape[0]-1
            x2, y2 = int(((src.shape[0]/2+200)-y)/vy*vx + x) , int(src.shape[0]/2)
            result = [x1,y1,x2,y2]
        elif what_line == 'horizontal':
            middle=int(lines.mean(axis=0)[1])
            min_x = int(lines.min(axis=0)[0])
            max_x = int(lines.max(axis=0)[0])
            result = [max_x, middle, min_x, middle]
        elif what_line == 'edge':
            max_y=int(lines.max(axis=0)[1])
            min_x = int(lines.min(axis=0)[0]) 
            max_x = int(lines.max(axis=0)[0]) 
            result = [max_x, max_y, min_x, max_y] 
        elif what_line == 'edge_R':
            min_y=int(lines.min(axis=0)[1])
            max_y=int(lines.max(axis=0)[1])
            min_x = int(lines.min(axis=0)[0]) 
            max_x = int(lines.max(axis=0)[0]) 
            result = [max_x, min_y, min_x, max_y] 
        elif what_line == 'edge_L':
            min_y=int(lines.min(axis=0)[1])
            max_y=int(lines.max(axis=0)[1])
            min_x = int(lines.min(axis=0)[0]) 
            max_x = int(lines.max(axis=0)[0]) 
            result = [min_x, min_y, max_x, max_y] 
        return result

    def get_fitline__(self, img, f_lines): 
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


    def get_all_lines(self, src, line_visualization = False, edge_visualization = False):

        line_info = {"DEGREE" : 0, "V" : False, "V_X" : [0 ,0], "V_Y" : [0 ,0], "H" : False, "H_X" : [0 ,0], "H_Y" : [0 ,0]}    
        edge_info = {"EDGE_LINE": 0,"EDGE_L": False, "L_X" : [0 ,0], "L_Y" : [0 ,0],"EDGE_R": False, "R_X" : [0 ,0], "R_Y" : [0 ,0]}

        lines, horizontal_lines, vertical_lines, edge_lines, edge_lines_L,edge_lines_R = self.get_lines(src)

        temp = np.zeros((src.shape[0], src.shape[1], 3), dtype=np.uint8)

        if len(lines)!=0:
            size = int(lines.shape[0]*2)
            fit_line = self.get_fitline__(src, lines)
            line_degree = (np.arctan2(fit_line[1] - fit_line[3], fit_line[0] - fit_line[2]) * 180) / np.pi
            line_info["DEGREE"] = line_degree
            if line_visualization is True:
                self.draw_lines(temp, fit_line, 'lines', 'fit')
                src = cv2.addWeighted(src, 1, temp, 1., 0.)

        if len(vertical_lines)!=0:
            size = int(vertical_lines.shape[0]*vertical_lines.shape[2]/2)
            vertical_fit_line = self.get_fitline(src, vertical_lines, size, 'vertical')
            line_info["V"] = True
            line_info["V_X"] = [vertical_fit_line[2], vertical_fit_line[0]] #[x1,y1,x2,y2]
            line_info["V_Y"] = [vertical_fit_line[3], vertical_fit_line[1]]
            if line_visualization is True:
                self.draw_lines(temp, vertical_fit_line, 'vertical', 'fit')
                src = cv2.addWeighted(src, 1, temp, 1., 0.)

        if len(horizontal_lines)!=0:
            size = int(horizontal_lines.shape[0]*horizontal_lines.shape[2]/2)
            horizontal_fit_line = self.get_fitline(src, horizontal_lines, size, 'horizontal')
            line_info["H"] = True
            line_info["H_X"] = [horizontal_fit_line[0], horizontal_fit_line[2]] #[min_x, middle, max_x, middle]
            line_info["H_Y"] =  [horizontal_fit_line[1], horizontal_fit_line[2]]
            if line_visualization is True:
                self.draw_lines(temp, horizontal_fit_line, 'horizontal', 'fit')
                src = cv2.addWeighted(src, 1, temp, 1., 0.)

        if len(edge_lines) != 0:
            size = int(edge_lines.shape[0]*edge_lines.shape[2]/2)
            edge_fit_line = self.get_fitline(src, edge_lines, size, 'edge')
            edge_info["EDGE_LINE"] = edge_fit_line[1] # [max_x, max_y, min_x, max_y] 
            if edge_visualization is True:
                self.draw_lines(temp, edge_fit_line, 'edge', 'fit')
                src = cv2.addWeighted(src, 1, temp, 1., 0.)

        if len(edge_lines_L)!=0:
            size = int(edge_lines_L.shape[0]*edge_lines_L.shape[2]/2)
            edge_line_L = self.get_fitline(src, edge_lines_L, size, 'edge_L')
            edge_info["EDGE_L"] = True
            edge_info["L_X"] = [edge_line_L[0], edge_line_L[2]] # [min_x, min_y, max_x, max_y] 
            edge_info["L_Y"] = [edge_line_L[1], edge_line_L[3]] 
            if edge_visualization is True:
                self.draw_lines(temp, edge_line_L, 'edge_L', 'fit')
                src = cv2.addWeighted(src, 1, temp, 1., 0.)
        
        if len(edge_lines_R)!=0:
            size = int(edge_lines_R.shape[0]*edge_lines_R.shape[2]/2)
            edge_line_R = self.get_fitline(src, edge_lines_R, size, 'edge_R')
            edge_info["EDGE_R"] = True
            edge_info["R_X"] = [edge_line_R[2], edge_line_R[0]] # [max_x, min_y, min_x, max_y] 
            edge_info["R_Y"] = [edge_line_R[1], edge_line_R[3]]
            if edge_visualization is True: 
                self.draw_lines(temp, edge_line_R, 'edge_R', 'fit')
                src = cv2.addWeighted(src, 1, temp, 1., 0.)

        return line_info,edge_info, src


if __name__ == "__main__":
    video = cv2.VideoCapture(".\src\old\out_room.mp4")
    line_detector = LineDetector()
    while True:
        ret, src = video.read()
        if not ret:
            video = cv2.VideoCapture(".\src\old\out_room.mp4")
            print("No video")
            continue
        src = cv2.resize(src, dsize=(640,480))
        line_info,edge_info, result = line_detector.get_all_lines(src, line_visualization = False, edge_visualization = True)
        print(edge_info)
        cv2.imshow('result',result)
        key = cv2.waitKey(1)
        if key == 27:
            break
    video.release()
    cv2.destroyAllWindows()

