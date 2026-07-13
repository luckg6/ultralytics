# 实验配置登记

这个目录用于登记 EI 会议论文和毕业学位论文的训练实验配置。它不是 Ultralytics 官方配置目录，而是本课题的实验台账。

## 原则

- 每个数据集单独一个子目录。
- 每个实验变体单独一个 YAML。
- YAML 记录模型结构、预训练权重、数据集、训练超参、run name 和当前状态。
- `status: planned` 表示只登记计划，还没有可运行结构。
- `status: ready` 表示可以直接用统一训练脚本运行。

## 当前 DIOR-R 统一超参

后续 baseline/A/B/C/AB/ABC 主实验统一使用：

```text
epochs: 100
batch: 4
imgsz: 640
seed: 42
amp: true
deterministic: true
cos_lr: true
```

说明：最初 baseline 和 A-P2 使用过更大的 batch，但本机 RTX 4060 Laptop 8GB 在 A-P2 上频繁 OOM，并触发 CPU fallback；显存占用仍偏高。因此后续正式对比实验统一改为 `batch=4`，保证所有结构变体公平比较。

## 当前 DIOR-R 实验进展

Baseline、A-P2、B-LSK、C-Dynamic、B-PKI-Lite 和 A+B-PKI-Lite 已完成 `test` split 评估。A-P2 相对 baseline 在全尺度和小目标指标上均有提升，可以作为有效消融基础；B-LSK 当前单独实验未提升；C-Dynamic 和 B-PKI-Lite 轻微正向；A+B-PKI-Lite 继续超过 A-P2，是当前最佳组合。
C-Dynamic-Plus 已完成代码和配置，当前待训练，用于复验稍重一点的 C 方向几何适应模块。

| 实验 | 配置 | 权重 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 | 状态 |
|---|---|---|---:|---:|---:|---:|---|
| Baseline | `experiments/dior/baseline.yaml` | `weights/baselines/dior-r/yolo11n-obb-dior-r-best.pt` | 0.8588 | 0.6874 | 0.5146 | 0.3470 | 已评估 |
| A-P2 | `experiments/dior/a_p2.yaml` | `weights/experiments/dior/a_p2/best.pt` | 0.8779 | 0.6990 | 0.5830 | 0.4215 | 已评估 |
| B-LSK | `experiments/dior/b_lsk.yaml` | `weights/experiments/dior/b_lsk/best.pt` | 0.8580 | 0.6809 | 0.5070 | 0.3438 | 未提升 |
| B-PKI-Lite | `experiments/dior/b_pki_lite_homews.yaml` | `weights/experiments/dior/b_pki_lite/best.pt` | 0.8588 | 0.6885 | 0.5249 | 0.3621 | 小幅提升，已续训到 100，best 优于 last |
| C-Dynamic | `experiments/dior/c_dynamic.yaml` | `weights/experiments/dior/c_dynamic/best.pt` | 0.8562 | 0.6884 | 0.5173 | 0.3527 | 小幅提升 |
| C-Dynamic-Plus | `experiments/dior/c_dynamic_plus_homews.yaml` | 待训练 | - | - | - | - | ready |
| A+B-PKI-Lite | `experiments/dior/ab_p2_pki_lite_homews.yaml` | `weights/experiments/dior/ab_p2_pki_lite/best.pt` | 0.8859 | 0.7198 | 0.5958 | 0.4288 | 当前最佳 |
| A-P2 相对 baseline | - | - | +0.0191 | +0.0116 | +0.0684 | +0.0745 | 有效 |
| B-LSK 相对 baseline | - | - | -0.0008 | -0.0065 | -0.0076 | -0.0032 | 无效 |
| B-PKI-Lite 相对 baseline | - | - | +0.0000 | +0.0011 | +0.0103 | +0.0151 | 轻微正向 |
| C-Dynamic 相对 baseline | - | - | -0.0026 | +0.0010 | +0.0027 | +0.0057 | 轻微正向 |
| A+B-PKI-Lite 相对 baseline | - | - | +0.0271 | +0.0324 | +0.0812 | +0.0818 | 最佳 |

