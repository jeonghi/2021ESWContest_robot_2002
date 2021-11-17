import os
os.chdir("/home/pi/2021ESWContest_robot_2002/")

from Brain.Controller import Controller, Mode

def main():
    #Controller.set_test_mode(Mode.CHECK_AREA_COLOR)
    while not Controller.run():
        continue

if __name__ == "__main__":
    main()
    #while True:
        #line, edge, _ = Controller.robot._image_processor.line_tracing(color = 'YELLOW', edge_visualization = True, ROI_edge=True)
        #print(edge["EDGE_POS"][0] + 200, edge["EDGE_POS"][1])
        #print(line)
        #print(Controller.robot._image_processor.get_door_alphabet_using_iou(visualization=True))

