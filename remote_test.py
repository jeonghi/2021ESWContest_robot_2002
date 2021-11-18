from Brain.Controller import Controller, Mode
from Actuator.Motion import Motion
import time

def main():
    
    _motion = Motion()
    prx = _motion.RX_data()
    while True:
        rx = _motion.RX_data()
        if prx == rx:
            continue
        prx = rx
        if rx == 15:
            print(rx)
            time.sleep(1)
            break
    
    while not Controller.run():
        continue

if __name__ == "__main__":
    main()