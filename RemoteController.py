import time
from Actuator.Motion import Motion

if __name__ == "__main__":
    motion = Motion()

    while True:
        command = input("Input command: ")
        command_key = None

        if command == "power on" or command == "power off":
            command_key = 16
        elif command == "head vcenter":
            command_key = 44
        elif command == "head hcenter":
            command_key = 54
        elif command == "grab on":
            command_key = 64
        elif command == "grab off":
            command_key = 65
        elif command == "exit":
            break
        else:
            continue
        
        print("Launch " + command)
        motion.TX_data_py2(command_key)