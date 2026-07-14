# C-Dynamic-Plus 与 Baseline/C-Dynamic 对比

- 评估日期：2026-07-14
- 当前模型：`weights/experiments/dior/c_dynamic_plus/best.pt`
- 数据集：DIOR-R `test` split

## 绝对指标

| 模型 | Params | GFLOPs | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 2,657,623 | 6.6 | 0.8588 | 0.6874 | 0.5146 | 0.3470 |
| C-Dynamic | 2,676,940 | 6.6 | 0.8562 | 0.6884 | 0.5173 | 0.3527 |
| C-Dynamic-Plus | 2,696,431 | 6.7 | 0.8588 | 0.6896 | 0.5268 | 0.3541 |

## 相对 Baseline

| 模型 | Params | GFLOPs | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| C-Dynamic | +19,317 | +0.0 | -0.0026 | +0.0010 | +0.0027 | +0.0057 |
| C-Dynamic-Plus | +38,808 | +0.1 | +0.0000 | +0.0022 | +0.0122 | +0.0071 |

## 相对 C-Dynamic

| 模型 | Params | GFLOPs | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| C-Dynamic-Plus | +19,491 | +0.1 | +0.0026 | +0.0012 | +0.0095 | +0.0014 |

## 结论

C-Dynamic-Plus 相比 C-Dynamic 和 baseline 都有小幅正向收益，说明加重 head 几何适应后确实比原 C 更稳，但提升幅度仍不明显。当前不建议把 C-Dynamic-Plus 作为论文主打改进点；如果要做 A+B+C，可作为 C 的候选版本，但优先级低于 A+B-PKI-Lite 的第二数据集复验和论文表格整理。
