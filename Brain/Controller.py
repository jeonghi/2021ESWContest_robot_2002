from Sensor.ImageProcessor import ImageProcessor
from Sensor.LineDetector import LineDetector
from Actuator.Motion import Motion
from Sensor.ColorChecker import get_pixel_rate4green
import numpy as np
import cv2
import time
import sys

import cv2
import numpy as np


class Robot:

	def __init__(self, video_path =""):
		self._motion = Motion()
		self._image_processor = ImageProcessor(video_path=video_path)
		self._line_detector = LineDetector()

	def detect_alphabet(self):
		self._motion.head_angle('DOWN', 75)
		flag = True
		alphabet = None
		while alphabet is None:
			alphabet = self._image_processor.get_door_alphabet()
			
			if alphabet is not None:
				break

			if flag:
				self._motion.walk("RIGHT")
			else:
				self._motion.walk("LEFT")
			flag = not flag
		self._motion.notice_direction(dir=alphabet)

	def line_tracing(self):
		while True:
			src = self._image_processor.get_image(visualization=False)
			src = cv2.resize(src, dsize=(480, 640))
			ans, src = self._line_detector.get_all_lines(src)
			cv2.imshow('src', src)
			cv2.waitKey(1)
			# ans list : [0]현재 방향(동작 보정 각도), [1]vertical, [2]vertical-x, [3]horizontal, [4]horizontal-y, [5]horizontal-minx, [6]horizontal-max
			if ans[1] is not None and ans[3] is None: #직진
				print('FORWARD', ans)
				self._motion.walk(dir='FORWARD', loop=1) # 일정 y좌표때 멈추기
			elif ans[1] is not None and ans[3] is not None:
				# ans[5] 수평선의 마지막 x좌표 - 중앙보다 작으면 ㄱ , 중앙보다 크면 T 
				if 200 < ans[4]:
					if ans[5] < 50 and ans[6] < 340:
						# ㄱ자
						print('ㄱ자', ans)
						self._motion.turn('LEFT', loop=4)
					elif ans[5] > 300 and ans[6]>600:
						# ㄴ자
						print('ㄴ자', ans[0])
						self._motion.turn('RIGHT', loop=4)
					else:
						# T자
						print('T자', ans)
						return 0
				else:
					print('FORWARD', ans)
					self._motion.walk(dir='FORWARD')


			elif ans[1] is None and ans[3] is None:
				if ans[0] < 80:
					print('RIGHT', ans)
					self._motion.turn(dir='RIGHT', loop=1)
				elif ans[0] > 100:
					print('LEFT', ans)
					self._motion.turn(dir='LEFT', loop=1)


			elif ans[1] is None and ans[3] is not None:
				print("ans[1] is None and ans[3] is not None")
				print(ans)
			else:
				print("else")

	def line_tracing_sol(self, mode = 'LEFT'):
		mode = mode
		self._motion.head_angle('DOWN', 10)
		while True:
			src = self._image_processor.get_image(visualization=False)
			src = cv2.resize(src, dsize=(640,480))
			ans, src = self._line_detector.get_all_lines(src)
			cv2.imshow('src', src)
			cv2.waitKey(1)

			# ans list : [0]현재 방향(동작 보정 각도), [1]vertical, [2]vertical-x, [3]horizontal, [4]horizontal-y, [5]horizontal-minx, [6]horizontal-max

			if ans[1] is not None and ans[3] is None: #직선만 검출
				if 280 < ans[2] <360:
					print('FORWARD', ans)
					self._motion.walk(dir='FORWARD', loop=1) # 일정 y좌표때 멈추기
				else:
					if ans[2] < 280:
						print('MODIFY walk --LEFT', ans)
						self._motion.walk(dir='LEFT', loop=1)
					elif ans[2] > 360:
						print('MODIFY walk --RIGHT', ans)
						self._motion.walk(dir='RIGHT', loop=1)

			elif ans[1] is None and ans[3] is None: # 아무 직선도 검출 안됨(수직, 수평선 검출될 때까지 계속 회전)
				if ans[0] < 80:
					print('MODIFY angle --LEFT', ans)
					self._motion.turn(dir='LEFT', loop=1)
				elif ans[0] > 100:
					print('MODIFY angle --RIGHT', ans)
					self._motion.turn(dir='RIGHT', loop=1)

			else:
			#elif ans[1] is None and ans[3] is not None: # 수평만 검출, ㄱ자랑 T자 앞에 있다는 뜻
				# 가려는 방향으로 두칸 이동 및 회전
				#print('INFRONT OF LINE --go LEFT 2 and trun LEFT', ans)

			#elif ans[1] is not None and ans[3] is not None: # 수직 수평 둘다 검출
				# ans[5] 수평선의 마지막 x좌표 - 중앙보다 작으면 ㄱ , 중앙보다 크면 T 
				if ans[4] > 150: 
					if ans[5] < 50 and ans[6] < 340:
						# ㄱ자
						print('ㄱ자', ans)
						self._motion.turn('LEFT', loop=8)
					elif ans[5] > 300 and ans[6]>600:
						# ㄴ자
						print('ㄴ자', ans)
						self._motion.turn('RIGHT', loop=8)
					else:
						# T자 :: 가려는 방향으로 두칸 이동 및 회전
						print('T자 :: INFRONT OF LINE --go WANT mode 4 and trun WANT mode', ans)
						self._motion.walk(mode, 4)
						self._motion.turn(mode, 8)
				else:
					self._motion.walk('FORWARD')
					print(ans[4], 'low then 150')

	def test_green(self):
		self._motion.head_angle('DOWN', 45)
		self._motion.head_angle('RIGHT', 30)
		src = self._image_processor.get_image()
		get_pixel_rate4green(src)
		
