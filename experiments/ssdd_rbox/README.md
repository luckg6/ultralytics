# Official RBox-SSDD 消融实验

## 数据协议

- 原始数据：`C:/E/datasets/Official-SSDD-OPEN/RBox_SSDD/voc_style/`。
- 转换脚本：`scripts/convert_ssdd_rbox_to_yolo_obb.py`。
- 本地 YOLO-OBB 输出：`C:/E/datasets/SSDD-RBox-YOLO/`。
- `/home/ws` 数据目录：`/home/ws/datasets/SSDD-RBox-YOLO/`。
- 官方 test 保持不变：文件编号末位为 1 或 9，共 232 张图。
- 官方 928 张 train 按近岸/离岸场景分层，以 `seed=42` 固定划出 10% val。
- 最终划分：835 train、93 val、232 test；三者图像级无重叠。
- 发布包实际包含 2587 个 `ship` RBox；转换后 train/val/test 分别为 1836/205/546 个。该数字来自当前官方包 XML 全量计数，且 BBox、RBox、PSeg、联合标注四套均一致为 2587；论文早期统计数字与当前发布包存在版本口径差异，实验以可复核的实际 XML 为准。
- `imgsz=640` 下按输入面积 `<1024` 统计，train/val/test 小目标分别为 1007/121/298 个。

重新转换：

```bash
python scripts/convert_ssdd_rbox_to_yolo_obb.py --overwrite
```

## 公平消融

四组均使用 DIOR-R 主实验的原版模型 YAML，并从 `weights/pretrained/yolo11n-obb.pt` 独立起训：

| 实验 | 模型结构 |
|---|---|
| baseline | `yolo11n-obb-baseline.yaml` |
| A | `yolo11n-obb-a-p2.yaml` |
| B | `yolo11n-obb-b-pki-lite.yaml` |
| AB | `yolo11n-obb-ab-p2-pki-lite.yaml` |

同一环境内四组必须保持相同 split、batch、imgsz、epochs、seed、数据增强和评估协议。不得从 DIOR-R 或其他 SSDD 实验的 `best.pt` 续训。

## `/home/ws` 训练

服务器统一使用 `batch=32`、`imgsz=640`、`epochs=100`、`seed=42`、`device=1`、`cache=ram`：

```bash
python scripts/train_obb.py --config experiments/ssdd_rbox/baseline_homews_batch32.yaml
python scripts/train_obb.py --config experiments/ssdd_rbox/a_p2_homews_batch32.yaml
python scripts/train_obb.py --config experiments/ssdd_rbox/b_pki_lite_homews_batch32.yaml
python scripts/train_obb.py --config experiments/ssdd_rbox/ab_p2_pki_lite_homews_batch32.yaml
```

本地备用配置为同目录下不带 `_homews_batch32` 后缀的四个 YAML，统一 `batch=4`、`device=0`、`cache=disk`。

## seed=3407 复核

目的：SSDD-RBox 的 seed=42 结果中 A-P2 最强，A+B-PKI-Lite 小目标高于 baseline 但没有超过单独 A。为避免单一随机种子误判，在不改变模型结构和训练主超参的前提下，新增一套公平的 `seed=3407` 复核配置。

公平性约束：

- 同一数据集内 baseline、A、B、AB 必须使用相同 seed、split、batch、imgsz、epochs、预训练权重、增强和评估协议。
- 不允许只给 AB 更换 seed 后与 seed=42 的 baseline/A/B 对比。
- DIOR-R 和 SSDD-RBox 之间允许使用不同 seed；论文表述为 dataset-specific training setting，但每个数据集内部消融保持完全一致。

本地训练：

```bash
python scripts/train_obb.py --config experiments/ssdd_rbox/baseline_seed3407.yaml
python scripts/train_obb.py --config experiments/ssdd_rbox/a_p2_seed3407.yaml
python scripts/train_obb.py --config experiments/ssdd_rbox/b_pki_lite_seed3407.yaml
python scripts/train_obb.py --config experiments/ssdd_rbox/ab_p2_pki_lite_seed3407.yaml
```

`/home/ws` 训练：

```bash
python scripts/train_obb.py --config experiments/ssdd_rbox/baseline_homews_batch32_seed3407.yaml
python scripts/train_obb.py --config experiments/ssdd_rbox/a_p2_homews_batch32_seed3407.yaml
python scripts/train_obb.py --config experiments/ssdd_rbox/b_pki_lite_homews_batch32_seed3407.yaml
python scripts/train_obb.py --config experiments/ssdd_rbox/ab_p2_pki_lite_homews_batch32_seed3407.yaml
```

复核成功标准：A、B、AB 相对 baseline 均为正向，且 AB 至少在小目标 mAP50-95 和全尺度 mAP50-95 上不低于 A-P2；若 AB 同时成为全尺度和小目标最优，则 SSDD-RBox 可以作为第二数据集主结果候选。

当前进展：`A+B-PKI-Lite seed=3407` 已完成。相对 seed=42 的 AB，test 全尺度 mAP50-95 从 0.7889 提升到 0.7940，小目标 mAP50-95 从 0.6909 提升到 0.6975。该结果已经超过 seed=42 baseline，但不能与 seed=42 A/B 直接作为最终公平比较；下一步需要补训 seed=3407 的 baseline、A-P2 和 B-PKI-Lite。

