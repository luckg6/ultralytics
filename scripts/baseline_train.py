# 完整可运行训练脚本
from ultralytics import YOLO
import torch
from multiprocessing import freeze_support  # Windows 必须加

# 固定随机种子，保证完全复现
torch.manual_seed(42)

# Windows 训练必须加这个入口保护
if __name__ == '__main__':
    freeze_support()  # 解决多进程报错
    
    # 基线模型：原始head.py
    model = YOLO('yolo11n-obb.yaml')
    # model.train(
    #     data='dota1_small.yaml',
    #     pretrained='yolo11s.pt',
    #     epochs=100,
    #     batch=2,
    #     imgsz=1024,
    #     seed=42,
    #     device=0,          # 建议指定GPU
    #     #amp=True,          # 混合精度（默认开启）
    #     deterministic=True, # 保证实验可复现（关键！对比实验必须开）
    #     workers=4
    # )
    model.train(
    data='DOTAv1.yaml',
    pretrained='yolo11n-obb.pt',
    epochs=100,
    batch=8,            # 从2提升到8，1024图8G显存刚好
    imgsz=1024,         # 保持1024匹配切片
    seed=42,
    device=0,
    amp=True,           # 必须开！
    deterministic=True,
    workers=4,
    cache='disk',       # 25G用disk cache，避免爆内存
    cos_lr=True,
)