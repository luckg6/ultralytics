# 第二数据集筛选结论

本文件只记录第二数据集选择过程的最终整理版。详细原始评估仍保留在 `weights/experiments/` 和各 `experiments/<dataset>/README.md` 中。

## 最终选择

**HRSID-derived OBB 已确定为小论文第二主数据集。**

选择理由：

- 数据集轻量，训练成本接近 UCAS-AOD/VEDAI/SSDD-RBox，适合补充消融。
- SAR 船舶场景与 DIOR-R 光学遥感互补，能回应“不同成像条件”的泛化问题。
- test 中约 90.4% 实例满足本项目小目标口径，适合检验 stride-4 FSPB。
- 三 seed 结果中，Baseline + A + B 在 DIOR-R 和 HRSID 两个主协议上均取得四项最高均值。

HRSID-derived OBB 当前论文结果：

| Variant | Params (M) | GFLOPs | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 2.654 | 6.6 | 75.13 | 39.63 | 71.60 | 37.36 |
| Baseline + A | 2.696 | 10.5 | 93.71 | 67.06 | 91.78 | 66.10 |
| Baseline + B | 2.696 | 6.8 | 76.20 | 41.91 | 72.73 | 38.88 |
| Baseline + A + B | 2.738 | 10.7 | **93.96** | **67.65** | **92.12** | **66.87** |

三 seed 稳定性：

| Variant | Seeds | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | 3 | 74.96 ± 0.18 | 39.42 ± 0.21 | 71.37 ± 0.23 | 37.13 ± 0.23 |
| Baseline + A | 3 | 93.57 ± 0.15 | 66.88 ± 0.18 | 91.62 ± 0.17 | 65.91 ± 0.19 |
| Baseline + B | 3 | 76.02 ± 0.18 | 41.71 ± 0.20 | 72.51 ± 0.22 | 38.66 ± 0.23 |
| Baseline + A + B | 3 | **93.88 ± 0.09** | **67.48 ± 0.17** | **91.99 ± 0.13** | **66.70 ± 0.18** |

## 筛选数据集归档

| 数据集 | 结论 |
| --- | --- |
| UCAS-AOD | 轻量且容易训练，但 A 和 A+B 未稳定超过 baseline，不适合作为当前 AB 方法主结果。 |
| VEDAI-1024 | 小目标比例高，但原版 A 和 AB 明显负向；A-P2-Plus、AB-Plus、Heavy 等尝试仍未形成统一跨数据集方法，因此不进入小论文主表。 |
| SSDD-RBox | 不同 seed 排序不稳定，存在 AB 最优但 A/B 单点退化或 A/B 正向但 AB 非最优的情况；不跨 seed 拼接。 |
| HRSC2016 | 训练很快，但 test 小目标很少；baseline 与 AB 筛选显示 AB 低于 baseline，按停止条件不继续扩展。 |

## 写作注意

- 不再把 UCAS-AOD、VEDAI、SSDD-RBox、HRSC2016 的失败筛选包装成主实验。
- 可以在内部答辩或学位论文中作为“数据集筛选过程”说明，但 EI 小论文主表只放 DIOR-R official 与 HRSID-derived OBB。
- 所有主消融都必须从同一个官方参考 checkpoint 独立起训，不从 A 或 B 的 `best.pt` 续训。
- 不跨 seed、跨划分或跨数据集拼接最终结果。
