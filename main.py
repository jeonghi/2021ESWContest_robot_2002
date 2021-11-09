from Brain.Controller import Controller, Mode

def main():
    Controller.set_test_mode(mode=Mode.CHECK_AREA_COLOR)

    while not Controller.run():
        continue
if __name__ == "__main__":
    main()
    #while True:
        #Controller.robot._image_processor.get_arrow_direction(visualization=True)