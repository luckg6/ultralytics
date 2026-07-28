# YOLOv8n-OBB 与 YOLO26n-OBB 官方 DIOR-R test 评估

评估日期：2026-07-21

> 整理说明：本文件保留 YOLOv8n-OBB、YOLO26n-OBB 与本项目模型的同 split test 评估记录。论文最终表格以 `paper/ippr2026/main.pdf` 为准；本文件中的自动 batch 描述是当时训练记录，不应覆盖论文主协议中的固定 batch 与三 seed 消融说明。

## 协议

- 数据：DIOR-R 官方 5,862/5,863/11,738 train/val/test 划分。
- 训练：100 epochs、`imgsz=640`、`seed=42`、`deterministic=true`、`cache=ram`、Ultralytics 自动 batch。
- 初始化：分别使用官方 `yolov8n-obb.pt` 与 `yolo26n-obb.pt`，不使用本文 YOLO11n-OBB 或 AB 权重初始化。
- 选择：训练期间仅根据 val 选择 `best.pt`，最后统一在 test 上运行 `scripts/evaluate_obb.py --mode both`。
- 数据过滤：与 baseline/A/B/AB 相同，test 中 48 张含越界标签的图像被 Ultralytics 整图忽略，实际评估 11,690 张图像。
- 小目标：在 640 输入空间按 OBB 面积 `w*h<1024 px²` 筛选，属于本项目附加协议。

## 结果

| 模型 | Params | GFLOPs | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| YOLOv8n-OBB | 3,081,119 | 8.4 | 0.7038 | 0.5339 | 0.2662 | 0.1759 |
| YOLO11n-OBB baseline | 2,657,623 | 6.6 | 0.7111 | 0.5431 | 0.2732 | 0.1796 |
| YOLO26n-OBB | 2,450,307 | 5.5 | 0.6979 | 0.5435 | 0.2581 | 0.1738 |
| A-P2 | 2,698,340 | 10.5 | 0.7160 | 0.5394 | 0.2843 | 0.1980 |
| B-PKI-Lite | 2,699,673 | 6.8 | 0.7111 | 0.5424 | 0.2768 | 0.1823 |
| A+B-PKI-Lite | **2,740,390** | **10.7** | **0.7225** | **0.5455** | **0.2920** | **0.2042** |

Params 和 GFLOPs 均取本次 test 评估的 fused model 摘要；其中 baseline/A/B/AB 沿用同一评估脚本此前归档的摘要。

## 差值

| 对比 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| YOLOv8n - baseline | -0.0073 | -0.0092 | -0.0070 | -0.0037 |
| YOLO26n - baseline | -0.0132 | +0.0004 | -0.0151 | -0.0058 |
| AB - YOLOv8n | +0.0187 | +0.0116 | +0.0258 | +0.0283 |
| AB - YOLO26n | +0.0246 | +0.0020 | +0.0339 | +0.0304 |

## 结论

YOLOv8n-OBB 四项均低于 YOLO11n-OBB baseline。YOLO26n-OBB 的参数量和 GFLOPs 最低，全尺度 mAP50-95 比 baseline 高 0.0004，但全尺度 mAP50 及两项小目标指标更低。本文 A+B-PKI-Lite 在六个同协议模型中四项均为最高，并分别在四项上同时超过 YOLOv8n-OBB 与 YOLO26n-OBB。

该结论只适用于本项目统一训练和评估协议。外部论文作者报告值仍需单独列出并标注 `Reported under authors' settings`。
