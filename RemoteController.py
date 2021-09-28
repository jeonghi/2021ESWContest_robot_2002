import cv2

from Actuator.Motion import Motion

if __name__ == "__main__":
    motion = Motion()
    cap = cv2.VideoCapture(-1)
    is_grabbed = False

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

    walk_list = {'FORWARD':55, 'BACKWARD':56, 'LEFT':57, 'RIGHT':58}
    turn_list = {'SLIDING_LEFT':59, 'SLIDING_RIGHT':60, 'LEFT':61, 'RIGHT':62}

    while True:
        command = input("Input command: ")
        command_key = None

        if command in ["power on", "power off"]:
            command_key = 16
        elif command == "head vcenter":
            command_key = 44
        elif command == "head hcenter":
            command_key = 54
        elif command == "grab on":
            command_key = 64
            is_grabbed = True
        elif command == "grab off":
            command_key = 65
            is_grabbed = False
        elif command == "movearm 1":
            command_key = 76
        elif command == "movearm 2":
            command_key = 77
        elif command == "movearm 3":
            command_key = 78

        elif command.split()[0] == "head": # usage head [direction] [angle] ex) head down 60
            cmd, opt, angle = command.split()
            opt = opt.upper()
            angle = int(angle)
            command_key = dir_list[opt][angle]

        elif command.split()[0] == "walk": # usage walk [direction] [grab]
            grab = ""
            if len(command.split()) == 3:
                cmd, opt, grab = command.split()
            else:
                cmd, opt = command.split()

            opt = opt.upper()
            command_key = walk_list[opt]

            if grab != "":
                command_key += 13

        elif command.split()[0] == "turn": # usage walk [direction] [grab]
            grab = ""
            if len(command.split()) == 3:
                cmd, opt, grab = command.split()
            else:
                cmd, opt = command.split()

            opt = opt.upper()
            command_key = turn_list[opt]

            if grab != "":
                command_key += 11

        elif command == "capture":
            for i in range(10):
                _, img = cap.read()

            cv2.imwrite("debug_image.png", img)
            print("CAPTURED!!")

        elif command == "get head":
            print("current head angle(ver, hor): ", motion.get_head())
        elif command == "exit":
            break
        else:
            continue
        
        if command_key is None:
            continue

        print("Launch " + command)
        motion.TX_data_py2(command_key)
        cv2.waitKey(1)