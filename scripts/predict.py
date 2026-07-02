# from ultralytics import YOLO
# # 加载预训练模型
# model = YOLO('C:\\E\\github\\ultralytics\\modelPt\\yolo11n-obb.pt')
# model = model.to('cuda:0')
# # 查看模型设备（输出cuda:0表示使用GPU）
# print("模型运行设备:", model.device)

# # 简单推理（会自动使用GPU）
# results = model('C:\\E\\github\\ultralytics\\pic\\plane.jpeg',device='0')
# results.save()  # 保存预测后的图片

from ultralytics import YOLO  

# 加载预训练模型
model = YOLO('C:\\E\\github\\ultralytics\\runs\\obb\\train4\\weights\\best.pt')  
model = model.to('cuda:0')  

# 查看模型设备
print("模型运行设备:", model.device)  

results = model(
    'C:\\E\\github\\ultralytics\\pic\\plane2.jpg',
    device='0',
    conf=0.25  # 置信度阈值
)

# 保存预测图片，不带置信度
for result in results:
    result.save(
        filename='C:\\E\\github\\ultralytics\\pic\\5.jpg',
        conf=False  # 不显示置信度
    )  
