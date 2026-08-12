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

## 当前筛选路线

当前仅把以下名称视为待验证候选，不能在论文中提前称为最终 C/D：

- `C-v2 = FDConv-Lite`：在 LSKNet-T 的 P3/P4/P5 通道适配后加入频域动态 adapter。
- `D = FDF`：保留第一轮中对小目标有效的 top-down 频率细节融合。
- `C+D = FDConv-Lite + FDF`。

模型规模：FDConv-Lite 为 `5.832M / 19.2 GFLOPs`，FDConv-Lite+FDF 为 `5.862M / 19.2 GFLOPs`。初始化报告分别为 `lsknet_t_fdconv_init_report.md` 和 `lsknet_t_fdconv_fdf_init_report.md`。

先运行 seed 42 筛选：

```bash
cd /home/ws/ultralytics && source .venv/bin/activate && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdconv_dior_official_homews.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdconv_fdf_dior_official_homews.yaml
```

训练后持久化评估：

```bash
python scripts/evaluate_chapter4_multiseed.py --combo fdconv_fdf --data ultralytics/cfg/datasets/DIOR-official-homews.yaml --split test --imgsz 640 --device 1 --workers 8
```

只有 seed 42 同时支持单 C 和 C+D，且组合达到预期趋势后，才补齐三个 seed、第二数据集及正式四组消融配置。

## 设计与报告边界

- C、D 不得简单重复 LSKNet 的大核选择机制，也不复制第三章 FSPB/LPCF。
- 同一数据集内四组实验共享 split、epochs、batch、seed、初始化、增强、NMS 和评估协议。
- 最终至少报告 Params、GFLOPs、FPS、延迟、显存和全尺度/小目标 mAP。
- 小目标口径为 `wh < 1024 px^2`，属于项目诊断指标，不等同于 COCO `AP_S`。
- 跨章节比较只说明“轻量小目标增强”和“容量更高的精度优先路线”的权衡，不写成公平绝对排名。

服务器完整命令索引见 `dior_official_multiseed_homews_commands.md`，候选来源与迁移依据见 `../../research/top_conference/chapter4_2024plus_candidates.md`。
