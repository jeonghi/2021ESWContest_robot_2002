import cv2
import numpy as np
import math


class LineDetector:
    def __init__(self):
        pass

    def draw_lines(self, src, lines, what_line, mode='all', thickness=2):
        if mode == 'all':
            thickness = 2
            if what_line == 'vertical':
                color = [0, 0, 255]
            elif what_line == 'horizontal':
                color = [0, 255, 0]
            elif what_line == 'lines':
                color = [255, 0, 0]
            elif what_line == 'edge':
                color = [255, 255, 0]
            elif what_line == 'edge_L':
                color = [255, 0, 255]
            elif what_line == 'edge_R':
                color = [0, 255, 255]
            else:
                color = [255, 255, 255]
            for line in lines:
                for x1, y1, x2, y2 in line:
                    cv2.line(src, (x1, y1), (x2, y2), color, thickness)

        if mode == 'fit':
            thickness = 10
            if what_line == 'vertical':
                color = [0, 0, 255]
            elif what_line == 'compact_horizontal' or what_line == "horizontal_D":
                color = [150, 150, 150]
            elif what_line == 'horizontal':
                color = [0, 255, 0]
            elif what_line == 'lines':
                color = [255, 0, 0]
            elif what_line == 'edge':
                color = [255, 255, 0]
            elif what_line == 'edge_L':
                color = [255, 0, 255]
            elif what_line == 'edge_R':
                color = [0, 255, 255]
            else:
                color = [255, 255, 255]
            for line in lines:
                cv2.line(src, (lines[0], lines[1]), (lines[2], lines[3]), color, thickness)

    # def mask_color(self, src):
    # hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    # h, s, v = cv2.split(hsv)
    # ret, mask = cv2.threshold(s, 70, 255, cv2.THRESH_BINARY)
    # src = cv2.bitwise_and(src, src, mask = mask)
    # yellow_lower = np.array([10,40,95])
    # yellow_upper = np.array([40, 220, 220])
    # src = cv2.GaussianBlur(src, (5, 5), 0)
    # hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    # mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
    # return mask

    def mask_color(self, src, color='YELLOW'):
        if color == 'YELLOW':
            hls = cv2.cvtColor(src, cv2.COLOR_BGR2HLS)
            h, l, s = cv2.split(hls)
            ret, mask = cv2.threshold(s, 40, 255, cv2.THRESH_BINARY)
            src = cv2.bitwise_and(src, src, mask=mask)
            match_lower = np.array([10, 40, 110])  # yellow_lower
            match_upper = np.array([45, 225, 220])  # yellow_upper

        if color == 'GREEN':
            hls = cv2.cvtColor(src, cv2.COLOR_BGR2HLS)
            h, l, s = cv2.split(hls)
            ret, mask = cv2.threshold(s, 100, 255, cv2.THRESH_BINARY)
            src = cv2.bitwise_and(src, src, mask=mask)
            match_lower = np.array([20, 20, 20])  # green_lower
            match_upper = np.array([80, 255, 220])  # green_upper

        if color == 'BLACK':
            match_lower = np.array([0, 0, 0])  # black_lower
            match_upper = np.array([255, 255, 30])  # black_upper
        
        src = cv2.GaussianBlur(src, (5, 5), 0)
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, match_lower, match_upper)
        return mask

    def get_lines(self, src, color='YELLOW'):
        mask = self.mask_color(src, color)
        
        if color == 'BLACK':
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            return contours
        else:
            edges = cv2.Canny(mask, 75, 150)
            #cv2.imshow('mask', mask)
            #cv2.imshow('edges', edges)
            lines = cv2.HoughLinesP(edges, 1, 1 * np.pi / 180, 30, np.array([]), minLineLength=50, maxLineGap=150)
            lines = np.squeeze(lines)
            #print(lines)

            if len(lines.shape) == 0:
                return [], [], [], [], [], [], []
            elif len(lines.shape) == 1:
                return [], [], [], [], [], [], []
            else:
                slope_degree = (np.arctan2(lines[:, 1] - lines[:, 3], lines[:, 0] - lines[:, 2]) * 180) / np.pi

                edge_lines = lines[:, None]

                edge_lines_L = lines[(slope_degree) < 0]
                edge_lines_L_degree = slope_degree[(slope_degree) < 0]
                edge_lines_L = edge_lines_L[:, None]

                edge_lines_R = lines[(slope_degree) > 0]
                edge_lines_R_degree = slope_degree[(slope_degree) > 0]
                edge_lines_R = edge_lines_R[:, None]

                horizontal_lines = lines[np.abs(slope_degree) > 170]
                horizontal_slope_degree = slope_degree[np.abs(slope_degree) > 170]
                horizontal_lines = horizontal_lines[:, None]
                
                compact_horizontal_lines = lines[np.abs(slope_degree) > 175]
                #compact_horizontal_lines = slope_degree[np.abs(slope_degree) > 175]
                compact_horizontal_lines = compact_horizontal_lines[:, None]

                lines = lines[np.abs(slope_degree) < 150]
                slope_degree = slope_degree[np.abs(slope_degree) < 150]

                vertical_lines = lines[np.abs(slope_degree) < 110]
                vertical_slope_degree = slope_degree[np.abs(slope_degree) < 110]
                vertical_lines = vertical_lines[np.abs(vertical_slope_degree) > 70]
                vertical_slope_degree = vertical_slope_degree[np.abs(vertical_slope_degree) > 70]
                vertical_lines = vertical_lines[:, None]

                lines = lines[:, None]

                return lines, horizontal_lines,vertical_lines, edge_lines, edge_lines_L, edge_lines_R ,compact_horizontal_lines

    def get_fitline(self, src, f_lines, size, what_line):
        lines = np.squeeze(f_lines)
        lines = lines.reshape(size, 2)
        if what_line == 'vertical':
            output = cv2.fitLine(lines, cv2.DIST_L2, 0, 0.01, 0.01)
            vx, vy, x, y = output[0], output[1], output[2], output[3]
            x1, y1 = int(((src.shape[0] - 1) - y) / vy * vx + x), src.shape[0] - 1
            x2, y2 = int(((src.shape[0] / 2 + 200) - y) / vy * vx + x), int(src.shape[0] / 2)
            result = [x2, y2, x1, y1]
            return result
        elif what_line == 'horizontal':
            middle=int(lines.mean(axis=0)[1])
            min_x = int(lines.min(axis=0)[0])
            max_x = int(lines.max(axis=0)[0])
            #min_y = int(lines.min(axis=0)[1])
            #max_y = int(lines.max(axis=0)[1])
            result = [min_x, middle, max_x, middle]
            #result = [min_x, min_y, max_x, max_y ]
            return result
        elif what_line == 'horizontal_D':
            #middle=int(lines.mean(axis=0)[1])
            min_x = int(lines.min(axis=0)[0])
            max_x = int(lines.max(axis=0)[0])
            min_y = int(lines.min(axis=0)[1]) + 10
            max_y = int(lines.max(axis=0)[1]) - 10
            #result = [min_x, middle, max_x, middle]
            result = [min_x, min_y, max_x, max_y ]
            return result
        elif what_line == 'compact_horizontal':
            middle=int(lines.mean(axis=0)[1])
            min_x = int(lines.min(axis=0)[0])
            max_x = int(lines.max(axis=0)[0])
            result = [min_x, middle, max_x, middle]
            return result
        elif what_line == 'edge_UP':
            min_y = int(lines.min(axis=0)[1])
            min_x = int(lines.min(axis=0)[0])
            max_x = int(lines.max(axis=0)[0])
            result = [max_x, min_y, min_x, min_y]
            return result
        elif what_line == 'edge_DOWN':
            max_y = int(lines.max(axis=0)[1])
            min_x = int(lines.min(axis=0)[0])
            max_x = int(lines.max(axis=0)[0])
            result = [max_x, max_y, min_x, max_y]
            return result
        elif what_line == 'edge_R':
            min_y = int(lines.min(axis=0)[1])
            max_y = int(lines.max(axis=0)[1])
            min_x = int(lines.min(axis=0)[0])
            max_x = int(lines.max(axis=0)[0])
            result = [max_x, min_y, min_x, max_y]
            return result
        elif what_line == 'edge_L' or 'all':
            min_y = int(lines.min(axis=0)[1])
            max_y = int(lines.max(axis=0)[1])
            min_x = int(lines.min(axis=0)[0])
            max_x = int(lines.max(axis=0)[0])
            result = [min_x, min_y, max_x, max_y]
            return result

    def get_contour_line(self, contours, what_line):
        contours_min = np.argmin(contours[0], axis = 0)
        contours_max = np.argmax(contours[0], axis = 0)
        
        xMin = contours[0][contours_min[0][0]][0][0]
        yMin =contours[0][contours_min[0][1]][0][1]
        xMax = contours[0][contours_max[0][0]][0][0]
        yMax = contours[0][contours_max[0][1]][0][1]

        if what_line == 'UP':
            result = [ xMin, yMin, xMax, yMin]
        else:
            result = [ xMin, yMax, xMax, yMax]

    def get_fitline__(self, img, f_lines):
        lines = np.squeeze(f_lines)
        if len(lines.shape) == 1:
            lines = lines.reshape(int(lines.shape[0] / 2), 2)
        else:
            lines = lines.reshape(lines.shape[0] * 2, 2)
        output = cv2.fitLine(lines, cv2.DIST_L2, 0, 0.01, 0.01)
        vx, vy, x, y = output[0], output[1], output[2], output[3]
        x1, y1 = int(((img.shape[0] - 1) - y) / vy * vx + x), img.shape[0] - 1
        x2, y2 = int(((img.shape[0] / 2 + 200) - y) / vy * vx + x), int(img.shape[0] / 2 + 200)
        result = [x1, y1, x2, y2]
        return result

    def get_all_lines(self, src, color='YELLOW', line_visualization=False, edge_visualization=False):
        temp = np.zeros((src.shape[0], src.shape[1], 3), dtype=np.uint8)

        if color == 'BLACK':
            contours = None
            line_info = { }
            edge_info = {'EDGE_DOWN': False, 'EDGE_DOWN_X': 0, 'EDGE_DOWN_Y': 0, 'EDGE_UP_Y': 0, 'EDGE_UP':False, 'EDGE_UP_X':0}
            contours = self.get_lines(src, color)

            if len(contours) != 0:
                contour = max(contours, key=lambda x:cv2.contourArea(x))
                leftmost = tuple(contour[contour[:,:,0].argmin()][0])
                rightmost = tuple(contour[contour[:,:,0].argmax()][0])
                topmost = tuple(contour[contour[:,:,1].argmin()][0])
                bottommost = tuple(contour[contour[:,:,1].argmax()][0])

                edge_contour_line_DOWN = [ 10, bottommost[1], 600, bottommost[1]]
                edge_contour_line_UP = [ 10, topmost[1], 600, topmost[1]]
                
                edge_info["EDGE_UP"] = True     
                edge_info["EDGE_UP_X"] = [ edge_contour_line_UP[0] , edge_contour_line_UP[2]]
                edge_info["EDGE_UP_Y"] = edge_contour_line_UP[1]
                edge_info["EDGE_DOWN"] = True
                edge_info["EDGE_DOWN_X"] = [ edge_contour_line_DOWN[0] , edge_contour_line_DOWN[2]]
                edge_info["EDGE_DOWN_Y"] = edge_contour_line_DOWN[1]

                if edge_visualization is True:
                    self.draw_lines(temp, edge_contour_line_UP, 'lines', 'fit')
                    self.draw_lines(temp, edge_contour_line_DOWN, 'lines', 'fit')
                    src = cv2.addWeighted(src, 1, temp, 1., 0.)
                    for cnt in contours:
                        cv2.drawContours(src, cnt, -1, (255, 0, 0), 2)

        else:
            lines, horizontal_lines,vertical_lines,edge_lines,edge_lines_L,edge_lines_R ,compact_horizontal_lines = self.get_lines(src, color)

            if color == 'YELLOW':
                line_info = {"DEGREE": 0, "ALL_X": [0, 0], 'ALL_Y': [0, 0], "V": False, "V_X": [0, 0], "V_Y": [0, 0],"H_DEGREE" : 0, "H": False, "H_X": [0, 0],
                            "H_Y": [0, 0], "compact_H": False, "compact_H_X": [0, 0], "compact_H_Y": [0, 0]}
                edge_info = {"EDGE_POS": None, "EDGE_L": False, "L_X": [0, 0], "L_Y": [0, 0], "EDGE_R": False,
                            "R_X": [0, 0], "R_Y": [0, 0]}

                if len(lines) != 0:
                    size = int(lines.shape[0] * 2)
                    fit_line = self.get_fitline__(src, lines)
                    line_degree = (np.arctan2(fit_line[1] - fit_line[3], fit_line[0] - fit_line[2]) * 180) / np.pi
                    line_info["DEGREE"] = line_degree
                    if line_visualization is True:
                        self.draw_lines(temp, fit_line, 'lines', 'fit')
                        src = cv2.addWeighted(src, 1, temp, 1., 0.)

                if len(vertical_lines) != 0:
                    size = int(vertical_lines.shape[0] * vertical_lines.shape[2] / 2)
                    vertical_fit_line = self.get_fitline(src, vertical_lines, size, 'vertical')
                    line_info["V"] = True
                    line_info["V_X"] = [vertical_fit_line[0], vertical_fit_line[2]]  # [x1,y1,x2,y2]
                    line_info["V_Y"] = [vertical_fit_line[1], vertical_fit_line[3]]
                    if line_visualization is True:
                        self.draw_lines(temp, vertical_fit_line, 'vertical', 'fit')
                        src = cv2.addWeighted(src, 1, temp, 1., 0.)

                if len(horizontal_lines) != 0:
                    #print(horizontal_lines)
                    #print(horizontal_lines.shape)
                    size = int(horizontal_lines.shape[0] * horizontal_lines.shape[2] / 2)
                    horizontal_fit_line = self.get_fitline(src, horizontal_lines, size, 'horizontal')
                    horizontal_D_fit_line = self.get_fitline(src, horizontal_lines, size, 'horizontal_D')
                    a = horizontal_fit_line[1] - horizontal_fit_line[3]
                    b = horizontal_fit_line[0] - horizontal_fit_line[2]
                    c = math.sqrt((a * a) + (b * b))
                    if c >= 200:
                        line_info["H"] = True
                    
                    H_degree = (np.arctan2(horizontal_D_fit_line[1] - horizontal_D_fit_line[3], horizontal_D_fit_line[0] - horizontal_D_fit_line[2]) * 180) / np.pi
                    line_info["H_DEGREE"] = np.abs(H_degree)
                    line_info["H_X"] = [horizontal_fit_line[0], horizontal_fit_line[2]]  # [min_x, middle, max_x, middle]
                    line_info["H_Y"] = [horizontal_fit_line[1], horizontal_fit_line[3]]
                    if line_visualization is True:
                        self.draw_lines(temp, horizontal_D_fit_line, 'horizontal_D', 'fit')
                        self.draw_lines(temp, horizontal_fit_line, 'horizontal', 'fit')
                        src = cv2.addWeighted(src, 1, temp, 1., 0.)

                if len(compact_horizontal_lines) != 0:
                    #print(compact_horizontal_lines)
                    #print(compact_horizontal_lines.shape)
                    size = int(compact_horizontal_lines.shape[0] * compact_horizontal_lines.shape[2] / 2)
                    compact_horizontal_line = self.get_fitline(src, compact_horizontal_lines, size, 'compact_horizontal')
                    a = compact_horizontal_line[1] - compact_horizontal_line[3]
                    b = compact_horizontal_line[0] - compact_horizontal_line[2]
                    c = math.sqrt((a * a) + (b * b))
                    print(c)
                    if c >= 350:
                        line_info["H"] = True
                    #H_degree = (np.arctan2(horizontal_fit_line[1] - horizontal_fit_line[3], horizontal_fit_line[0] - horizontal_fit_line[2]) * 180) / np.pi
                    #line_info["H_DEGREE"] = H_degree
                    line_info["compact_H_X"] = [compact_horizontal_line[0], compact_horizontal_line[2]]  # [min_x, middle, max_x, middle]
                    line_info["compact_H_Y"] = [compact_horizontal_line[1], compact_horizontal_line[3]]
                    if line_visualization is True:
                        # self.draw_lines(temp, horizontal_fit_line, 'horizontal')
                        self.draw_lines(temp, compact_horizontal_line, 'compact_horizontal', 'fit')
                        src = cv2.addWeighted(src, 1, temp, 1., 0.)

                if len(edge_lines) != 0:
                    size = int(edge_lines.shape[0] * edge_lines.shape[2] / 2)
                    edge_fit_line_DOWN = self.get_fitline(src, edge_lines, size, 'edge_DOWN')
                    line_info["ALL_X"] = [edge_fit_line_DOWN[2], edge_fit_line_DOWN[0]]  # [min_x, min_y, max_x, max_y]
                    line_info["ALL_Y"] = [edge_fit_line_DOWN[1], edge_fit_line_DOWN[3]]
                    if edge_visualization is True:
                        self.draw_lines(temp, edge_fit_line_DOWN, 'edge', 'fit')
                        src = cv2.addWeighted(src, 1, temp, 1., 0.)

                if len(edge_lines_L) != 0:
                    size = int(edge_lines_L.shape[0] * edge_lines_L.shape[2] / 2)
                    edge_line_L = self.get_fitline(src, edge_lines_L, size, 'edge_L')
                    edge_info["EDGE_L"] = True
                    edge_info["L_X"] = [edge_line_L[0], edge_line_L[2]]  # [min_x, min_y, max_x, max_y]
                    edge_info["L_Y"] = [edge_line_L[1], edge_line_L[3]]
                    if edge_visualization is True:
                        self.draw_lines(temp, edge_line_L, 'edge_L', 'fit')
                        src = cv2.addWeighted(src, 1, temp, 1., 0.)

                if len(edge_lines_R) != 0:
                    size = int(edge_lines_R.shape[0] * edge_lines_R.shape[2] / 2)
                    edge_line_R = self.get_fitline(src, edge_lines_R, size, 'edge_R')
                    edge_info["EDGE_R"] = True
                    edge_info["R_X"] = [edge_line_R[0], edge_line_R[2]]  # [max_x, min_y, min_x, max_y]
                    edge_info["R_Y"] = [edge_line_R[1], edge_line_R[3]]
                    if edge_visualization is True:
                        self.draw_lines(temp, edge_line_R, 'edge_R', 'fit')
                        src = cv2.addWeighted(src, 1, temp, 1., 0.)

                if len(edge_lines) != 0 and len(edge_lines_L) != 0 and len(edge_lines_R) != 0:
                    x_center = int((edge_line_L[2] + edge_line_R[2]) / 2)
                    y_center = edge_fit_line_DOWN[1]  # [max_x, max_y, min_x, max_y]
                    edge_info["EDGE_POS"] = [x_center, y_center]
                else:
                    edge_info["EDGE_POS"] = None

            if color == 'GREEN':
                line_info = {'ALL_X': [0, 0], 'ALL_Y': [0, 0], 'V': False, 'V_X': [0, 0], 'V_Y': [0, 0], 'H': False, 'H_DEGREE': 0 , 'H_X': [0, 0], 'H_Y': [0, 0]}
                edge_info = {'EDGE_DOWN': False, 'EDGE_DOWN_X': 0, 'EDGE_DOWN_Y': 0, 'EDGE_UP_Y': 0, 'EDGE_UP':False, 'EDGE_UP_X':0}

                if len(edge_lines) != 0:
                    size = int(edge_lines.shape[0] * edge_lines.shape[2] / 2)
                    line = self.get_fitline(src, edge_lines, size, 'all')
                    line_info["ALL_X"] = [line[0], line[2]]  # [min_x, min_y, max_x, max_y]
                    line_info["ALL_Y"] = [line[1], line[3]]

                    # size = int(lines.shape[0]*2)
                    # fit_line = self.get_fitline__(src, lines)
                    # line_degree = (np.arctan2(fit_line[1] - fit_line[3], fit_line[0] - fit_line[2]) * 180) / np.pi
                    # line_info["V_DEGREE"] = line_degree
                    if line_visualization is True:
                        self.draw_lines(temp, edge_lines, 'lines')
                        self.draw_lines(temp, line, 'lines', 'fit')
                        src = cv2.addWeighted(src, 1, temp, 1., 0.)
                        
                if len(vertical_lines) != 0:
                    size = int(vertical_lines.shape[0] * vertical_lines.shape[2] / 2)
                    vertical_fit_line = self.get_fitline(src, vertical_lines, size, 'vertical')
                    line_info["V"] = True
                    line_info["V_X"] = [vertical_fit_line[0], vertical_fit_line[2]]  # [x1,y1,x2,y2]
                    line_info["V_Y"] = [vertical_fit_line[1], vertical_fit_line[3]]
                    if line_visualization is True:
                        self.draw_lines(temp, vertical_fit_line, 'vertical', 'fit')
                        src = cv2.addWeighted(src, 1, temp, 1., 0.)

                if len(compact_horizontal_lines) != 0:
                    #print(compact_horizontal_lines)
                    #print(compact_horizontal_lines.shape)
                    size = int(compact_horizontal_lines.shape[0] * compact_horizontal_lines.shape[2] / 2)
                    compact_horizontal_line = self.get_fitline(src, compact_horizontal_lines, size, 'compact_horizontal')
                    
                    size_ = int(horizontal_lines.shape[0] * horizontal_lines.shape[2] / 2)
                    horizontal_D_fit_line = self.get_fitline(src, horizontal_lines, size_, 'horizontal_D')
                    
                    H_degree = (np.arctan2(horizontal_D_fit_line[1] - horizontal_D_fit_line[3], horizontal_D_fit_line[0] - horizontal_D_fit_line[2]) * 180) / np.pi
                    line_info["H_DEGREE"] = np.abs(H_degree)
                    
                    a = compact_horizontal_line[1] - compact_horizontal_line[3]
                    b = compact_horizontal_line[0] - compact_horizontal_line[2]
                    c = math.sqrt((a * a) + (b * b))
                    print('length:  ', c)
                    if c >= 100:
                        line_info["H"] = True
                    print(compact_horizontal_line[3])
                    #H_degree = (np.arctan2(horizontal_fit_line[1] - horizontal_fit_line[3], horizontal_fit_line[0] - horizontal_fit_line[2]) * 180) / np.pi
                    #line_info["H_DEGREE"] = H_degree
                    line_info["H_X"] = [compact_horizontal_line[0], compact_horizontal_line[2]]  # [min_x, middle, max_x, middle]
                    line_info["H_Y"] = [compact_horizontal_line[1], compact_horizontal_line[3]]
                    if line_visualization is True:
                        # self.draw_lines(temp, horizontal_fit_line, 'horizontal')
                        self.draw_lines(temp, compact_horizontal_line, 'compact_horizontal', 'fit')
                        src = cv2.addWeighted(src, 1, temp, 1., 0.)
                # edge_info = {'EDGE_DOWN': False, 'EDGE_DOWN_Y':0, 'EDGE_UP_Y': 0}
                if len(edge_lines) != 0:
                    size = int(edge_lines.shape[0] * edge_lines.shape[2] / 2)
                    edge_info["EDGE_UP"] = True
                    edge_fit_line_UP = self.get_fitline(src, edge_lines, size, 'edge_UP')
                    edge_fit_line_DOWN = self.get_fitline(src, edge_lines, size, 'edge_DOWN')
                    edge_info["EDGE_UP_X"] = int((edge_fit_line_UP[0] + edge_fit_line_UP[2])/2)
                    edge_info["EDGE_UP_Y"] = edge_fit_line_UP[1]
                    edge_info["EDGE_DOWN"] = True
                    edge_info["EDGE_DOWN_X"] = int((edge_fit_line_DOWN[0] + edge_fit_line_DOWN[2]) / 2)
                    edge_info["EDGE_DOWN_Y"] = edge_fit_line_DOWN[1]
                    if edge_visualization is True:
                        self.draw_lines(temp, edge_fit_line_UP, 'edge', 'fit')
                        self.draw_lines(temp, edge_fit_line_DOWN, 'edge', 'fit')
                        src = cv2.addWeighted(src, 1, temp, 1., 0.)

        return line_info, edge_info, src


if __name__ == "__main__":
    video = cv2.VideoCapture("Sensor/src/green_room_test/green_area1.h264")
    line_detector = LineDetector()
    while True:
        ret, src = video.read()
        if not ret:
            video = cv2.VideoCapture(-1)
            continue
        src = cv2.resize(src, dsize=(640, 480))

        hsv_image = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        val_S = 0
        val_V = 0
        array = np.full(hsv_image.shape, (0, val_S, val_V), dtype=np.uint8)
        val_add_image = cv2.add(hsv_image, array)
        src = cv2.cvtColor(val_add_image, cv2.COLOR_HSV2BGR)

        line_info, edge_info, result = line_detector.get_all_lines(src, color='YELLOW', line_visualization=True,
                                                                   edge_visualization=False)
        print(line_info)
        print(edge_info)
        cv2.imshow('result', result)
        key = cv2.waitKey(1)
        if key == 27:
            break
    video.release()
    cv2.destroyAllWindows()