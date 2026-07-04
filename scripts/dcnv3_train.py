# 完整可运行训练脚本
import torch

from ultralytics import YOLO

# 固定随机种子
torch.manual_seed(42)

# 改进版：head.py 已替换为DCNv3
model = YOLO("yolo11s-obb.yaml")
model.train(
    data="DOTAv1.yaml",
    pretrained="yolo11s.pt",
    epochs=100,
    batch=16,
    imgsz=1024,
    seed=42,
    device=0,
    amp=True,
    deterministic=True,  # 关键：保证对比公平
)
