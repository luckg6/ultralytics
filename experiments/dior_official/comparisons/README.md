# DIOR-R 官方划分轻量模型对比

本目录用于在与本文 baseline/A/B/AB 完全相同的 DIOR-R 官方划分和训练超参数下，重新训练 YOLOv8n-OBB 与 YOLO26n-OBB。这里的结果可以进入“统一实验协议”主对比表；旧 `experiments/dior/comparisons/` 配置属于 8:1:1 历史划分，不可混用。

## 训练命令

本地：

```powershell
python scripts/train_obb.py --config experiments/dior_official/comparisons/yolov8n_obb.yaml
python scripts/train_obb.py --config experiments/dior_official/comparisons/yolo26n_obb.yaml
```

`/home/ws` 服务器：

```bash
python scripts/train_obb.py --config experiments/dior_official/comparisons/yolov8n_obb_homews.yaml
python scripts/train_obb.py --config experiments/dior_official/comparisons/yolo26n_obb_homews.yaml
```

本地配置固定 `device=0`、`batch=4`、`cache=disk`；服务器配置固定 `device=1`、`batch=-1`、`cache=ram`。其余主超参数均为 `epochs=100`、`imgsz=640`、`seed=42`、`deterministic=true`。

## 最终评估

训练期间只使用 `val` 选择 `best.pt`。训练结束后在 `test` 上统一运行：

```bash
python scripts/evaluate_obb.py --model runs/obb/dior_official_compare_yolov8n_obb/weights/best.pt --data ultralytics/cfg/datasets/DIOR-official-homews.yaml --split test --mode both --device 1
python scripts/evaluate_obb.py --model runs/obb/dior_official_compare_yolo26n_obb/weights/best.pt --data ultralytics/cfg/datasets/DIOR-official-homews.yaml --split test --mode both --device 1
```

报告全尺度和小目标的 mAP50、mAP50-95，并从相同评估输出记录 Params/GFLOPs。不要把外部论文作者报告值当成这两组统一协议复现结果。
