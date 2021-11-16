from Brain.Controller import Controller, Mode
from Actuator.Motion import Motion

def main():
    _motion = Motion()
    while True:
        rx = _motion.RX_data2()
        if rx == 15:
            print(rx)
            break

    while not Controller.run():
        continue

if __name__ == "__main__":
    main()