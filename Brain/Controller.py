from Sensor.ImageProcessor import ImageProcessor
from Actuator.Motion import Motion
import numpy as np
import cv2
import time
import sys

import cv2
import numpy as np

def grayscale(img): # 흑백이미지로 변환
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

def canny(img, low_threshold, high_threshold): # Canny 알고리즘
    return cv2.Canny(img, low_threshold, high_threshold)

def gaussian_blur(img, kernel_size): # 가우시안 필터
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

def draw_lines(img, lines, color=[0, 0, 255], thickness=2): # 선 그리기
    for line in lines:
        for x1,y1,x2,y2 in line:
            cv2.line(img, (x1, y1), (x2, y2), color, thickness)

def draw_fit_line(img, lines, color=[255, 0, 0], thickness=10): # 대표선 그리기
        cv2.line(img, (lines[0], lines[1]), (lines[2], lines[3]), color, thickness)

def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap): # 허프 변환
    lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)
    return lines

def weighted_img(img, initial_img, α=1, β=1., λ=0.): # 두 이미지 operlap 하기
    return cv2.addWeighted(initial_img, α, img, β, λ)

def get_fitline(img, f_lines): # 대표선 구하기   
    lines = np.squeeze(f_lines)
    lines = lines.reshape(lines.shape[0]*2,2)
    rows,cols = img.shape[:2]
    output = cv2.fitLine(lines,cv2.DIST_L2,0, 0.01, 0.01)
    vx, vy, x, y = output[0], output[1], output[2], output[3]
    x1, y1 = int(((img.shape[0]-1)-y)/vy*vx + x) , img.shape[0]-1
    x2, y2 = int(((img.shape[0]/2+200)-y)/vy*vx + x) , int(img.shape[0]/2+200)
    
    result = [x1,y1,x2,y2]
    return result



class Robot:

    def __init__(self, video_path =""):
        self._motion = Motion()
        self._image_processor = ImageProcessor(video_path=video_path)

    def detect_alphabet(self):
        alphabet = self._image_processor.get_door_alphabet()
        self._motion.notice_direction(dir=alphabet)
        exit()
        
    def line_trace(self):
        image = self._image_processor.get_image()
        height, width = image.shape[:2] 

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        low_yellow = np.array([18, 94, 140])
        up_yellow = np.array([48, 255, 255])

        yellowmask = cv2.inRange(hsv, low_yellow, up_yellow)
        yellowedges = cv2.Canny(yellowmask, 75, 150)
        line_arr = hough_lines(yellowedges, 1, 1 * np.pi/180, 30, 100, 150) # 허프 변환
        line_arr = np.squeeze(line_arr)

        temp = np.zeros((image.shape[0], image.shape[1], 3), dtype=np.uint8)
        lines = line_arr[:,None]

        #대표선 구하기
        fit_line = get_fitline(image, lines)
        # 대표선 그리기
        #draw_fit_line(temp, fit_line)

        slope_degree = (np.arctan2(fit_line[1] - fit_line[3], fit_line[0] -   fit_line[2]) * 180) / np.pi

        #result = weighted_img(temp, image) # 원본 이미지에 검출된 선 overlap

        #print(line_arr)
        print(slope_degree)
        #cv2.imshow('result',result) # 결과 이미지 출력
        #cv2.imshow('temp', temp)
        #cv2.imshow('yellowedges', yellowmask)
        #cv2.waitKey(0)