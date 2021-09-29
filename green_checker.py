import cv2
from math import sqrt
import imutils
import numpy as np

cap = cv2.VideoCapture("debug_video.avi")

def draw_lines(src, lines, mode = 'all', thickness=2):
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


def get_fitline(f_lines, size):
    lines = np.squeeze(f_lines)
    lines = lines.reshape(size,2)
    middle=int(lines.mean(axis=0)[1])
    min_x = int(lines.min(axis=0)[0])
    max_x = int(lines.max(axis=0)[0])
    H = [max_x, middle, min_x, middle]
    H_degree = (np.arctan2(H[1] - H[3], H[0] - H[2]) * 180) / np.pi
    return H, H_degree
        
                
while True:
    ret, img = cap.read()
    
    if not ret:
        break
    
    #img = cv2.imread("debug_image6.png")
    
    h, w = img.shape[:2]

    frame_center_x = w / 2
    frame_center_y = h / 2

    green_lower = np.array([25, 52, 72])
    green_upper = np.array([102, 255, 255])

    kernel = np.ones((5, 5), np.uint8)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue, saturation, value = cv2.split(hsv)

    green_mask = cv2.inRange(hsv, green_lower, green_upper)
    green_mask = cv2.erode(green_mask, kernel, iterations=2)
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
    green_mask = cv2.dilate(green_mask, kernel, iterations=1)
    
    _, binary = cv2.threshold(saturation, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    green_area_mask = cv2.bitwise_and(green_mask, binary)
    
    edge = imutils.auto_canny(green_area_mask)
    cnts, _ = cv2.findContours(green_area_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    def distance(pt1, pt2):
        return sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)

    max_dist = 0
    max_pos = 0, 0
    center = 0, 0

    if len(cnts) > 0:
        cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
        ((x, y), radius) = cv2.minEnclosingCircle(cnt)
        M = cv2.moments(cnt)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

    approx = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True) * 0.02, True)
    for pos in cnt:
        if max_dist < distance((frame_center_x, 0), pos[0]):
            max_pos = pos[0]
    
    #cv2.drawContours(img, [approx], 0, (0, 255, 255), 3)
    #cv2.circle(img, center, 10, (255, 255, 0), 3)
    
    lines = cv2.HoughLinesP(edge, 1, np.pi / 180, 90, minLineLength = 100, maxLineGap = 100)
    lines = np.squeeze(lines)
    
    if len(lines.shape) == 0:
        continue
    elif len(lines.shape) == 1:
        slope_degree = (np.arctan2(lines[1] - lines[3], lines[0] - lines[2]) * 180) / np.pi
    else:
        slope_degree = (np.arctan2(lines[:,1] - lines[:,3], lines[:,0] - lines[:,2]) * 180) / np.pi
        
    horizontal_lines = lines[np.abs(slope_degree) > 175]
    horizontal_slope_degree = slope_degree[np.abs(slope_degree)>175]
    horizontal_lines = horizontal_lines[:,None]
    
    if len(horizontal_lines) != 0:
        size = int(horizontal_lines.shape[0]*horizontal_lines.shape[2]/2)
        H, H_degree = get_fitline(horizontal_lines, size)
        draw_lines(img, horizontal_lines)

    cv2.imshow("img", img)
    cv2.imshow("edge", edge)
    cv2.imshow("and_mask", green_area_mask)
    
    if cv2.waitKey(100) == 27:
        break

cv2.destroyAllWindows()