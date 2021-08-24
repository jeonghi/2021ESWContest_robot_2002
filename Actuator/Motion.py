# -*- coding: utf-8 -*-

import platform
import argparse
import cv2
import serial
import time
import sys
from threading import Thread, Lock

#-----------------------------------------------

class Motion:
    def __init__(self):
        self.serial_use = 1
        self.serial_port = None
        self.Read_RX = 0
        self.receiving_exit = 1
        self.threading_Time = 0.01
        self.lock = Lock()
        self.distance = 0
        BPS = 4800  # 4800,9600,14400, 19200,28800, 57600, 115200

        # ---------local Serial Port : ttyS0 --------
        # ---------USB Serial Port : ttyAMA0 --------
        self.serial_port = serial.Serial('/dev/ttyS0', BPS, timeout=0.01)
        self.serial_port.flush()  # serial cls
        self.serial_t = Thread(target=self.Receiving, args=(self.serial_port,))
        self.serial_t.daemon = True
        self.serial_t.start()
        time.sleep(0.1)

    def TX_data_py2(self, one_byte):  # one_byte= 0~255
        self.lock.acquire()
        #with self.lock:
        
        self.serial_port.write(serial.to_bytes([one_byte]))  # python3
        time.sleep(0.01)
        
    def RX_data(self):
        if self.serial_port.inWaiting() > 0:
            result = self.serial_port.read(1)
            RX = ord(result)
            return RX
        else:
            return 0

    def getRx(self):
        return self.lock

    def Receiving(self, ser):
        self.receiving_exit = 1
        while True:
            if self.receiving_exit == 0:
                break
            time.sleep(self.threading_Time)
            # 수신받은 데이터의 수가 0보다 크면 데이터를 읽고 출력
            while ser.inWaiting() > 0:
                # Rx, 수신
                result = ser.read(1)
                RX = ord(result)
                print ("RX=" + str(RX))
                
                # -----  remocon 16 Code  Exit ------
                if RX == 16:
                    self.receiving_exit = 0
                    break
                elif RX == 200:
                    self.lock.release()
                elif RX != 200:
                     self.distance = RX
    
    def notice_direction(self, dir):
        dir_list = {'E':33, 'W':34, 'S':35, 'N':36}
        self.TX_data_py2(dir_list[dir])

    def head_angle(self, dir, angle=0):
        """parameter 설명
        dir: {down, left, right, updown_center, leftright_center}
        angle: {down:{10,20,30,45,60,75,90,100},
        left:{30,45,60,90},
        right:{30,45,60,90}
        }
        """
        center_list = {'UPDOWN_CENTER':45, 'LEFTRIGHT_CENTER':54}
        dir_list = {
            'DOWN':{
            10:37, 20:38, 30:39, 45:40, 60:41, 75:42, 90:43, 100:44
            },
            'LEFT':{
                30:46, 45:47, 60:48, 90:49
            },
            'RIGHT':{
                30:50, 45:51, 60:52, 90:53
            }
        }
        if dir in center_list:
            self.TX_data_py2(center_list[dir])
        else:
            self.TX_data_py2(dir_list[dir][angle])

    def walk(self, dir, loop=1):
        dir_list = {'FORWARD':2, 'BACKWARD':56, 'LEFT':57, 'RIGHT':58}
        for _ in range(loop):
            self.TX_data_py2(dir_list[dir])
            
    def turn(self, dir, loop=1):
        dir_list = {'SLIDING_LEFT':59, 'SLIDING_RIGHT':60, 'LEFT':61, 'RIGHT':62}
        for _ in range(loop):
            self.TX_data_py2(dir_list[dir])

    def get_IR(self) -> int:
        self.TX_data_py2(5)
        self.TX_data_py2(5)
        return self.distance

    def open_door(self):
        self.turn('LEFT', loop=5)
        self.TX_data_py2(63)
        self.walk('RIGHT', loop=10)



# **************************************************
# **************************************************
# **************************************************
if __name__ == '__main__':
    motion = Motion()
    #motion.TX_data_py2(16)
    #motion.notice_direction('N')
    #motion.head_angle('DOWN',10)
    #motion.walk(dir='LEFT', loop=10)
    #motion.turn('RIGHT', loop=10)
    for _ in range(10):
        x = motion.get_IR()
        print('IR value: ', x)
        time.sleep(3)
    pass









