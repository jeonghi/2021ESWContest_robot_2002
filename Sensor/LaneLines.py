
from scipy.stats import linregress
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2
import os
import math
from imutils import auto_canny


def hough_lines(image):
    image_edges = auto_canny(image)
    houghed_lns = cv2.HoughLinesP(image_edges, rho=2, theta=np.pi / 180,
                                  threshold=50, lines=np.array([]),
                                  minLineLength=20, maxLineGap=100)
    return houghed_lns


def left_right_lines(lines):
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

    filtered_left_lns = filter_lines_outliers(lines_all_left, slopes_left, True)
    filtered_right_lns = filter_lines_outliers(lines_all_right, slopes_right, False)

    return filtered_left_lns, filtered_right_lns


def filter_lines_outliers(lines, slopes, min_slope=0.2, max_slope=0.9):
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


def median(lines, prev_ms, prev_bs):
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


def intersect(f_a, f_b):
    if f_a is None or f_b is None:
        return None

    equation = f_a.coeffs - f_b.coeffs
    x = -equation[1] / equation[0]
    y = np.poly1d(f_a.coeffs)(x)
    x, y = map(int, [x, y])

    return [x, y]


def detect(image, prev_left_ms, prev_left_bs, prev_right_ms, prev_right_bs):
    houghed_lns = hough_lines(image)

    if houghed_lns is None:
        return [None, None, None, None]

    filtered_left_lns, filtered_right_lns = left_right_lines(houghed_lns)
    median_left_f = median(filtered_left_lns, prev_left_ms, prev_left_bs)
    median_right_f = median(filtered_right_lns, prev_right_ms, prev_right_bs)

    if median_left_f is None or median_right_f is None:
        return detect(image, prev_left_ms, prev_left_bs, prev_right_ms, prev_right_bs)
    else:
        return [filtered_left_lns, filtered_right_lns, median_left_f, median_right_f]