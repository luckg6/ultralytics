# 实验目录总览

本目录保留全部训练配置和数据集实验记录。当前论文主线只使用 DIOR-R official 与 HRSID-derived OBB；其他目录是历史探索或第二数据集筛选记录。

## 当前论文主实验

| 数据集 | 目录 | 状态 | 论文用途 |
| --- | --- | --- | --- |
| DIOR-R official | `experiments/dior_official/` | baseline、A、B、A+B、YOLOv8n、YOLO26n 已完成 | 第一数据集主实验 |
| HRSID-derived OBB | `experiments/hrsid/` | baseline、A、B、A+B 的三 seed 结果已完成 | 第二数据集主实验 |

### 单次最佳消融结果

| Dataset | Variant | Params (M) | GFLOPs | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
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
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DIOR-R | Baseline | 3 | 71.02 ± 0.10 | 54.19 ± 0.12 | 27.17 ± 0.16 | 17.79 ± 0.17 |
| DIOR-R | Baseline + A | 3 | 71.47 ± 0.13 | 53.83 ± 0.12 | 28.27 ± 0.16 | 19.61 ± 0.19 |
| DIOR-R | Baseline + B | 3 | 71.03 ± 0.08 | 54.15 ± 0.09 | 27.55 ± 0.13 | 18.10 ± 0.14 |
| DIOR-R | Baseline + A + B | 3 | **72.12 ± 0.14** | **54.43 ± 0.12** | **29.01 ± 0.19** | **20.24 ± 0.18** |
| HRSID | Baseline | 3 | 74.96 ± 0.18 | 39.42 ± 0.21 | 71.37 ± 0.23 | 37.13 ± 0.23 |
| HRSID | Baseline + A | 3 | 93.57 ± 0.15 | 66.88 ± 0.18 | 91.62 ± 0.17 | 65.91 ± 0.19 |
| HRSID | Baseline + B | 3 | 76.02 ± 0.18 | 41.71 ± 0.20 | 72.51 ± 0.22 | 38.66 ± 0.23 |
| HRSID | Baseline + A + B | 3 | **93.88 ± 0.09** | **67.48 ± 0.17** | **91.99 ± 0.13** | **66.70 ± 0.18** |

## DIOR-R 同协议模型对比

| Model | Params | GFLOPs | mAP50 | mAP50:95 |
| --- | ---: | ---: | ---: | ---: |
| YOLOv8n-OBB | 3.081M | 8.4 | 70.38 | 53.39 |
| YOLO11n-OBB | 2.658M | 6.6 | 71.11 | 54.31 |
| YOLO26n-OBB | 2.450M | 5.5 | 69.79 | 54.35 |
| FSPC-OBB | 2.740M | 10.7 | **72.25** | **54.55** |

详细记录位于 `experiments/dior_official/comparisons/`。

## 历史与筛选实验

| 目录 | 当前定位 |
| --- | --- |
| `experiments/dior/` | 早期 DIOR-R 8:1:1 划分、A/B/C/AB/ABC 探索。A+B 在该划分仍为最佳，可作为鲁棒性附加说明，但不能与官方划分主表混用。 |
| `experiments/ucas_aod/` | 第二数据集筛选。数据较轻，但 A 和 AB 未稳定超过 baseline。 |
| `experiments/vedai/` | 第二数据集筛选。B 有一定正向，A/AB 未形成主论文所需互补趋势。 |
| `experiments/ssdd_rbox/` | 第二数据集筛选。不同 seed 下排序不稳定，未进入主表。 |
| `experiments/hrsc2016/` | 快速筛选。AB 低于 baseline，停止扩展。 |

## 复现原则

- 同一数据集内的 baseline、A、B、A+B 必须共享 split、epochs、batch、imgsz、seed 集合、初始化、增强、NMS 和评估设置。
- `best.pt` 只由 validation fitness 选择，test split 只做最终评估。
- 不允许跨 seed 拼接单行结果。
- 旧实验配置保留是为了可追溯，不代表论文当前主线。
