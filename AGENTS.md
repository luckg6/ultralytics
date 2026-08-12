# Codex / Claude 工作说明

本仓库当前服务遥感图像小目标 OBB 检测论文。后续代理接手时，请先读本文件，再读 [paper/ippr2026/main.pdf](paper/ippr2026/main.pdf) 或 [paper/ippr2026/main.tex](paper/ippr2026/main.tex)。

## 当前主线

- 论文方法名：**FSPC-OBB**。
- 标题：`FSPC-OBB: Fine-Scale Preservation and Poly-Kernel Context Fusion for Small Oriented Object Detection in Remote Sensing Images`。
- 参考基线：YOLO11n-OBB。
- A：**FSPB**, Fine-Scale Preservation Branch。内部旧名 A-P2，新增 stride-4 / P2 预测分支，并把 P2 回流到底向上 PAN。
- B：**LPCF**, Lightweight Poly-Kernel Context Fusion。内部旧名 B-PKI-Lite，只作用于原 top-down P5->P4、P4->P3 两个融合块。
- A+B：**FSPC-OBB**。这是当前小论文主方法。
- C-Dynamic、C-GRA、C-Chol、C-SET-HBS 等只作为历史探索记录，不进入当前主论文方法。

## 硕士论文章节边界

- 当前 IPPR 2026 / EI 小论文可理解为硕士论文第三章内容。
- 第三章维持 `YOLO11n-OBB + FSPB(A) + LPCF(B)`，不要再把 C 系列塞回第三章主线。
- 第四章方案入口是 [thesis_chapter3_chapter4_consensus_for_codex.md](thesis_chapter3_chapter4_consensus_for_codex.md)。
- 第三章和第四章是并列互补路线，不要写成严格模型递进关系，也不要把第四章定位为解决第三章计算量上升的问题。
- 第四章基础结构已确认：采用 `LSKNet-T Backbone + 必要通道适配层 + YOLO11 Neck + YOLO11 OBB Head`，不继承第三章 FSPB/LPCF。
- 更换 LSKNet-T Backbone 本身不算创新点；第四章创新点应由 C、D 构成。
- LSKNet-T baseline、结构适配和混合权重初始化已经完成。OAC、FDF、OAC+FDF 及 Blend 是已完成但未达到最终组合目标的筛选路线，不再作为当前定稿 C/D。
- 当前筛选路线为 `C-v2 = FDConv-Lite`、`D = FDF`，先运行 DIOR-R seed 42 的单 C 与 C+D；结果成立后再补三 seed 和第二数据集。尚无训练结果时不得把它们写成最终创新点。
- 第四章正式目标接受两数据集、四组消融、三随机种子。组合模型应在主要指标上优于 baseline 和两个单模块，并争取 All mAP50 相对 baseline 提升约 1 个百分点。
- 第四章首先与自己的 LSKNet-T baseline 做受控消融；跨章节结果只用于说明路线特点和复杂度-精度权衡，不用于不公平的绝对排名。

## 结果可信源

优先级从高到低：

1. [paper/ippr2026/main.pdf](paper/ippr2026/main.pdf) 和 [paper/ippr2026/main.tex](paper/ippr2026/main.tex)，用于第三章/小论文定稿结果。
2. [thesis_chapter3_chapter4_consensus_for_codex.md](thesis_chapter3_chapter4_consensus_for_codex.md)，用于硕士论文第三章与第四章衔接方案。
3. `weights/experiments/**/eval*.md` 原始评估记录。
4. `weights/checkpoints/` 中集中保存的 `best.pt`、`results.csv` 和 `args.yaml`。
5. 历史 README 或聊天记录。

如果 README 与 PDF 冲突，以 PDF 和原始评估记录为准；修正文档，不要为了叙事改实验结果。

## 论文主实验协议

| 数据集 | train/val/test | 有效图像 | 类别 | epochs | batch | imgsz | seeds | cache |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DIOR-R official | 5862/5863/11738 | 5800/5833/11690 | 20 | 100 | 32 | 640 | 3 | RAM |
| HRSID-derived OBB | 3278/364/1962 | 3278/364/1962 | 1 | 100 | 8 | 640 | 3 | disk |

论文表格中精度均按百分数报告。小目标口径为 `wh < 1024 px^2`，这是本项目诊断指标，不要写成 COCO 官方 `AP_S`。

## 当前主结果

### 单次最佳消融

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

## 数据集和目录边界

- `experiments/dior_official/` 是 DIOR-R 官方划分主实验；不要和旧 `experiments/dior/` 的 8:1:1 结果混用。
- `experiments/hrsid/` 是第二数据集主实验。
- `experiments/dior/` 保留早期 8:1:1、C 系列和组合探索。
- `experiments/ucas_aod/`、`experiments/vedai/`、`experiments/ssdd_rbox/`、`experiments/hrsc2016/` 是第二数据集筛选记录；不进入当前主表。
- `paper/archive/md_cleanup_20260728/` 保存本次整理前的旧 md 和草稿建议文件。

## 服务器约定

- `/home/ws` 是长期服务器根目录，数据集放 `/home/ws/datasets/<dataset-name>/`。
- 第四章新增 `/home/ws` 实验统一使用 `device=1`、`batch=16`、`cache=ram`；历史配置中的 `batch=-1` 只用于还原当时实验。
- 复现当前论文已定稿实验时，按论文协议固定：DIOR-R `batch=32, cache=RAM`；HRSID `batch=8, cache=disk`。
- AutoDL 一次性多卡续训记录只用于历史追踪，不作为未来默认服务器配置。

## 文档维护规则

- 核心索引只保留当前结论；失败实验写成筛选记录，不再堆到根 README。
- 原始评估 md 不合并、不改写，除非发现路径或指标抄录错误。
- 不跨 seed、跨数据集或跨划分拼接结果。
- 普通训练输出权重仍应被 git 忽略；但 `weights/pretrained/` 中用于服务器复现的预训练和初始化权重允许随远程同步。
- 训练完成后只把仍服务论文或当前实验对照的 `best.pt` 归档到 `weights/checkpoints/`；不要长期保留 `last.pt`、临时 `val*` 或失败筛选权重。
