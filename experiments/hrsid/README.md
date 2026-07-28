# HRSID-derived OBB 主实验

本目录是 IPPR 2026 小论文的第二个主数据集实验。当前结果以 [paper/ippr2026/main.pdf](../../paper/ippr2026/main.pdf) 为准。

## 数据集协议

- 原始来源：HRSID 官方 JPG 数据与实例 mask 标注。
- 本地原始目录：`C:/E/datasets/HRSID/HRSID_JPG/`。
- YOLO-OBB 输出：`C:/E/datasets/HRSID-YOLO/`。
- 服务器目录：`/home/ws/datasets/HRSID-YOLO/`。
- OBB 构造：由实例 mask 生成 minimum-area rotated rectangle。
- 划分：从官方 train 中分出 validation，保留官方 1,962 张 test。
- train/val/test：`3278/364/1962`。
- 实例数：train/val/test = `9974/1064/5918`。
- test 中小目标：`5350/5918`，约 90.4%。
- 训练：100 epochs，`imgsz=640`，batch 8，disk cache，3 seeds。
- 小目标口径：`wh < 1024 px^2`，仅用于诊断分析。

转换脚本为 `scripts/convert_hrsid_to_yolo_obb.py`，数据配置为 `ultralytics/cfg/datasets/HRSID.yaml`。

## 主消融结果

精度为百分数。论文 Table IV 报告每个 variant 的最佳单次结果，Table V 报告三 seed 均值和标准差。

| Variant | Params (M) | GFLOPs | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 2.654 | 6.6 | 75.13 | 39.63 | 71.60 | 37.36 |
| Baseline + A | 2.696 | 10.5 | 93.71 | 67.06 | 91.78 | 66.10 |
| Baseline + B | 2.696 | 6.8 | 76.20 | 41.91 | 72.73 | 38.88 |
| Baseline + A + B | 2.738 | 10.7 | **93.96** | **67.65** | **92.12** | **66.87** |

| Variant | Seeds | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | 3 | 74.96 ± 0.18 | 39.42 ± 0.21 | 71.37 ± 0.23 | 37.13 ± 0.23 |
| Baseline + A | 3 | 93.57 ± 0.15 | 66.88 ± 0.18 | 91.62 ± 0.17 | 65.91 ± 0.19 |
| Baseline + B | 3 | 76.02 ± 0.18 | 41.71 ± 0.20 | 72.51 ± 0.22 | 38.66 ± 0.23 |
| Baseline + A + B | 3 | **93.88 ± 0.09** | **67.48 ± 0.17** | **91.99 ± 0.13** | **66.70 ± 0.18** |

## 解释边界

- HRSID-derived OBB 不是原生人工旋转框，而是由 mask 转换得到；论文中必须保留这一说明。
- HRSID 小目标比例高、类别单一，能很好检验 FSPB 的高分辨率收益，但不能单独代表所有遥感 OBB 场景。
- 当前主结论依赖 DIOR-R official 与 HRSID-derived OBB 两个协议共同支持。
