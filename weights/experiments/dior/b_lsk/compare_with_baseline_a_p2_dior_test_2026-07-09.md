# DIOR-R 测试集对比记录 - Baseline / A-P2 / B-LSK

日期：2026-07-09

三组模型均使用 `DIOR.yaml` 的 `test` split 评估，评估入口为：

```bash
python scripts/evaluate_obb.py --data DIOR.yaml --split test --mode both
```

结果汇总：

| 模型 | 权重路径 | Params | GFLOPs | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 | 结论 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Baseline | `weights/baselines/dior-r/yolo11n-obb-dior-r-best.pt` | 2,657,623 | 6.6 | 0.8588 | 0.6874 | 0.5146 | 0.3470 | 基线 |
| A-P2 | `weights/experiments/dior/a_p2/best.pt` | 2,698,340 | 10.5 | 0.8779 | 0.6990 | 0.5830 | 0.4215 | 有效提升 |
| B-LSK | `weights/experiments/dior/b_lsk/best.pt` | 2,776,094 | 6.7 | 0.8580 | 0.6809 | 0.5070 | 0.3438 | 未提升 |

B-LSK 相对 baseline：

| 指标 | 变化 |
|---|---:|
| 全尺度 mAP50 | -0.0008 |
| 全尺度 mAP50-95 | -0.0065 |
| 小目标 mAP50 | -0.0076 |
| 小目标 mAP50-95 | -0.0032 |

阶段判断：

- A-P2 是当前有效创新点。
- B-LSK 当前单独实验未提升，暂不建议直接进入 A+B 融合。
- 下一步更适合优先尝试 C，或重新设计 B 的插入位置后再复验。
