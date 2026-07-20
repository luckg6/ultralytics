# VEDAI-1024 轻量筛选实验

## 原版 A/B/AB 的 imgsz=512 统一复核

为保持与 DIOR-R 完全相同的模型结构，同时不重跑已经完成的 DIOR-R 实验，VEDAI 新增一组统一 `imgsz=512` 的四行复核。四组分别使用原版 baseline、A-P2、B-PKI-Lite 和 A+B-PKI-Lite YAML；它们都从 `weights/pretrained/yolo11n-obb.pt` 独立起训，除模型结构外训练设置完全一致。已有 `imgsz=640` 结果和探索版 A-Plus/AB-Plus 全部保留，不覆盖。

`/home/ws` 服务器训练统一使用 `batch=32`、`device=1`、`cache=ram`：

```bash
python scripts/train_obb.py --config experiments/vedai/baseline_homews_batch32_img512.yaml
python scripts/train_obb.py --config experiments/vedai/a_p2_homews_batch32_img512.yaml
python scripts/train_obb.py --config experiments/vedai/b_pki_lite_homews_batch32_img512.yaml
python scripts/train_obb.py --config experiments/vedai/ab_p2_pki_lite_homews_batch32_img512.yaml
```

训练完成后统一评估 fold10 test：

```bash
python scripts/evaluate_obb.py --model runs/obb/vedai_f10_512_baseline_yolo11n_obb/weights/best.pt --data VEDAI-1024-homews.yaml --split test --mode both --imgsz 512
python scripts/evaluate_obb.py --model runs/obb/vedai_f10_512_A_p2/weights/best.pt --data VEDAI-1024-homews.yaml --split test --mode both --imgsz 512
python scripts/evaluate_obb.py --model runs/obb/vedai_f10_512_B_pki_lite/weights/best.pt --data VEDAI-1024-homews.yaml --split test --mode both --imgsz 512
python scripts/evaluate_obb.py --model runs/obb/vedai_f10_512_AB_p2_pki_lite/weights/best.pt --data VEDAI-1024-homews.yaml --split test --mode both --imgsz 512
```

本地备用配置为 `baseline_img512.yaml`、`a_p2_img512.yaml`、`b_pki_lite_img512.yaml` 和 `ab_p2_pki_lite_img512.yaml`，统一 `batch=4`、`device=0`、`cache=disk`。该复核是公平的输入尺度假设验证，不预设 A 或 AB 必然提升；论文只按最终实测结果报告。小目标评估仍按模型输入空间 `w*h<1024` 判定，因此 512 四组之间可以公平横向比较，但不要把其小目标数量口径与 640 实验直接混合比较。

四组已完成训练和 fold10 test 重评，`small` 模式保留 358 个 OBB：

| 模型 | 最佳 val epoch | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|---:|
| baseline | 43 | 0.6720 | **0.4643** | 0.6351 | **0.4268** |
| A-P2 | 73 | 0.5695 | 0.4240 | 0.5161 | 0.3730 |
| B-PKI-Lite | 56 | **0.6756** | 0.4541 | **0.6362** | 0.4156 |
| A+B-PKI-Lite | 67 | 0.5736 | 0.4140 | 0.5314 | 0.3685 |

相对同为 `imgsz=512` 的 baseline，A 四项变化为 `-0.1025/-0.0403/-0.1190/-0.0538`，B 为 `+0.0036/-0.0102/+0.0011/-0.0112`，AB 为 `-0.0984/-0.0503/-0.1037/-0.0583`。B 只有两个 mAP50 指标极小幅上升，而两个 mAP50-95 均下降；A 和 AB 四项明显负向。因此降低输入分辨率没有解决原版 P2 分支在 VEDAI 上的问题，该组只作为失败复核保留，不进入论文主消融表，也不再围绕 512 继续调参。

VEDAI-1024 用于筛选 A-P2、B-PKI-Lite 和 A+B-PKI-Lite 在真实微小、多方向车辆场景中的跨数据集效果。

## 数据转换

官方原始数据目录：`C:/E/datasets/VEDAI-1024/`。

```bash
python scripts/convert_vedai_to_yolo_obb.py
```

转换输出：`C:/E/datasets/VEDAI-1024-YOLO/`。脚本只使用彩色 `_co.png`，不混入同场景红外图。

