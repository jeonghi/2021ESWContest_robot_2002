from Brain.Controller import Controller, Mode

def main():
    Controller.set_test_mode(mode=Mode.CHECK_AREA_COLOR)

    while not Controller.run():
        continue
if __name__ == "__main__":
    main()
    
#     while True:
#         (line_info, edge_info, _) = Controller.robot._image_processor.line_tracing("YELLOW", ROI=True, line_visualization=True)
#         print(edge_info)
#         alphabet_info = Controller.robot._image_processor.line_checker(line_info)
#         print(alphabet_info)