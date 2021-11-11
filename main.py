from Brain.Controller import Controller, Mode

def main():
    Controller.set_test_mode(mode=Mode.GO_TO_NEXT_ROOM)

    while not Controller.run():
        continue
if __name__ == "__main__":
    main()
    #while True:
         #(line_info, edge_info, _) = Controller.robot._image_processor.line_tracing("GREEN", ROI=False, edge_visualization=True)
         #print(edge_info)
         #alphabet_info = Controller.robot._image_processor.line_checker(line_info)
         #print(alphabet_info)