### 参数量变化

下表用于论文消融表中的轻量化分析。B-LSK 为已记录的无效消融，当前有效候选重点看 A-P2、B-PKI-Lite、C-Dynamic 和 A+B-PKI-Lite。

| 实验 | Params | 相对 baseline 增加 | 参数增幅 |
|---|---:|---:|---:|
| Baseline | 2,657,623 | - | - |
| A-P2 | 2,698,340 | +40,717 | +1.53% |
| B-PKI-Lite | 2,699,673 | +42,050 | +1.58% |
| C-Dynamic | 2,676,940 | +19,317 | +0.73% |
| C-Dynamic-Plus | 2,734,555 | +76,932 | +2.90% |
| A+B-PKI-Lite | 2,740,390 | +82,767 | +3.11% |

详细记录见：

- `weights/experiments/dior/a_p2/eval_dior_test_2026-07-06.md`
- `weights/experiments/dior/a_p2/compare_with_baseline_dior_test_2026-07-06.md`
- `weights/experiments/dior/b_lsk/eval_dior_test_2026-07-09.md`
- `weights/experiments/dior/b_lsk/compare_with_baseline_a_p2_dior_test_2026-07-09.md`
- `weights/experiments/dior/c_dynamic/eval_dior_test_2026-07-10.md`
- `weights/experiments/dior/c_dynamic/compare_with_baseline_a_p2_b_lsk_dior_test_2026-07-10.md`
- `weights/experiments/dior/b_pki_lite/eval_dior_test_2026-07-11.md`
- `weights/experiments/dior/b_pki_lite/compare_with_baseline_a_b_lsk_c_dior_test_2026-07-11.md`
- `weights/experiments/dior/ab_p2_pki_lite/eval_dior_test_2026-07-13.md`
- `weights/experiments/dior/ab_p2_pki_lite/compare_with_baseline_a_b_pki_c_dior_test_2026-07-13.md`

## 命令

统一训练脚本：

```bash
python scripts/train_obb.py --config experiments/dior/baseline.yaml --env local
```

正式训练前先 dry-run：

```bash
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --env local --dry-run
```

B-LSK 复跑前检查配置：

```bash
python scripts/train_obb.py --config experiments/dior/b_lsk.yaml --env local --dry-run
```

B-PKI-Lite 本地训练前检查配置：

```bash
python scripts/train_obb.py --config experiments/dior/b_pki_lite.yaml --env local --dry-run
```

B-PKI-Lite `/home/ws` 服务器配置检查，服务器 batch 使用 `-1` 自动 batch：

```bash
python scripts/train_obb.py --config experiments/dior/b_pki_lite_homews.yaml --dry-run
```

A+B-PKI-Lite 本地训练前检查配置：

```bash
python scripts/train_obb.py --config experiments/dior/ab_p2_pki_lite.yaml --env local --dry-run
```

A+B-PKI-Lite `/home/ws` 服务器训练命令，服务器 batch 使用 `-1` 自动 batch：

```bash
python scripts/train_obb.py --config experiments/dior/ab_p2_pki_lite_homews.yaml
```

C-Dynamic 检查配置：

```bash
python scripts/train_obb.py --config experiments/dior/c_dynamic.yaml --env local --dry-run
```

C-Dynamic-Plus 本地训练前检查配置：

```bash
python scripts/train_obb.py --config experiments/dior/c_dynamic_plus.yaml --env local --dry-run
```

C-Dynamic-Plus `/home/ws` 服务器训练命令，服务器 batch 使用 `-1` 自动 batch：

```bash
python scripts/train_obb.py --config experiments/dior/c_dynamic_plus_homews.yaml
```
