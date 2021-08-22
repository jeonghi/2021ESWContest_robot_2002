from Sensor.ImageProcessor import ImageProcessor
from Actuator.Motion import Motion
import numpy as np
import cv2
import time
import sys

class Robot:

    def __init__(self, file_path =""):
        self._motion = Motion()
        self._image_processor = ImageProcessor(file_path)

    def detect_alphabet(self):
        alphabet = self._image_processor.get_door_alphabet()
        self._motion.notice_direction(dir=alphabet)
        exit()
