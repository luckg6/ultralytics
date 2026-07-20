# SSDD-RBox 本地 test 评估记录

- 日期：2026-07-18
- 数据集：`SSDD-RBox.yaml`
- split：`test`
- 图片数：232
- 全尺度实例数：546
- 小目标实例数：293
- 小目标协议：`imgsz=640` 下输入尺度旋转框面积 `<1024`
- 评估脚本：`scripts/evaluate_obb.py --mode both --imgsz 640 --device 0 --workers 0`

## 训练期 best val

| 实验 | best epoch | val mAP50 | val mAP50-95 |
|---|---:|---:|---:|
| baseline | 97 | 0.98618 | 0.78908 |
| A-P2 | 97 | 0.99480 | 0.79927 |
| B-PKI-Lite | 93 | 0.99252 | 0.80192 |
| A+B-PKI-Lite | 99 | 0.99412 | 0.79525 |

## official test 重评

| 实验 | 权重 | Params | GFLOPs | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---|---:|---:|---:|---:|---:|---:|
| baseline | `runs/obb/ssdd_rbox_baseline_yolo11n_obb/weights/best.pt` | 2,653,918 | 6.6 | 0.9874 | 0.7909 | 0.8916 | 0.6827 |
| A-P2 | `runs/obb/ssdd_rbox_A_p2/weights/best.pt` | 2,695,832 | 10.5 | 0.9913 | 0.7946 | 0.9063 | 0.7071 |
| B-PKI-Lite | `runs/obb/ssdd_rbox_B_pki_lite/weights/best.pt` | 2,695,968 | 6.8 | 0.9904 | 0.7938 | 0.8918 | 0.6869 |
| A+B-PKI-Lite | `runs/obb/ssdd_rbox_AB_p2_pki_lite/weights/best.pt` | 2,737,882 | 10.7 | 0.9918 | 0.7889 | 0.8952 | 0.6909 |

## 相对 baseline

| 实验 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| A-P2 | +0.0039 | +0.0037 | +0.0147 | +0.0244 |
| B-PKI-Lite | +0.0030 | +0.0029 | +0.0002 | +0.0042 |
| A+B-PKI-Lite | +0.0044 | -0.0020 | +0.0036 | +0.0082 |

## 结论

A-P2 在 SSDD-RBox 上是当前最佳结果，尤其小目标 mAP50-95 相对 baseline 提升 +0.0244。B-PKI-Lite 小幅正向。A+B-PKI-Lite 没有形成 DIOR-R 上那种互补优势，小目标 mAP50-95 高于 baseline 但低于 A-P2，全尺度 mAP50-95 低于 baseline 0.0020。

论文层面建议：SSDD-RBox 可作为“轻量船舶小目标数据集”的补充筛选结果，但如果 EI 小论文需要第二数据集呈现 A、B、AB 均稳定正向且 AB 最优，当前 SSDD-RBox 结果还不理想。

## seed=3407 AB 预评估

- 日期：2026-07-18
- 权重：`runs/obb/ssdd_rbox_AB_p2_pki_lite_s3407/weights/best.pt`
- 配置：`experiments/ssdd_rbox/ab_p2_pki_lite_seed3407.yaml`
- 训练期 best val：epoch 99，mAP50 0.99333，mAP50-95 0.79862

| 实验 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| A+B-PKI-Lite seed=42 | 0.9918 | 0.7889 | 0.8952 | 0.6909 |
| A+B-PKI-Lite seed=3407 | 0.9913 | 0.7940 | 0.9062 | 0.6975 |
| seed=3407 相对 seed=42 | -0.0005 | +0.0051 | +0.0110 | +0.0066 |

阶段性判断：seed=3407 对 AB 有明显改善，已经超过 seed=42 baseline 的全尺度 mAP50-95 和小目标 mAP50-95，但仍低于 seed=42 A-P2 的小目标 mAP50-95。由于跨 seed 不能直接作为最终消融结论，下一步必须补训 baseline/A/B 的 seed=3407 版本，再用同一 seed 四组比较。

## seed=3407 baseline 补评估

- 日期：2026-07-18
- 权重：`runs/obb/ssdd_rbox_baseline_yolo11n_obb_s3407/weights/best.pt`
- 配置：`experiments/ssdd_rbox/baseline_seed3407.yaml`
- 训练期 best val：epoch 89，mAP50 0.99001，mAP50-95 0.78240

| 实验 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| baseline seed=3407 | 0.9885 | 0.7891 | 0.9120 | 0.6978 |
| A+B-PKI-Lite seed=3407 | 0.9913 | 0.7940 | 0.9062 | 0.6975 |
| AB 相对 baseline | +0.0028 | +0.0049 | -0.0058 | -0.0003 |

阶段性判断：同 seed=3407 下，AB 的全尺度 mAP50 和 mAP50-95 均高于 baseline，但小目标 mAP50 和 mAP50-95 略低于 baseline，其中小目标 mAP50-95 差距仅 -0.0003。该 seed 已经改善 AB 的全尺度表现，但还不能作为“小目标也稳定超过 baseline”的最终证据；仍需补训 A-P2 和 B-PKI-Lite seed=3407 后判断四组排序。

