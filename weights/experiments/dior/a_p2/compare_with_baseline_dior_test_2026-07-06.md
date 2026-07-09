# DIOR-R 测试集对比记录 - A-P2 vs Baseline

日期：2026-07-06

两组模型均使用以下设置评估：

```bash
python scripts/evaluate_obb.py --data DIOR.yaml --split test --mode both
```

结果汇总：

| 模型 | 参数量 | GFLOPs | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 2,657,623 | 6.6 | 0.8588 | 0.6874 | 0.5146 | 0.3470 |
| A-P2 | 2,698,340 | 10.5 | 0.8779 | 0.6990 | 0.5830 | 0.4215 |
| 提升 | +40,717 | +3.9 | +0.0191 | +0.0116 | +0.0684 | +0.0745 |

完整评估命令：

```bash
python scripts/evaluate_obb.py --model weights/experiments/dior/a_p2/best.pt --data DIOR.yaml --split test --mode both
python scripts/evaluate_obb.py --model weights/baselines/dior-r/yolo11n-obb-dior-r-best.pt --data DIOR.yaml --split test --mode both
```

备注：

- 这是随 A-P2 权重暂存的阶段性结果记录。
- 小目标评估协议使用 `EVAL_SMALL_ONLY=1`，在 `imgsz=640` 下保留面积 `< 1024` 的目标。
- 两次评估均使用 2332 张有效 test 图像；DIOR-R test 中有 15 个标签因坐标未归一化或越界被忽略。
