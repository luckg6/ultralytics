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

论文定稿表格使用 DIOR-R official 协议：`epochs=100`、`imgsz=640`、`batch=32`、`cache=RAM`，并按同一 test split 评估。第四章若在 `/home/ws` 新增筛选实验，统一使用 `device=1`、`batch=16`、`cache=ram`；第三章论文复现口径仍以固定 batch 和三 seed 主协议为准。

## 最终评估

训练期间只使用 `val` 选择 `best.pt`。训练结束后在 `test` 上统一运行：

```bash
python scripts/evaluate_obb.py --model weights/checkpoints/chapter3/dior_official_comparisons/seed42/yolov8n_obb/best.pt --data ultralytics/cfg/datasets/DIOR-official-homews.yaml --split test --mode both --device 1
python scripts/evaluate_obb.py --model weights/checkpoints/chapter3/dior_official_comparisons/seed42/yolo26n_obb/best.pt --data ultralytics/cfg/datasets/DIOR-official-homews.yaml --split test --mode both --device 1
```

报告全尺度和小目标的 mAP50、mAP50-95，并从相同评估输出记录 Params/GFLOPs。不要把外部论文作者报告值当成这两组统一协议复现结果。

## 已完成结果

两组训练及官方 test 重评已于 2026-07-21 完成：

| 模型 | Params | GFLOPs | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| YOLOv8n-OBB | 3,081,119 | 8.4 | 0.7038 | 0.5339 | 0.2662 | 0.1759 |
| YOLO26n-OBB | 2,450,307 | 5.5 | 0.6979 | 0.5435 | 0.2581 | 0.1738 |

完整六模型对比、差值和协议说明见 `eval_yolov8n_yolo26n_test_2026-07-21.md`。本文 AB 四项均超过这两个 nano OBB 参照。