固定筛选划分使用官方 fold10 test、fold02 val，其余八个 fold train。fold10 的九类直方图最接近全数据的 1/10，尤其包含 5 个 plane，接近理论期望 4.8；fold02 是下一份接近总体分布的 fold。该规则在模型训练前根据标签分布确定，不根据任何模型结果挑选。

类别采用官方 DevKit 的九类：car、truck、tractor、camping car、van、other、pickup、boat、plane。原始类别 7 和 8 只有极少实例且不属于官方九类评估，转换报告会记录并忽略。

本地数据配置：`ultralytics/cfg/datasets/VEDAI-1024.yaml`。

`/home/ws` 数据配置：`ultralytics/cfg/datasets/VEDAI-1024-homews.yaml`，服务器数据目录为 `/home/ws/datasets/VEDAI-1024-YOLO/`。

## 数据统计

| split | 官方 fold | 图像 | OBB | `imgsz=640` 小目标 |
|---|---|---:|---:|---:|
| train | 01、03-09 | 968 | 2950 | 2835 |
| val | 02 | 121 | 368 | 362 |
| test | 10 | 121 | 369 | 353 |

Ultralytics 原生 `YOLODataset(task='obb')` 已完整扫描，0 损坏标签。完整转换统计位于 `C:/E/datasets/VEDAI-1024-YOLO/conversion_report.json`。

## 主消融公平性硬规则

VEDAI 服务于 DIOR-R + VEDAI 两数据集的 baseline/A/B/AB 主消融。主表候选必须同时满足：

- baseline、A、B、AB 全部从 `weights/pretrained/yolo11n-obb.pt` 独立起训。
- 同一数据集内统一 split、epochs、batch、imgsz、seed、数据增强、优化器和评估协议。
- AB 只能通过结构同时包含 A 和 B，不能从 A/B 数据集微调权重续训，不能冻结 A 后只训 B，不能多一个训练阶段或享有独有训练资源。
- 不允许为了让 AB 超过单点而只改 AB 的 seed、batch、训练轮数或评估设置。
- 主结论只能来自同一公平协议下的结构消融。负向串联、解耦和 Heavy 结果保留为探索记录，不写成主方法增益。

当前 `experiments/vedai/*.yaml` 已检查，所有现有配置的 `pretrained` 均为 `weights/pretrained/yolo11n-obb.pt`，不存在从 A/B `best.pt` 续训的配置。

## `/home/ws` 固定 batch=32 筛选

四组严格使用相同 `batch=32`、`seed=42`、1 号 GPU 和 RAM cache：

```bash
python scripts/train_obb.py --config experiments/vedai/baseline_homews_batch32.yaml
python scripts/train_obb.py --config experiments/vedai/a_p2_homews_batch32.yaml
python scripts/train_obb.py --config experiments/vedai/b_pki_lite_homews_batch32.yaml
python scripts/train_obb.py --config experiments/vedai/ab_p2_pki_lite_homews_batch32.yaml
```

训练后统一评估 fold10 test：

```bash
python scripts/evaluate_obb.py --model runs/obb/vedai_f10_baseline_yolo11n_obb/weights/best.pt --data VEDAI-1024-homews.yaml --split test --mode both
python scripts/evaluate_obb.py --model runs/obb/vedai_f10_A_p2/weights/best.pt --data VEDAI-1024-homews.yaml --split test --mode both
python scripts/evaluate_obb.py --model runs/obb/vedai_f10_B_pki_lite/weights/best.pt --data VEDAI-1024-homews.yaml --split test --mode both
python scripts/evaluate_obb.py --model runs/obb/vedai_f10_AB_p2_pki_lite/weights/best.pt --data VEDAI-1024-homews.yaml --split test --mode both
```

若把权重拷回本机评估，将命令中的 `VEDAI-1024-homews.yaml` 换成 `VEDAI-1024.yaml`。

## fold10 筛选结果

四组固定 `batch=32` 实验已完成，以下数值均为 fold10 test 结果：

| 模型 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| baseline | 0.7300 | 0.5661 | 0.6831 | 0.5293 |
| A-P2 | 0.6526 | 0.4687 | 0.5978 | 0.4311 |
| B-PKI-Lite | **0.7482** | **0.5756** | **0.7014** | **0.5365** |
| A+B-PKI-Lite | 0.6782 | 0.4994 | 0.6320 | 0.4674 |

