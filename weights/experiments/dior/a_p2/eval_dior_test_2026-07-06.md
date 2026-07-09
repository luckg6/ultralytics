# DIOR-R 测试集评估记录 - A-P2

日期：2026-07-06

评估命令：

```bash
python scripts/evaluate_obb.py --model weights/experiments/dior/a_p2/best.pt --data DIOR.yaml --split test --mode both
```

模型信息：

- 权重路径：`weights/experiments/dior/a_p2/best.pt`
- 实验变体：`dior_A_p2`
- 参数量：2,698,340
- GFLOPs：10.5
- 数据集配置：`DIOR.yaml`
- 评估划分：`test`
- 评估设备：NVIDIA GeForce RTX 4060 Laptop GPU, 8188 MiB
- 运行环境：Python 3.10.19, torch 2.1.0+cu121, Ultralytics 8.4.21

全尺度目标结果：

| P | R | mAP50 | mAP50-95 | 图像数 | 实例数 |
|---:|---:|---:|---:|---:|---:|
| 0.863 | 0.818 | 0.8779 | 0.6990 | 2332 | 19651 |

小目标结果，面积 `< 1024`：

| P | R | mAP50 | mAP50-95 | 图像数 | 实例数 |
|---:|---:|---:|---:|---:|---:|
| 0.699 | 0.544 | 0.5830 | 0.4215 | 2332 | 12918 |

备注：

- DIOR-R test 中有 15 个标签因坐标未归一化或越界被评估过程忽略。
- 本次评估对应的 Ultralytics 原始结果目录：`runs/obb/val` 和 `runs/obb/val2`。
