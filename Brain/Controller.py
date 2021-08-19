from .Sensor.ImageProcessor import ImageProcessor
from .Actuator.Motion import Motion
from .Sensor.HashDetector import HashDetector
from .Sensor.Target import Target
import numpy as np
import cv2
import time
import sys

dir_list = {'E':33, 'W':34, 'S':35, 'N':36}

imageProcessor = ImageProcessor()
img = imageProcessor.get_image()

target = Target(img)
roi = target.get_target_roi()

hashDetector = HashDetector()
direct = hashDetector.detect_direction_hash(roi)

motion = Motion
motion.notice_direction(dir_list[direct])