B-PKI-Lite 四项指标均高于 baseline；A-P2 和 AB 则明显低于 baseline。AB 虽然比 A 好，但不足以抵消 P2 在该数据集上引入的误检。详细评估和复杂度记录见 `weights/experiments/vedai/eval_vedai_fold10_test_2026-07-17.md`。

该结果是固定 fold10 单划分筛选，不是完整十折均值。由于它不支持 A/AB 的跨数据集增益，VEDAI 不建议作为当前 AB 主方法的第二数据集主结果。

## A-P2-Plus 实验

旧 A-P2 在 VEDAI 上的召回率与 baseline 接近，但精确率明显下降。A-P2-Plus 不改变 A 的核心定义，仍为新增 P2/4 检测分支，但对 P3→P2 融合进行三项加强：

- P2 融合输出的实际通道数由 32 增加到 48。
- P2 `C3k2` 的有效内部重复数由 1 增加到 2，隐藏扩展率提高到 0.75。
- 新增 `P2SemanticGuard`，用低频语义上下文生成通道和空间门控，允许抑制缺少语义支持的高分辨率背景响应。

该模块不使用 B-PKI-Lite 的多核 neck 结构，A 与 B 的实验边界保持独立。新模型与旧 A 也是独立 YAML，不会改变已有权重的行为。

| 构建口径 | Params | GFLOPs |
|---|---:|---:|
| baseline | 2,663,262 | 6.6 |
| 旧 A-P2 | 2,704,904 | 10.5 |
| A-P2-Plus | 2,803,925 | 13.8 |

A-P2-Plus 相对 baseline 增加 140,663 参数（约 `+5.28%`），相对旧 A 增加 99,021 参数（约 `+3.66%`）。

本地训练：

```bash
python scripts/train_obb.py --config experiments/vedai/a_p2_plus.yaml
```

`/home/ws` 固定 `batch=32`、1 号 GPU 训练：

```bash
python scripts/train_obb.py --config experiments/vedai/a_p2_plus_homews_batch32.yaml
```

训练完后评估：

```bash
python scripts/evaluate_obb.py --model runs/obb/vedai_f10_A_p2_plus/weights/best.pt --data VEDAI-1024-homews.yaml --split test --mode both
```

A-P2-Plus 已使用上述 `/home/ws` 固定 `batch=32` 配置训练完成：

| 模型 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| baseline | 0.7300 | **0.5661** | 0.6831 | 0.5293 |
| 旧 A-P2 | 0.6526 | 0.4687 | 0.5978 | 0.4311 |
| B-PKI-Lite | **0.7482** | **0.5756** | 0.7014 | 0.5365 |
| A-P2-Plus | 0.7310 | 0.5507 | **0.7054** | **0.5444** |

A-P2-Plus 小目标 mAP50/mAP50-95 相对 baseline 提升 `+0.0223/+0.0151`，相对旧 A 提升 `+0.1076/+0.1133`，小目标两项均是当前最佳。其全尺度 mAP50 略高于 baseline `+0.0010`，但 mAP50-95 仍低 `0.0154`。

守门模块已将全尺度 precision 从 baseline 的 0.657 提高到 0.777，同时 recall 从 0.679 降到 0.614，说明它成功抑制了旧 P2 的误检，但筛选略显保守。当前 B 的全尺度指标最好，A-P2-Plus 的小目标指标最好，因此下一步构建 AB-Plus 已有比较明确的互补依据。

权重已归档至 `weights/experiments/vedai/a_p2_plus/best.pt`，训练日志已整理至 `experiments/logs/vedai/a_p2_plus/`。

## AB-Plus 实验

AB-Plus 组合 A-P2-Plus 和 B-PKI-Lite，不覆盖旧 AB：

- A-Plus：第 19 层使用 `C3k2P2Guard`，负责加宽、加深 P2 分支和语义误检抑制。
- B-PKI-Lite：只在第 13、16 层使用 `C3k2PKI`，负责 P5→P4、P4→P3 的 top-down neck 上下文融合。
- OBB 仍为 P2/P3/P4/P5 四层输出，不改 loss、解码、NMS 和评估协议。

| 构建口径 | Params | GFLOPs | 相对 baseline Params |
|---|---:|---:|---:|
| baseline | 2,663,262 | 6.6 | - |
| A-P2-Plus | 2,803,925 | 13.8 | +5.28% |
| AB-Plus | 2,845,975 | 14.0 | +6.86% |

