# DIOR-R 官方划分主实验

本目录是 IPPR 2026 小论文的第一个主数据集实验。当前结果以 [paper/ippr2026/main.pdf](../../paper/ippr2026/main.pdf) 为准。

## 数据集协议

- 原始数据：DIOR-R，23,463 张图，20 类。
- 本地目录：`C:/E/datasets/YOLODIOR-R-official/`。
- 服务器目录：`/home/ws/datasets/YOLODIOR-R-official/`。
- 划分：按官方 image order 使用 `00001-05862` train、`05863-11725` val、`11726-23463` test。
- 原始数量：train/val/test = `5862/5863/11738`。
- 有效数量：train/val/test = `5800/5833/11690`。第三方 Ultralytics 格式转换中有 140 张图片存在越界标注并被整图忽略，四组实验使用同一过滤规则。
- 训练：100 epochs，`imgsz=640`，batch 32，RAM cache，3 seeds。
- 小目标口径：`wh < 1024 px^2`，仅用于诊断分析。

转换脚本为 `scripts/prepare_dior_r_official_split.py`。早期 Kaggle 8:1:1 划分保留在 `experiments/dior/`，不能与本目录结果混为同一协议。

## 主消融结果

精度为百分数。论文 Table IV 报告每个 variant 的最佳单次结果，Table V 报告三 seed 均值和标准差。

| Variant | Params (M) | GFLOPs | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 2.658 | 6.6 | 71.11 | 54.31 | 27.32 | 17.96 |
| Baseline + A | 2.698 | 10.5 | 71.60 | 53.94 | 28.43 | 19.80 |
| Baseline + B | 2.700 | 6.8 | 71.11 | 54.24 | 27.68 | 18.23 |
| Baseline + A + B | 2.740 | 10.7 | **72.25** | **54.55** | **29.20** | **20.42** |

| Variant | Seeds | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | 3 | 71.02 ± 0.10 | 54.19 ± 0.12 | 27.17 ± 0.16 | 17.79 ± 0.17 |
| Baseline + A | 3 | 71.47 ± 0.13 | 53.83 ± 0.12 | 28.27 ± 0.16 | 19.61 ± 0.19 |
| Baseline + B | 3 | 71.03 ± 0.08 | 54.15 ± 0.09 | 27.55 ± 0.13 | 18.10 ± 0.14 |
| Baseline + A + B | 3 | **72.12 ± 0.14** | **54.43 ± 0.12** | **29.01 ± 0.19** | **20.24 ± 0.18** |

## 同协议参照模型

| Model | Params | GFLOPs | mAP50 | mAP50:95 |
| --- | ---: | ---: | ---: | ---: |
| YOLOv8n-OBB | 3.081M | 8.4 | 70.38 | 53.39 |
| YOLO11n-OBB | 2.658M | 6.6 | 71.11 | 54.31 |
| YOLO26n-OBB | 2.450M | 5.5 | 69.79 | 54.35 |
| FSPC-OBB | 2.740M | 10.7 | **72.25** | **54.55** |

详细记录见 `comparisons/README.md` 和 `comparisons/eval_yolov8n_yolo26n_test_2026-07-21.md`。

## 目录说明

- 本目录保留训练 YAML 和评估说明。
- 第四章 `/home/ws` 新增筛选实验统一使用 `device=1`、`batch=16`、`cache=ram`；复现本章第三章论文表格时仍必须按上面的固定 batch 与三 seed 协议。
- 旧 `experiments/dior/` 的 8:1:1 结果只可作为 alternate split robustness，不可直接横向比较。
