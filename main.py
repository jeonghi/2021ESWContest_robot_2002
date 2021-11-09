from Brain.Controller import Controller

def main():

    while not Controller.run():
        continue
    
if __name__ == "__main__":
    #main()
    while True:
        Controller.robot._image_processor.get_arrow_direction(visualization=True)