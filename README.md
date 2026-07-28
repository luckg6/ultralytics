# FSPC-OBB 遥感小目标旋转框检测仓库

本仓库服务 IPPR 2026 / EI 小论文和后续学位论文实验。当前论文主线已经收敛为 **FSPC-OBB: Fine-Scale Preservation and Poly-Kernel Context Fusion for Small Oriented Object Detection in Remote Sensing Images**。

最终论文结果以 [paper/ippr2026/main.pdf](paper/ippr2026/main.pdf) 和 [paper/ippr2026/main.tex](paper/ippr2026/main.tex) 为准；训练与评估原始记录保留在 `weights/experiments/` 和各数据集实验目录中。

## 当前方法

论文中使用两个独立改进点：

| 论文符号 | 正式名称 | 内部实验名 | 改动位置 |
| --- | --- | --- | --- |
| A | FSPB, Fine-Scale Preservation Branch | A-P2 | 新增 stride-4 / P2 预测分支，并回流到底向上 PAN |
| B | LPCF, Lightweight Poly-Kernel Context Fusion | B-PKI-Lite | 仅替换原 top-down P5->P4、P4->P3 两个融合阶段 |
| A+B | FSPC-OBB | AB-P2-PKI-Lite | 四尺度 OBB head + 选择性多核上下文融合 |

当前小论文不再采用 C 系列作为主方法。C-Dynamic、C-GRA、C-Chol、C-SET-HBS 等保留为探索记录，不进入最终主消融表。

## 硕士论文衔接

当前小论文结果可作为硕士论文第三章主体内容。第四章方案入口为 [thesis_chapter3_chapter4_consensus_for_codex.md](thesis_chapter3_chapter4_consensus_for_codex.md)：当前共识是先构建 `LSKNet-T Backbone + 必要通道适配层 + YOLO11 Neck + YOLO11 OBB Head` 的新 baseline，不继承第三章 FSPB/LPCF，再基于该 baseline 设计 C、D 两个不同于 FSPB/LPCF 的创新模块。LSKNet-T 源码和 checkpoint 当前尚未放入本仓库，后续实现前需要先补齐外部材料。

## 论文主实验

### 数据集与协议

| 数据集 | train/val/test | 有效图像 | 类别 | epochs | batch | imgsz | seeds | cache |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DIOR-R official | 5862/5863/11738 | 5800/5833/11690 | 20 | 100 | 32 | 640 | 3 | RAM |
| HRSID-derived OBB | 3278/364/1962 | 3278/364/1962 | 1 | 100 | 8 | 640 | 3 | disk |

小目标分析采用本项目诊断口径：在 640 输入尺度下，旋转框面积满足 `wh < 1024 px^2` 的标注和预测会先被独立筛选，再进行 rotated-IoU 匹配。该指标用于分析小目标趋势，不等同于 COCO 官方 `AP_S`。

### 单次最佳消融结果

精度为百分数，参数量和 GFLOPs 使用统一评估摘要口径。

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

## 目录索引

| 路径 | 用途 |
| --- | --- |
| `paper/ippr2026/` | 小论文 LaTeX 源码、图、bib、PDF |
| `paper/ippr2026_latex_submission/` | 已整理的 LaTeX 投稿包源目录 |
| `experiments/dior_official/` | DIOR-R 官方划分主实验和同协议 YOLOv8/YOLO26 对比 |
| `experiments/hrsid/` | HRSID-derived OBB 第二数据集主实验 |
| `experiments/dior/` | 早期 8:1:1 DIOR-R 与 C 系列探索配置 |
| `experiments/ucas_aod/`、`experiments/vedai/`、`experiments/ssdd_rbox/`、`experiments/hrsc2016/` | 第二数据集筛选记录 |
| `weights/experiments/` | 原始评估 md 和轻量结果记录；权重文件本身已被 git 忽略 |
| `research/top_conference/` | PKINet、LSKNet、SET 等参考材料记录 |
| `paper/archive/md_cleanup_20260728/` | 本次整理前的旧 md 备份和草稿建议归档 |

## 训练与评估入口

统一训练入口：

```bash
python scripts/train_obb.py --config <experiment.yaml>
```

统一评估入口：

```bash
python scripts/evaluate_obb.py --model <best.pt> --data <dataset.yaml> --split test --mode both --imgsz 640
```

复现实验时要保证同一数据集内 baseline、A、B、A+B 使用相同数据划分、训练轮数、batch、seed 集合、初始化权重、NMS 和评估配置；不得跨 seed 或跨数据集拼接单行结果。

## 文档状态

核心结论已经合并到本文件、[AGENTS.md](AGENTS.md)、[experiments/README.md](experiments/README.md)、[experiments/dior_official/README.md](experiments/dior_official/README.md)、[experiments/hrsid/README.md](experiments/hrsid/README.md) 和 [research/datasets/SECOND_DATASET_SELECTION.md](research/datasets/SECOND_DATASET_SELECTION.md)。旧的大段过程性说明保留在 archive 或对应历史实验目录中，后续写论文时优先读 `paper/ippr2026/main.pdf`。
