# 完整可运行训练脚本
from multiprocessing import freeze_support  # Windows 必须加

import torch

from ultralytics import YOLO

# 固定随机种子，保证完全复现
torch.manual_seed(42)

# Windows 训练必须加这个入口保护
if __name__ == "__main__":
    freeze_support()  # 解决多进程报错

    # 基线模型：原始head.py
    model = YOLO("yolo11n-obb.yaml")

    model.train(
        data="DIOR.yaml",
        pretrained="yolo11n-obb.pt",
        epochs=100,
        batch=16,
        imgsz=640,  # 保持640匹配切片
        seed=42,
        device=0,
        amp=True,  # 必须开！
        deterministic=True,
        workers=4,
        cache="disk",  # 用disk cache，避免爆内存
        cos_lr=True,
    )
