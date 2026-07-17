# VEDAI-1024 轻量筛选实验

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

## 待训练 A-P2-Plus

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

建议先验收 A-P2-Plus 能否超过 baseline 的 0.5661/0.5293（全尺度/小目标 mAP50-95），再构建对应 AB-Plus，避免在 A 单点仍负向时继续浪费训练资源。
