from scipy.stats import linregress
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2
import os
import math
from imutils import auto_canny
from ColorChecker import ColorPreProcessor


class CornerFinder():
    @classmethod
    def hough_lines(cls, image):
        image_edges = auto_canny(image)
        houghed_lns = cv2.HoughLinesP(image_edges, rho=2, theta=np.pi / 180,
                                      threshold=50, lines=np.array([]),
                                      minLineLength=20, maxLineGap=100)
        return houghed_lns

    @classmethod
    def left_right_lines(cls, lines):
        lines_all_left = []
        lines_all_right = []
        slopes_left = []
        slopes_right = []

        for line in lines:
            for x1, y1, x2, y2 in line:
                if int(x2 - x1) == 0 :
                    slope = 0
                else:
                    slope = (y2 - y1) / (x2 - x1)

                if 0 <= slope < 1:  # 1,5사분면 (8사분면 기준)
                    lines_all_right.append(line)
                    slopes_right.append(slope)
                elif slope >= 1:  # 2,6사분면
                    lines_all_right.append(line)
                    slopes_right.append(slope)
                elif slope <= -1:  # 3,7사분면
                    lines_all_left.append(line)
                    slopes_left.append(slope)

                elif -1 < slope < 0: # 4,8사분
                    lines_all_left.append(line)
                    slopes_left.append(slope)

        filtered_left_lns = cls.filter_lines_outliers(lines_all_left, slopes_left, True)
        filtered_right_lns = cls.filter_lines_outliers(lines_all_right, slopes_right, False)

        return filtered_left_lns, filtered_right_lns

    @classmethod
    def filter_lines_outliers(cls, lines, slopes, min_slope=0.2, max_slope=0.9):
        if len(lines) < 2:
            return lines
        lines_no_outliers = lines
        slopes_no_outliers = slopes

        slope_median = np.median(slopes_no_outliers)
        slope_std_deviation = np.std(slopes_no_outliers)
        filtered_lines = []

        for i, line in enumerate(lines_no_outliers):
            slope = slopes_no_outliers[i]
            intercepts = np.median(line)

            if slope_median - 2 * slope_std_deviation < slope < slope_median + 2 * slope_std_deviation:
                filtered_lines.append(line)

        return filtered_lines

    @classmethod
    def median(cls, lines, prev_ms, prev_bs):
        if prev_ms is None:
            prev_ms = []
            prev_bs = []

        xs = []
        ys = []
        xs_med = []
        ys_med = []
        m = 0
        b = 0

        for line in lines:
            for x1, y1, x2, y2 in line:
                xs += [x1, x2]
                ys += [y1, y2]

        if len(xs) > 2 and len(ys) > 2:
            #         m, b = np.polyfit(xs, ys, 1)
            m, b, r_value_left, p_value_left, std_err = linregress(xs, ys)

            if len(prev_ms) > 0:
                prev_ms.append(m)
                prev_bs.append(b)
            else:
                return np.poly1d([m, b])

        if len(prev_ms) > 0:
            return np.poly1d([np.average(prev_ms), np.average(prev_bs)])
        else:
            return None

    @classmethod
    def intersect(cls, f_a, f_b):
        if f_a is None or f_b is None:
            return None

        equation = f_a.coeffs - f_b.coeffs
        x = -equation[1] / equation[0]
        y = np.poly1d(f_a.coeffs)(x)
        x, y = map(int, [x, y])

        return [x, y]


    @classmethod
    def get_yellow_line_corner_pos(cls, src, visualization: bool = False):
        pos = None

        if visualization:
            h, w = src.shape[:2]
            canvas = src.copy()

        yellow_mask = ColorPreProcessor.get_yellow_mask4hsv(src)

        masked = cv2.bitwise_and(src,src,mask=yellow_mask)
        canny = auto_canny(masked)
        lines = cv2.HoughLinesP(canny, 2, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=60)
        if lines is not None:
            if visualization:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    if int(x2 - x1) == 0:
                        slope = 0
                    else:
                        slope = (y2 - y1) / (x2 - x1)

                    if 0 <= slope < 1: # 노란색선
                        cv2.line(canvas, (x1, y1), (x2, y2), (0, 255, 255), 2)
                    elif slope >= 1: # 하늘색선
                        cv2.line(canvas, (x1, y1), (x2, y2), (255, 255, 0), 2)
                    elif slope <= -1 : # 초록색선
                        cv2.line(canvas, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    elif -1 < slope < 0: # 빨간색선
                        cv2.line(canvas, (x1, y1), (x2, y2), (255, 0, 255), 2)
                    else:
                        cv2.line(canvas, (x1, y1), (x2, y2), (255, 255, 255), 2)

            filtered_left_lns, filtered_right_lns = cls.left_right_lines(lines)
            median_left_f = cls.median(filtered_left_lns, [], [])
            median_right_f = cls.median(filtered_right_lns, [], [])
            if median_left_f is not None and median_right_f is not None:
                intersect_pt = cls.intersect(median_left_f, median_right_f)
                if intersect_pt is not None:
                    pos = tuple(intersect_pt)
                    if visualization :
                        center = (cx, cy) = (w // 2, h // 2)
                        x_range = 10
                        y_range = 20
                        if cx-x_range*10 <= pos[0] <= cx+x_range*10 :
                            cv2.circle(canvas, pos, 10, (255, 0, 0), -1)
                            cv2.putText(canvas, "IN", pos, cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 0, 0), thickness=2)
                        else:
                            cv2.circle(canvas, pos, 10, (0, 0, 255), -1)
                            cv2.putText(canvas, "NOT IN", pos, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness=2)

                        cv2.line(canvas, (cx - x_range * 10, cy), (cx + x_range * 10, cy), (255, 0, 0), 2)
                        cv2.circle(canvas, center, 10, (255, 0, 0), 2)
                        for x_r in range(x_range + 1):
                            if x_r == 0 or x_r == x_range:
                                x_r *= 10
                                if x_r != 0:
                                    cv2.putText(canvas, "-%d" % x_r, (cx - x_r, cy - y_range), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                                (255, 0, 0), thickness=2)
                                    cv2.putText(canvas, "-%d" % x_r, (cx + x_r, cy - y_range), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                                (255, 0, 0), thickness=2)
                                else:
                                    cv2.putText(canvas, "0", (cx, cy - y_range), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                                (255, 0, 0), thickness=2)

                                cv2.line(canvas, (cx - x_r, cy - y_range), (cx - x_r, cy + y_range), (255, 0, 0), 2)
                                cv2.line(canvas, (cx + x_r, cy - y_range), (cx + x_r, cy + y_range), (255, 0, 0), 2)
                            else:
                                y_r = y_range // 2
                                x_r *= 10
                                cv2.line(canvas, (cx - x_r, cy - y_r), (cx - x_r, cy + y_r), (255, 0, 0), 1)
                                cv2.line(canvas, (cx + x_r, cy - y_r), (cx + x_r, cy + y_r), (255, 0, 0), 1)

        if visualization:
            result = cv2.hconcat([masked, canvas])
            cv2.imshow("corner_finder", result)
            cv2.waitKey(1)

        return pos

if __name__ == "__main__" :

    from imutils.video import FileVideoStream
    cam = FileVideoStream(path="Sensor\src\old\out_room.mp4")
    cam.start()

    while(True):
        src = cam.read()
        CornerFinder.get_yellow_line_corner_pos(src, visualization=True)

