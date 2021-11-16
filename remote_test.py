from Brain.Controller import Controller, Mode
from Actuator.Motion import Motion
import time

def main():
    
    while True:
        _motion_ = Motion()
        rx = _motion_.RX_data()
        print(rx)
        if rx == 15:
            print(rx)
            time.sleep(2)
            break
    
    while not Controller.run():
        continue

if __name__ == "__main__":
    main()