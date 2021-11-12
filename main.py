from Brain.Controller import Controller, Mode

def main():
    Controller.set_test_mode(mode=Mode.CHECK_AREA_COLOR)

    while not Controller.run():
        continue
    
def img_test():
    while True:
         #corner = Controller.robot._image_processor.get_yellow_line_corner(visualization=True)
         #print(corner)
         #(line_info, edge_info, _) = Controller.robot._image_processor.line_tracing("YELLOW", ROI=False, ROI_edge=True, edge_visualization=True, line_visualization=False)
         #print(line_info, edge_info)
         #alphabet_info = Controller.robot._image_processor.line_checker(line_info)
         #print(alphabet_info)
         #continue
    
if __name__ == "__main__":
    main()
    #img_test()