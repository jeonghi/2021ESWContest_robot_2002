from Brain.Controller import Controller, Mode

def main():
    #Controller.set_test_mode(Mode.DETECT_DIRECTION)
    
    while not Controller.run():
        continue

if __name__ == "__main__":
    main()
    #while True:
        #print(Controller.robot._image_processor.get_milk_info(color="RED"))