本地训练：

```bash
python scripts/train_obb.py --config experiments/vedai/ab_p2_plus_pki_lite.yaml
```

`/home/ws` 固定 `batch=32`、1 号 GPU、RAM cache：

```bash
python scripts/train_obb.py --config experiments/vedai/ab_p2_plus_pki_lite_homews_batch32.yaml
```

训练完成后评估：

```bash
python scripts/evaluate_obb.py --model runs/obb/vedai_f10_AB_p2_plus_pki_lite/weights/best.pt --data VEDAI-1024-homews.yaml --split test --mode both
```

基本验收线是四项指标都超过 baseline：`0.7300/0.5661/0.6831/0.5293`。理想目标是同时超过 B 的全尺度 `0.7482/0.5756` 和 A-P2-Plus 的小目标 `0.7054/0.5444`。

AB-Plus 已使用固定 `batch=32` 配置训练完成，未达到上述验收线：

| 模型 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| baseline | 0.7300 | 0.5661 | 0.6831 | 0.5293 |
| B-PKI-Lite | **0.7482** | **0.5756** | 0.7014 | 0.5365 |
| A-P2-Plus | 0.7310 | 0.5507 | **0.7054** | **0.5444** |
| AB-Plus | 0.6862 | 0.5263 | 0.6501 | 0.4955 |

AB-Plus 相对旧 AB 四项指标回升 `+0.0080/+0.0269/+0.0181/+0.0281`，但相对 baseline 仍分别下降 `-0.0438/-0.0398/-0.0330/-0.0338`。其全尺度 P/R 为 `0.625/0.666`，说明 B 恢复了 A-Plus 的一部分召回，但同时冲淡了语义守门的误检抑制。当前串联结构下 A-Plus 和 B 存在特征干扰，没有实现预期互补。

权重已归档至 `weights/experiments/vedai/ab_p2_plus_pki_lite/best.pt`，日志已整理至 `experiments/logs/vedai/ab_p2_plus_pki_lite/`。

## AB-Plus-Decoupled 实验

串联 AB-Plus 中 B 改变了送入 P2SemanticGuard 的 P3 特征，导致 A-Plus 的误检抑制失效。AB-Plus-Decoupled 改为双路 neck：

- A 主路的 0-28 层与已验证的 A-P2-Plus 完全一致，P2Guard 仍只接收普通 P3 融合特征。
- B 从 backbone P5 独立建立 P5→P4→P3 `C3k2PKI` 辅助路径，不再串入 A 的 P2 分支。
- B 只在最终 P3/P4 检测特征处通过 `ResidualFeatureBlend` 注入，P2 完全归 A 所有。
- 融合系数为逐通道可学习参数且初始为 0，因此训练起点严格等价于 A 主路；只有 B 对 loss 有利时才会逐步注入。

| 构建口径 | Params | GFLOPs | 相对 baseline Params |
|---|---:|---:|---:|
| baseline | 2,663,262 | 6.6 | - |
| A-P2-Plus | 2,803,925 | 13.8 | +5.28% |
| 串联 AB-Plus | 2,845,975 | 14.0 | +6.86% |
| AB-Plus-Decoupled | 2,989,559 | 14.8 | +12.25% |

本地训练：

```bash
python scripts/train_obb.py --config experiments/vedai/ab_p2_plus_pki_decoupled.yaml
```

`/home/ws` 固定 `batch=32`、1 号 GPU、RAM cache：

```bash
python scripts/train_obb.py --config experiments/vedai/ab_p2_plus_pki_decoupled_homews_batch32.yaml
```

训练完成后评估：

```bash
python scripts/evaluate_obb.py --model runs/obb/vedai_f10_AB_p2_plus_pki_decoupled/weights/best.pt --data VEDAI-1024-homews.yaml --split test --mode both
```

必须首先超过 baseline 四项 `0.7300/0.5661/0.6831/0.5293`。最终成功标准是超过 B 的全尺度 `0.7482/0.5756` 与 A-P2-Plus 的小目标 `0.7054/0.5444`。

解耦版已使用固定 `batch=32` 配置训练完成：

