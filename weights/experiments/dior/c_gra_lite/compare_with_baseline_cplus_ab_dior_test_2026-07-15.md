# C-GRA-Lite 与 baseline / C-Plus / AB 对比

- 日期：2026-07-15
- 数据集：DIOR-R
- split：test
- 当前模型权重：`weights/experiments/dior/c_gra_lite/best.pt`

## 指标对比

| 模型 | Params | GFLOPs | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 2,657,623 | 6.6 | 0.8588 | 0.6874 | 0.5146 | 0.3470 |
| C-Dynamic | 2,676,940 | 6.6 | 0.8562 | 0.6884 | 0.5173 | 0.3527 |
| C-Dynamic-Plus | 2,696,431 | 6.7 | 0.8588 | 0.6896 | 0.5268 | 0.3541 |
| C-GRA-Lite | 2,713,135 | 6.7 | 0.8583 | 0.6861 | 0.5219 | 0.3522 |
| A+B-PKI-Lite | 2,740,390 | 10.7 | 0.8859 | 0.7198 | 0.5958 | 0.4288 |

## 相对 baseline

| 指标 | 变化 |
|---|---:|
| Params | +55,512（+2.09%） |
| GFLOPs | +0.1 |
| 全尺度 mAP50 | -0.0005 |
| 全尺度 mAP50-95 | -0.0013 |
| 小目标 mAP50 | +0.0073 |
| 小目标 mAP50-95 | +0.0052 |

## 相对 C-Dynamic-Plus

| 指标 | 变化 |
|---|---:|
| Params | +16,704 |
| GFLOPs | +0.0 |
| 全尺度 mAP50 | -0.0005 |
| 全尺度 mAP50-95 | -0.0035 |
| 小目标 mAP50 | -0.0049 |
| 小目标 mAP50-95 | -0.0019 |

## 结论

C-GRA-Lite 的小目标指标相对 baseline 仍有轻微正向，但全尺度 mAP50-95 低于 baseline，也没有超过 C-Dynamic-Plus。它没有达到“替换 C-Plus 并推动 ABC 超过 A+B-PKI-Lite”的预期。

当前不建议继续训练 A+B-PKI-Lite+C-GRA-Lite；主结果仍建议使用 A+B-PKI-Lite，C-GRA-Lite 可作为已尝试但未优于 C-Plus 的 C 分支消融记录。
