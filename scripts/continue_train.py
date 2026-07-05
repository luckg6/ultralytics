from ultralytics import YOLO
from multiprocessing import freeze_support

if __name__ == '__main__':
    freeze_support()

    model = YOLO(r'C:\E\github\ultralytics\weights\baselines\dior-r\yolo11n-obb-dior-r-last.pt')

    model.train(
        resume=True
    )
