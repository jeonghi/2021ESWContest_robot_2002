from Brain.Controller import Controller, Mode
from Actuator.Motion import Motion

def main():
    _motion = Motion()
    while True:
        rx = _motion.RX_data()
        print(rx)
        if rx == 1:
            break

    while not Controller.run():
        continue

if __name__ == "__main__":
    main()