## seed=2024 AB 预评估

- 日期：2026-07-18
- 权重：`runs/obb/ssdd_rbox_AB_p2_pki_lite_s2024/weights/best.pt`
- 配置：`experiments/ssdd_rbox/ab_p2_pki_lite_seed2024.yaml`
- 训练期 best val：epoch 98，mAP50 0.99441，mAP50-95 0.80094

| 实验 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| A+B-PKI-Lite seed=42 | 0.9918 | 0.7889 | 0.8952 | 0.6909 |
| A+B-PKI-Lite seed=3407 | 0.9913 | 0.7940 | 0.9062 | 0.6975 |
| A+B-PKI-Lite seed=2024 | 0.9887 | 0.7954 | 0.9066 | 0.6999 |

与 seed=42 baseline/A-P2 的参考比较：

| 参考项 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| baseline seed=42 | 0.9874 | 0.7909 | 0.8916 | 0.6827 |
| A-P2 seed=42 | 0.9913 | 0.7946 | 0.9063 | 0.7071 |
| AB seed=2024 相对 baseline seed=42 | +0.0013 | +0.0045 | +0.0150 | +0.0172 |
| AB seed=2024 相对 A-P2 seed=42 | -0.0026 | +0.0008 | +0.0003 | -0.0072 |

阶段性判断：seed=2024 是目前三个 AB seed 中 test mAP50-95 最好的版本，且已经超过 seed=42 baseline 的全尺度和小目标 mAP50-95，也略高于 seed=42 A-P2 的全尺度 mAP50-95。但它的小目标 mAP50-95 仍低于 seed=42 A-P2。跨 seed 不能作为最终公平消融，若继续 SSDD-RBox，建议优先补 baseline seed=2024；若 AB 对同 seed baseline 的小目标优势明显，再补 A/B seed=2024。

## seed=2024 完整四组复核

四组均从 `weights/pretrained/yolo11n-obb.pt` 独立起训，统一使用 `batch=4`、`imgsz=640`、`epochs=100`、`seed=2024`、`cache=disk` 和相同数据划分。test 评估协议与 seed=42 完全一致。

| 实验 | best epoch | best val mAP50-95 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 97 | 0.78861 | 0.9905 | 0.7938 | 0.9029 | 0.6926 |
| A-P2 | 86 | 0.79557 | 0.9867 | 0.7762 | 0.8999 | 0.6925 |
| B-PKI-Lite | 96 | 0.79967 | 0.9880 | 0.7866 | 0.8952 | 0.6742 |
| A+B-PKI-Lite | 98 | 0.80094 | 0.9887 | 0.7954 | 0.9066 | 0.6999 |

相对同 seed baseline：

| 实验 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| A-P2 | -0.0038 | -0.0176 | -0.0030 | -0.0001 |
| B-PKI-Lite | -0.0025 | -0.0072 | -0.0077 | -0.0184 |
| A+B-PKI-Lite | -0.0018 | +0.0016 | +0.0037 | +0.0073 |

结论：seed=2024 下 AB 在全尺度和小目标 mAP50-95 上均为四组最优，并且相对 baseline 分别提升 +0.0016 和 +0.0073；但 A、B 单点均未超过 baseline，因此该 seed 不满足论文期望的“A、B、AB 均正向且 AB 最优”。不能只取 seed=42 的 A/B 与 seed=2024 的 AB 拼接成最终消融表。

## seed=0 AB 预筛选

- 权重：`runs/obb/ssdd_rbox_AB_p2_pki_lite_s0/weights/best.pt`
- 配置：`experiments/ssdd_rbox/ab_p2_pki_lite_seed0.yaml`
- 训练期 best val：epoch 86，mAP50 0.99307，mAP50-95 0.78241
- test：全尺度 mAP50 0.9908、mAP50-95 0.7762；小目标 mAP50 0.8791、mAP50-95 0.6676

结论：seed=0 的 AB 明显低于 seed=42/3407/2024 的 AB，也低于现有 baseline 参考结果，因此预筛选失败，不再补训该 seed 的 baseline、A 和 B。

## 多 seed 总结

- seed=42：A、B 单点均正向，但 AB 没有超过 A，且全尺度 mAP50-95 略低于 baseline。
- seed=3407：AB 全尺度优于同 seed baseline，但小目标 mAP50-95 低 0.0003，未继续补 A/B。
- seed=2024：AB 的两项 mAP50-95 均优于同 seed baseline，但 A、B 单点退化。
- seed=0：AB 预筛选明显退化，已淘汰。

当前没有任何一个 SSDD-RBox seed 同时满足“A、B、AB 都高于 baseline，且 AB 最优”。SSDD-RBox 对随机种子较敏感，不建议继续以挑选单次最好 seed 的方式作为论文主要证据；若继续使用该数据集，更可靠的做法是报告多 seed 均值和标准差，或调整一套对四种结构统一生效的训练超参数后重新做完整四组。