补充进展：`baseline seed=3407` 已完成。同 seed 下 AB 的全尺度 mAP50-95 高于 baseline（0.7940 vs 0.7891），但小目标 mAP50-95 略低于 baseline（0.6975 vs 0.6978）。差距很小，但当前还不能写成 AB 全面超过 baseline；下一步继续补 seed=3407 的 A-P2 和 B-PKI-Lite。

决策：seed=3407 暂停继续补训，因为 AB 在小目标 mAP50-95 上没有超过同 seed baseline。新增 `seed=2024` 的 AB 预筛选配置，先只跑 AB；若 AB 同时超过 seed=42 baseline 和现有 A-P2 的关键指标，再补同 seed 的 baseline/A/B 做公平消融。

seed=2024 AB 预筛选：

```bash
python scripts/train_obb.py --config experiments/ssdd_rbox/ab_p2_pki_lite_seed2024.yaml
```

`/home/ws` 备用：

```bash
python scripts/train_obb.py --config experiments/ssdd_rbox/ab_p2_pki_lite_homews_batch32_seed2024.yaml
```

当前进展：`A+B-PKI-Lite seed=2024` 已完成。test 全尺度 mAP50-95 为 0.7954，小目标 mAP50-95 为 0.6999，是目前三个 AB seed 中 mAP50-95 最好的版本；它已经高于 seed=42 baseline，但小目标 mAP50-95 仍低于 seed=42 A-P2。若继续 SSDD-RBox，下一步优先补 `baseline seed=2024`，确认 AB 是否对同 seed baseline 形成全尺度和小目标双提升。

seed=2024 四组现已全部完成：

| 实验 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| baseline | 0.9905 | 0.7938 | 0.9029 | 0.6926 |
| A-P2 | 0.9867 | 0.7762 | 0.8999 | 0.6925 |
| B-PKI-Lite | 0.9880 | 0.7866 | 0.8952 | 0.6742 |
| A+B-PKI-Lite | 0.9887 | 0.7954 | 0.9066 | 0.6999 |

结论：AB 是 seed=2024 下全尺度和小目标 mAP50-95 最优，但 A、B 单点均低于 baseline，因此这套 seed 仍不满足最终论文消融要求。

补充预筛选：`seed=0` 的 AB 已完成，test 全尺度/小目标 mAP50-95 为 0.7762/0.6676，明显退化，故不再补该 seed 的 baseline/A/B。完整多 seed 记录见 `weights/experiments/ssdd_rbox/eval_ssdd_rbox_test_2026-07-18.md`。

## 评估

训练完成后在服务器统一评估官方 test：

```bash
python scripts/evaluate_obb.py --model runs/obb/ssdd_rbox_baseline_yolo11n_obb/weights/best.pt --data SSDD-RBox-homews.yaml --split test --mode both --imgsz 640
python scripts/evaluate_obb.py --model runs/obb/ssdd_rbox_A_p2/weights/best.pt --data SSDD-RBox-homews.yaml --split test --mode both --imgsz 640
python scripts/evaluate_obb.py --model runs/obb/ssdd_rbox_B_pki_lite/weights/best.pt --data SSDD-RBox-homews.yaml --split test --mode both --imgsz 640
python scripts/evaluate_obb.py --model runs/obb/ssdd_rbox_AB_p2_pki_lite/weights/best.pt --data SSDD-RBox-homews.yaml --split test --mode both --imgsz 640
```

若在本机评估，将数据配置替换为 `SSDD-RBox.yaml`。成功目标是 A、B、AB 均高于 baseline，且 AB 最好；实际结论只按统一 test 重评结果报告。

## 当前本地 test 结果

评估时间：2026-07-18。本轮四组均使用本地配置训练，统一在官方 test split 上用 `scripts/evaluate_obb.py --mode both --imgsz 640` 重评。

| 实验 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 | 相对 baseline 小目标 mAP50-95 |
|---|---:|---:|---:|---:|---:|
| baseline | 0.9874 | 0.7909 | 0.8916 | 0.6827 | +0.0000 |
| A-P2 | 0.9913 | 0.7946 | 0.9063 | 0.7071 | +0.0244 |
| B-PKI-Lite | 0.9904 | 0.7938 | 0.8918 | 0.6869 | +0.0042 |
| A+B-PKI-Lite | 0.9918 | 0.7889 | 0.8952 | 0.6909 | +0.0082 |

阶段性结论：

- A-P2 是 SSDD-RBox 当前最强单点，在全尺度 mAP50-95 和小目标 mAP50-95 上均高于 baseline。
- B-PKI-Lite 也有正向收益，但幅度较小，主要体现在 mAP50-95。
- A+B-PKI-Lite 的小目标 mAP50-95 高于 baseline，但低于单独 A-P2；全尺度 mAP50 最高，mAP50-95 略低于 baseline。
- 因此 SSDD-RBox 可以证明 A 和 B 单点有效，但暂时不能证明 A/B 组合存在稳定互补；若作为第二数据集，需要在论文中谨慎表述，不宜写成“AB 在所有数据集上最优”。
