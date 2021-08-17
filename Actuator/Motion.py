# -*- coding: utf-8 -*-

import platform
import numpy as np
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
        #self.lock.acquire()
        with self.lock:
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
                
                print("RX=" + str(RX))
                
                # -----  remocon 16 Code  Exit ------
                if RX == 16:
                    self.receiving_exit = 0
                    break

    def init(self):
        if not self.lock:
            self.TX_data_py2(MOTION["SIGNAL"]["INIT"])
            while self.getRx():
                continue
        pass

    def init2(self):
        if not self.lock:
            self.TX_data_py2(MOTION["SIGNAL"]["INIT2"])
            while self.getRx():
                continue
        pass
    
    def notice_direction(self, dir):
        dir_list = {'E':33, 'W':34, 'S':35, 'N':36}
        print(dir_list[dir])
        self.TX_data_py2(dir_list[dir])        
#

# **************************************************
# **************************************************
# **************************************************
if __name__ == '__main__':
    motion = Motion()
#    motion.TX_data_py2(33)
    motion.notice_direction('N')
   
    pass









