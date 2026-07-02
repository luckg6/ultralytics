from ultralytics import YOLO

# Load a model
model = YOLO('C:\\E\\github\\ultralytics\\runs\\obb\\train10\\weights\\best.pt')
model = model.to('cuda:0')
#model = YOLO("path/to/best.pt")  # load a custom model

# Validate the model
metrics = model.val(data="DIOR.yaml",split='test',device='0',workers=0)  # no arguments needed, dataset and settings remembered
metrics.box.map  # map50-95(B)
metrics.box.map50  # map50(B)
metrics.box.map75  # map75(B)
metrics.box.maps  # a list containing mAP50-95(B) for each category