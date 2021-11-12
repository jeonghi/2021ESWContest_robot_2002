from Brain.Controller import Controller, Mode

def get_distance_from_baseline(pos: tuple, baseline: tuple = (320, 370)):
    """
    :param box_info: 우유팩 위치 정보를 tuple 형태로 받아온다. 우유팩 영역 중심 x좌표와 y좌표 순서
    :param baseline: 우유팩 위치 정보와 비교할 기준점이다.
    :return: 우유팩이 지정한 기준점으로부터 떨어진 상대적 거리를 tuple로 반환한다.
    """
    bx, by = baseline
    cx, cy = pos
    return bx - cx, by - cy

def main():
    Controller.set_test_mode(mode=Mode.CHECK_AREA_COLOR)

    while not Controller.run():
        continue
    
def img_test():
    while True:
        box_info = Controller.robot._image_processor.get_milk_info(color="RED", visualization=True)
        (dx, dy) = get_distance_from_baseline(pos=box_info)
        print(dx, dy)
        if -40 <= dx <= 40:
            print("기준점에서 적정범위. 전진 전진")
            cls.robot._motion.walk(dir='FORWARD', loop=1, width=width)
        elif dx < -40:
            cls.robot._motion.walk(dir='RIGHT', loop=1)
        elif dx > 40:  # 왼쪽
            print("기준점에서 왼쪽으로 많이 치우침. 조정한다")
            cls.robot._motion.walk(dir='LEFT', loop=1)
            
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