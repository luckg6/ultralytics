# 第四章实验入口

更新日期：2026-08-12

第四章与第三章是并列互补路线，不定位为解决第三章计算量上升，也不要求与第三章 A+B 做同容量下的绝对排名。第四章首先完成自身受控消融：

```text
LSKNet-T baseline
LSKNet-T + C
LSKNet-T + D
LSKNet-T + C + D
```

LSKNet-T backbone 和必要通道适配属于基础架构选择，不算创新；最终 C、D 必须相对该 baseline 分别有效，组合模型还应优于两个单模块。当前研究目标是组合 All mAP50 相对 baseline 提升约 1 个百分点，并在主要全尺度与小目标指标上形成稳定互补。

## 基础结构与协议

```text
LSKNet-T Backbone
+ necessary channel adapters
+ original YOLO11 Neck
+ original YOLO11 OBB Head
```

该结构不继承第三章 FSPB、LPCF 或 P2 检测分支。LSKNet-T 使用官方 DOTA checkpoint 初始化，兼容的 Neck/Head 参数从 `yolo11n-obb.pt` 加载，新增层随机初始化。

| 环境 | 数据 | batch | device | cache | epochs |
|---|---|---:|---:|---|---:|
| 本地筛选 | `DIOR-official.yaml` | 4 | 0 | disk | 100 |
| `/home/ws` 第四章 | `DIOR-official-homews.yaml` | 16 | 1 | RAM | 100 |

初始化与 baseline 入口：

```bash
python scripts/prepare_lsknet_yolo_init.py --model ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-baseline.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_baseline_dior_official_homews.yaml
```

## Baseline 结果

DIOR-R official seed 42 test：

| Model | Params (M) | GFLOPs | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---:|---:|---:|---:|---:|---:|
| Chapter 3 A+B | 2.740 | 10.7 | 72.25 | 54.55 | 29.20 | 20.42 |
| LSKNet-T baseline | 5.728 | 18.7 | 73.72 | 56.88 | 27.69 | 18.15 |

这里只能确认混合结构接入成功、能够稳定收敛且具有全尺度检测潜力。模型容量差异明显，不能据此声称 LSKNet-T backbone 公平优于第三章方法或原生 backbone。

三 seed baseline 均值见 `dior_official_multiseed_summary_2026-08-07.md`：All mAP50 / mAP50:95 为 `73.61 / 56.77`，Small mAP50 / mAP50:95 为 `28.25 / 18.47`。

## 已完成筛选

### OAC、FDF 与 OAC+FDF

OAC 是方向感知校准候选，FDF 是频率细节融合候选。三 seed 平均结果如下：

| Variant | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---:|---:|---:|---:|
| Baseline | 73.61 | 56.77 | 28.25 | 18.47 |
| FDF | 73.63 | 56.84 | 29.22 | 19.17 |
| OAC | **73.85** | 56.82 | 29.25 | 19.28 |
| OAC+FDF | 73.68 | **56.90** | **29.54** | **19.51** |

OAC+FDF 的小目标和 All mAP50:95 均值有提升，但 All mAP50 仅比 baseline 高 `0.07`，且组合不稳定优于单模块。它是有效的历史筛选结果，不是第四章定稿 C/D。原始记录：

- `eval_lsknet_t_oac_dior_official_test_2026-07-29.md`
- `eval_lsknet_t_fdf_dior_official_test_2026-07-29.md`
- `eval_lsknet_t_oac_fdf_dior_official_test_2026-08-03.md`
- `dior_official_multiseed_summary_2026-08-07.md`

### OAC+FDF-Blend

Blend 版保留原 top-down 主路径并以零初始化残差混合 FDF，目的是降低组合的 seed 波动。三 seed 结果仍未满足“组合优于 baseline 与任一单模块”的要求，因此停止扩展。数据保留在 `dior_official_multiseed_blend_eval_2026-08-07.md` 和同名 CSV 中。

### FDConv-Lite 与 FDConv-Lite+FDF

FDConv-Lite 是第二轮 C 候选，FDF 继续作为 D 候选参与组合。seed 42 结果如下：

| Variant | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---:|---:|---:|---:|
| Baseline | 73.68 | 56.87 | 27.69 | 18.14 |
| FDF | 73.60 | **56.92** | **29.31** | **19.47** |
| FDConv-Lite | 73.41 | 56.80 | 28.94 | 19.05 |
| FDConv-Lite+FDF | 73.28 | 56.53 | 28.77 | 18.92 |

模型规模：FDConv-Lite 为 `5.832M / 19.2 GFLOPs`，FDConv-Lite+FDF 为 `5.862M / 19.2 GFLOPs`。初始化报告分别为 `lsknet_t_fdconv_init_report.md` 和 `lsknet_t_fdconv_fdf_init_report.md`。

结论：FDConv-Lite 单独能提升小目标指标，但全尺度指标略降；FDConv-Lite+FDF 在四项指标上均低于单 FDF，也低于单 FDConv-Lite。因此该方向保留为筛选记录，不继续扩展三 seed。

