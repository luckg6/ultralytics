# A+B-PKI-Lite+C-Chol-Lite 与 Baseline/AB/ABC-Plus 对比

- 日期：2026-07-16
- 数据集：DIOR-R `test`
- 模型：`weights/experiments/dior/abc_p2_pki_chol_lite/best.pt`

## 绝对指标

| 模型 | Params | GFLOPs | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 2,657,623 | 6.6 | 0.8588 | 0.6874 | 0.5146 | 0.3470 |
| A+B-PKI-Lite | 2,740,390 | 10.7 | 0.8859 | 0.7198 | 0.5958 | 0.4288 |
| A+B-PKI-Lite+C-Plus | 2,784,390 | 11.1 | 0.8832 | 0.7149 | 0.5838 | 0.4242 |
| A+B-PKI-Lite+C-Chol-Lite | 2,819,058 | 10.7 | 0.8862 | 0.7190 | 0.5774 | 0.4209 |

## 相对变化

| 对比 | Params | GFLOPs | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ABC-Chol 相对 Baseline | +161,435 (+6.07%) | +4.1 | +0.0274 | +0.0316 | +0.0628 | +0.0739 |
| ABC-Chol 相对 A+B-PKI-Lite | +78,668 (+2.87%) | +0.0 | +0.0003 | -0.0008 | -0.0184 | -0.0079 |
| ABC-Chol 相对 ABC-Plus | +34,668 (+1.25%) | -0.4 | +0.0030 | +0.0041 | -0.0064 | -0.0033 |

## 结论

A+B-PKI-Lite+C-Chol-Lite 相对 baseline 仍有明显提升，并且比 A+B-PKI-Lite+C-Plus 的全尺度指标更好；但它没有超过 A+B-PKI-Lite 的 mAP50-95 和小目标指标。因此当前 DIOR-R 主结果候选仍建议使用 A+B-PKI-Lite，ABC-Chol 可作为三创新点融合消融行或补充结果。

