from ultralytics import YOLO
from multiprocessing import freeze_support

if __name__ == '__main__':
    freeze_support()

    model = YOLO(r'C:\E\github\ultralytics\runs\obb\train10\weights\last.pt')

    model.train(
        resume=True
    )