| 模型 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| baseline | 0.7300 | 0.5661 | 0.6831 | 0.5293 |
| B-PKI-Lite | **0.7482** | **0.5756** | 0.7014 | 0.5365 |
| A-P2-Plus | 0.7310 | 0.5507 | **0.7054** | **0.5444** |
| 串联 AB-Plus | 0.6862 | 0.5263 | 0.6501 | 0.4955 |
| AB-Plus-Decoupled | 0.7336 | 0.5487 | 0.6768 | 0.5222 |

解耦版相对串联版四项回升 `+0.0474/+0.0224/+0.0267/+0.0267`，且全尺度 mAP50 比 baseline 高 `0.0036`，证明解耦有效。但其余三项仍比 baseline 低 `0.0174/0.0063/0.0071`，因此还不能作为成功 AB 结果。

训练后两个融合门的平均幅度只有约 1.2%，但 P2Guard 抑制强度仍比单独 A-Plus 弱。该现象只用于指导后续公平的结构设计；不允许改用 A-P2-Plus `best.pt` 初始化、冻结主路或只训练 B 残差，因为这会破坏主消融公平性。

权重已归档至 `weights/experiments/vedai/ab_p2_plus_pki_decoupled/best.pt`，日志已整理至 `experiments/logs/vedai/ab_p2_plus_pki_decoupled/`。

## AB-PKI-Heavy 实验

AB-PKI-Heavy 不使用双路、残差门或阶段式初始化，仍从与其他消融相同的 `yolo11n-obb.pt` 独立起训。结构是单路径加宽加深：

- P2Guard 之前保持普通 P5→P4→P3 路径，B 不再改变 P2 输入。
- P2 实际通道从 A-Plus 的 48 提高到 64，有效重复保持 2。
- 最终 P3/P4 融合改为实际 96/160 通道的 `C3k2PKI`，有效重复数均为 2，隐藏扩展率为 0.75。
- P5 保持原尺度，OBB 仍输出 P2/P3/P4/P5，不改 loss、解码和 NMS。

| 构建口径 | Params | GFLOPs | 相对 baseline Params |
|---|---:|---:|---:|
| baseline | 2,663,262 | 6.6 | - |
| A-P2-Plus | 2,803,925 | 13.8 | +5.28% |
| AB-Plus-Decoupled | 2,989,559 | 14.8 | +12.25% |
| AB-PKI-Heavy | 3,580,431 | 20.2 | +34.44% |

尽管相对参数增幅较大，其绝对参数仍只有约 3.6M，且增量集中于小目标多尺度 neck，不是直接替换为更大 backbone。论文中应将其明确标为 Heavy 版本。

本地训练：

```bash
python scripts/train_obb.py --config experiments/vedai/ab_p2_plus_pki_heavy.yaml
```

`/home/ws` 固定 `batch=32`、1 号 GPU、RAM cache：

```bash
python scripts/train_obb.py --config experiments/vedai/ab_p2_plus_pki_heavy_homews_batch32.yaml
```

训练完成后评估：

```bash
python scripts/evaluate_obb.py --model runs/obb/vedai_f10_AB_p2_plus_pki_heavy/weights/best.pt --data VEDAI-1024-homews.yaml --split test --mode both
```

成功标准不变：全尺度超过 B 的 `0.7482/0.5756`，同时小目标超过 A-P2-Plus 的 `0.7054/0.5444`。

Heavy 版已使用固定 `batch=32` 配置训练完成，未达到成功标准：

| 模型 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| baseline | 0.7300 | 0.5661 | 0.6831 | 0.5293 |
| B-PKI-Lite | **0.7482** | **0.5756** | 0.7014 | 0.5365 |
| A-P2-Plus | 0.7310 | 0.5507 | **0.7054** | **0.5444** |
| AB-Plus-Decoupled | 0.7336 | 0.5487 | 0.6768 | 0.5222 |
| AB-PKI-Heavy | 0.7334 | 0.5431 | 0.6775 | 0.5208 |

Heavy 版相对 baseline 四项变化为 `+0.0034/-0.0230/-0.0056/-0.0085`；相对解耦版为 `-0.0002/-0.0056/+0.0007/-0.0014`。增加约 59 万参数没有产生精度收益。其全尺度 P/R 为 `0.640/0.704`，容量增加主要提高了召回，同时带来更多误检。

权重已归档至 `weights/experiments/vedai/ab_p2_plus_pki_heavy/best.pt`，日志已整理至 `experiments/logs/vedai/ab_p2_plus_pki_heavy/`。