复核训练命令：

```bash
cd /home/ws/ultralytics && source .venv/bin/activate && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdconv_dior_official_homews.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdconv_fdf_dior_official_homews.yaml
```

训练后持久化评估：

```bash
python scripts/evaluate_experiment_suite.py --suite experiments/chapter4/eval_fdconv_screen_homews.yaml
```

评估清单会同时记录 Baseline、FDF、FDConv-Lite 和 FDConv-Lite+FDF。以后新增 C/D 候选时，优先复制并修改 `eval_fdconv_screen_homews.yaml`，不要再新增写死组合名称的专用评估脚本。

下一轮 C/D 候选仍先跑 DIOR-R seed 42 筛选。只有单模块和组合达到预期趋势后，才补齐三个 seed、第二数据集及正式四组消融配置。

### SGC 与 SGC+FDF

SGC 是第三轮 C 候选，来源于 Strip R-CNN 的 large strip convolution 思想。当前只迁移条带几何校准，不整体替换 LSKNet-T backbone，也不引入两阶段 ROI head。

实现落点：

```text
LSKNet-T C3/C4/C5 output
-> 1x1 channel adapter
-> StripGuidedCalibration on P3/P4/P5
-> original YOLO11 Neck or FDF-enhanced top-down neck
-> original YOLO11 OBB Head
```

初始化报告：

- `lsknet_t_sgc_init_report.md`：`5.835M / 19.2 GFLOPs`，LSK backbone `478/478`，YOLO neck/head `304/355`。
- `lsknet_t_sgc_fdf_init_report.md`：`5.864M / 19.2 GFLOPs`，LSK backbone `478/478`，YOLO neck/head `304/355`。

seed 42 筛选结果：

| Variant | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---:|---:|---:|---:|
| Baseline | 73.68 | 56.87 | 27.69 | 18.14 |
| FDF | 73.60 | 56.92 | 29.31 | 19.47 |
| SGC | **73.92** | **57.35** | **29.62** | **19.79** |
| SGC+FDF | 73.38 | 56.68 | 28.81 | 18.91 |

结论：SGC 是目前最强的单 C 候选，四项指标均超过 baseline 和单 FDF；但直接 `SGC+FDF` 组合四项均低于两个单模块，说明当前条带几何校准和 FDF top-down 频率门控存在负交互。保留 SGC，暂不扩展这版直接组合到三 seed。

复核训练命令：

```bash
cd /home/ws/ultralytics && source .venv/bin/activate && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_sgc_dior_official_homews.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_sgc_fdf_dior_official_homews.yaml
```

训练后持久化评估：

```bash
python scripts/evaluate_experiment_suite.py --suite experiments/chapter4/eval_sgc_screen_homews.yaml
```

下一步优先围绕 SGC 设计新的 D 或更温和的 SGC+D 组合方式，而不是继续运行当前 `SGC+FDF` 三 seed。

### FDR-Lite 与 SGC+FDR-Lite

FDR-Lite 是新的 D 候选，用于替代直接插入 top-down neck 的 FDF。它不改变原始 YOLO11 neck 主路径，只在 P3/P4/P5 adapter 特征上加入零初始化的频率细节残差。组合模型保留 SGC 的条带几何校准，再追加 FDR-Lite 的弱残差细节补偿，目标是避免 `SGC+FDF` 的负交互。

模型规模：

- `lsknet_t_fdr_lite_init_report.md`：`5.824M / 19.1 GFLOPs`，LSK backbone `478/478`，YOLO neck/head `304/355`。
- `lsknet_t_sgc_fdr_lite_init_report.md`：`5.895M / 19.4 GFLOPs`，LSK backbone `478/478`，YOLO neck/head `304/355`。

当前应优先运行 seed 42 筛选：

```bash
cd /home/ws/ultralytics && source .venv/bin/activate && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdr_lite_dior_official_homews.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_sgc_fdr_lite_dior_official_homews.yaml
```

训练后持久化评估：

```bash
python scripts/evaluate_experiment_suite.py --suite experiments/chapter4/eval_sgc_fdr_lite_screen_homews.yaml
```

## 设计与报告边界

- C、D 不得简单重复 LSKNet 的大核选择机制，也不复制第三章 FSPB/LPCF。
- 同一数据集内四组实验共享 split、epochs、batch、seed、初始化、增强、NMS 和评估协议。
- 最终至少报告 Params、GFLOPs、FPS、延迟、显存和全尺度/小目标 mAP。
- 小目标口径为 `wh < 1024 px^2`，属于项目诊断指标，不等同于 COCO `AP_S`。
- 跨章节比较只说明“轻量小目标增强”和“容量更高的精度优先路线”的权衡，不写成公平绝对排名。

服务器完整命令索引见 `dior_official_multiseed_homews_commands.md`，候选来源与迁移依据见 `../../research/top_conference/chapter4_2024plus_candidates.md`。
