# 实验目录总览

本目录保留训练配置、数据集实验记录和阶段性评估。当前小论文/硕士第三章主线使用 DIOR-R official 与 HRSID-derived OBB；第四章已另设 `experiments/chapter4/`，作为 LSKNet-T backbone baseline 及后续 C/D 消融入口。

## 第三章主实验

第三章方法为 FSPC-OBB，即 FSPB(A) + LPCF(B)。它基于 YOLO11n-OBB，主要从 Neck 和 Head/预测端增强小目标细节传递和多尺度上下文融合。

| 数据集 | 目录 | 状态 | 论文用途 |
|---|---|---|---|
| DIOR-R official | `experiments/dior_official/` | baseline、A、B、A+B、YOLOv8n、YOLO26n 已完成 | 第三章第一数据集主实验 |
| HRSID-derived OBB | `experiments/hrsid/` | baseline、A、B、A+B 三 seed 已完成 | 第三章第二数据集主实验 |

### 单次最佳消融结果

精度为百分数，参数量和 GFLOPs 使用统一评估摘要口径。

| Dataset | Variant | Params (M) | GFLOPs | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---|---:|---:|---:|---:|---:|---:|
| DIOR-R | Baseline | 2.658 | 6.6 | 71.11 | 54.31 | 27.32 | 17.96 |
| DIOR-R | Baseline + A | 2.698 | 10.5 | 71.60 | 53.94 | 28.43 | 19.80 |
| DIOR-R | Baseline + B | 2.700 | 6.8 | 71.11 | 54.24 | 27.68 | 18.23 |
| DIOR-R | Baseline + A + B | 2.740 | 10.7 | **72.25** | **54.55** | **29.20** | **20.42** |
| HRSID | Baseline | 2.654 | 6.6 | 75.13 | 39.63 | 71.60 | 37.36 |
| HRSID | Baseline + A | 2.696 | 10.5 | 93.71 | 67.06 | 91.78 | 66.10 |
| HRSID | Baseline + B | 2.696 | 6.8 | 76.20 | 41.91 | 72.73 | 38.88 |
| HRSID | Baseline + A + B | 2.738 | 10.7 | **93.96** | **67.65** | **92.12** | **66.87** |

### 三 seed 稳定性

| Dataset | Variant | Seeds | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---|---:|---:|---:|---:|---:|
| DIOR-R | Baseline | 3 | 71.02 ± 0.10 | 54.19 ± 0.12 | 27.17 ± 0.16 | 17.79 ± 0.17 |
| DIOR-R | Baseline + A | 3 | 71.47 ± 0.13 | 53.83 ± 0.12 | 28.27 ± 0.16 | 19.61 ± 0.19 |
| DIOR-R | Baseline + B | 3 | 71.03 ± 0.08 | 54.15 ± 0.09 | 27.55 ± 0.13 | 18.10 ± 0.14 |
| DIOR-R | Baseline + A + B | 3 | **72.12 ± 0.14** | **54.43 ± 0.12** | **29.01 ± 0.19** | **20.24 ± 0.18** |
| HRSID | Baseline | 3 | 74.96 ± 0.18 | 39.42 ± 0.21 | 71.37 ± 0.23 | 37.13 ± 0.23 |
| HRSID | Baseline + A | 3 | 93.57 ± 0.15 | 66.88 ± 0.18 | 91.62 ± 0.17 | 65.91 ± 0.19 |
| HRSID | Baseline + B | 3 | 76.02 ± 0.18 | 41.71 ± 0.20 | 72.51 ± 0.22 | 38.66 ± 0.23 |
| HRSID | Baseline + A + B | 3 | **93.88 ± 0.09** | **67.48 ± 0.17** | **91.99 ± 0.13** | **66.70 ± 0.18** |

## 第四章实验

第四章是与第三章并列互补的路线，不再写成严格升级版，也不定位为解决第三章 GFLOPs 上升的问题。

入口目录：`experiments/chapter4/`

当前 baseline：

```text
LSKNet-T Backbone
+ necessary channel adapters
+ original YOLO11 Neck
+ original YOLO11 OBB Head
```

该 baseline 不继承第三章 FSPB/LPCF。LSKNet-T 只是基础架构选择，不作为创新；后续 C、D 才是第四章创新点。

当前 DIOR-R official 单种子结果：

| Model | Params (M) | GFLOPs | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---:|---:|---:|---:|---:|---:|
| Chapter 3 A+B | 2.740 | 10.7 | 72.25 | 54.55 | 29.20 | 20.42 |
| LSKNet-T baseline | 5.728 | 18.7 | 73.72 | 56.88 | 27.69 | 18.15 |

该结果只能说明 LSKNet-T 混合结构接入成功、可稳定训练，并具有较强全尺度检测潜力。由于模型容量和计算量明显不同，不能据此声称 LSKNet-T baseline 公平优于第三章 A+B 或 YOLO11 原生 backbone。第四章后续必须首先证明 C、D 相对于 LSKNet-T baseline 有效。

## DIOR-R 同协议模型对比

| Model | Params | GFLOPs | mAP50 | mAP50:95 |
|---|---:|---:|---:|---:|
| YOLOv8n-OBB | 3.081M | 8.4 | 70.38 | 53.39 |
| YOLO11n-OBB | 2.658M | 6.6 | 71.11 | 54.31 |
| YOLO26n-OBB | 2.450M | 5.5 | 69.79 | 54.35 |
| FSPC-OBB | 2.740M | 10.7 | **72.25** | **54.55** |

详细记录位于 `experiments/dior_official/comparisons/`。

## 历史与筛选实验

| 目录 | 当前定位 |
|---|---|
| `experiments/dior/` | 早期 DIOR-R 8:1:1 划分、A/B/C/AB/ABC 探索。A+B 在该划分仍为最佳，可作为鲁棒性附加说明，但不能与 official split 主表混用。 |
| `experiments/ucas_aod/` | 第二数据集筛选。数据较轻，但 A 和 AB 未稳定超过 baseline。 |
| `experiments/vedai/` | 第二数据集筛选。B 有一定正向，A/AB 未形成主论文所需互补趋势。 |
| `experiments/ssdd_rbox/` | 第二数据集筛选。不同 seed 下排序不稳定，未进入主表。 |
| `experiments/hrsc2016/` | 快速筛选。AB 低于 baseline，停止扩展。 |

## 复现原则

- 同一数据集内的 baseline、A、B、A+B 必须共享 split、epochs、batch、imgsz、seed 集合、初始化、增强、NMS 和评估设置。
- 第四章 C、D 消融必须共享 LSKNet-T baseline 的数据划分、训练轮数、初始化和评估协议。
- `best.pt` 只由 validation fitness 选择，test split 只做最终评估。
- 不允许跨 seed、跨数据集或跨划分拼接单行结果。
- 旧实验配置保留是为了可追溯，不代表论文当前主线。
