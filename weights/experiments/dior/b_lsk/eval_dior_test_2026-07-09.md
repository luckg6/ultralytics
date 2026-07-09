# DIOR-R 测试集评估记录 - B-LSK

日期：2026-07-09

评估命令：

```bash
python scripts/evaluate_obb.py --model weights/experiments/dior/b_lsk/best.pt --data DIOR.yaml --split test --mode both
```

模型信息：

- 权重路径：`weights/experiments/dior/b_lsk/best.pt`
- 实验变体：`dior_B_lsk`
- 模块：轻量 `SPPFLSK` 遥感上下文注意力
- 参数量：2,776,094
- GFLOPs：6.7
- 数据集配置：`DIOR.yaml`
- 评估划分：`test`
- 评估设备：NVIDIA GeForce RTX 4060 Laptop GPU, 8188 MiB
- 运行环境：Python 3.10.19, torch 2.1.0+cu121, Ultralytics 8.4.21

评估结果：

| 评估范围 | mAP50 | mAP50-95 |
|---|---:|---:|
| 全尺度目标 | 0.8580 | 0.6809 |
| 小目标，面积 `< 1024` | 0.5070 | 0.3438 |

与 baseline 对比：

| 指标 | Baseline | B-LSK | 变化 |
|---|---:|---:|---:|
| 全尺度 mAP50 | 0.8588 | 0.8580 | -0.0008 |
| 全尺度 mAP50-95 | 0.6874 | 0.6809 | -0.0065 |
| 小目标 mAP50 | 0.5146 | 0.5070 | -0.0076 |
| 小目标 mAP50-95 | 0.3470 | 0.3438 | -0.0032 |

结论：

- 当前 B-LSK 单独实验没有带来提升，属于负向或无效消融。
- 当前版本不建议直接作为 A+B 融合基础；后续如果继续做 B，建议重新调整注意力插入位置或模块强度。
- 本次评估对应的 Ultralytics 原始结果目录：`runs/obb/val7` 和 `runs/obb/val8`。
- 评估图已归档到：`experiments/logs/dior/b_lsk/eval_all/` 和 `experiments/logs/dior/b_lsk/eval_small/`。
