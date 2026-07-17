# UCAS-AOD 消融实验

UCAS-AOD 是 EI 会议论文的第二个遥感 OBB 数据集。本阶段只训练四组模型：baseline、A-P2、B-PKI-Lite 和 A+B-PKI-Lite。所有模型均直接从 `weights/pretrained/yolo11n-obb.pt` 起训，不使用 DIOR-R 训练权重做初始化。

## 数据集

- 本地目录：`C:/E/datasets/UCAS-AOD-YOLO/`
- `/home/ws` 目录：`/home/ws/datasets/UCAS-AOD-YOLO/`
- 类别：`car`、`airplane`
- 划分：755 train、302 val、453 test
- 实例：14597 个 OBB
- `imgsz=640` 时，按本项目 `w*h<1024` 协议统计的小目标约占 71%
- 本地数据配置：`ultralytics/cfg/datasets/UCAS-AOD.yaml`
- 服务器数据配置：`ultralytics/cfg/datasets/UCAS-AOD-homews.yaml`

服务器需要保持下面的目录结构：

```text
/home/ws/datasets/UCAS-AOD-YOLO/
  images/
    train/
    val/
    test/
  labels/
    train/
    val/
    test/
```

## 本地训练

本地配置固定使用 `batch=4`、`cache=disk`。这些配置已经包含 UCAS-AOD 本地数据路径，不要再加通用的 `--env local`，否则通用环境配置会把数据集覆盖回 DIOR-R。

```bash
python scripts/train_obb.py --config experiments/ucas_aod/baseline.yaml
python scripts/train_obb.py --config experiments/ucas_aod/a_p2.yaml
python scripts/train_obb.py --config experiments/ucas_aod/b_pki_lite.yaml
python scripts/train_obb.py --config experiments/ucas_aod/ab_p2_pki_lite.yaml
```

正式训练前可在命令末尾添加 `--dry-run` 检查配置。

## `/home/ws` 训练

服务器配置按约定固定使用 `device=1`、`batch=-1`、`cache=ram`，不需要额外传 `--env homews`。

```bash
cd /home/ws/ultralytics
source .venv/bin/activate

python scripts/train_obb.py --config experiments/ucas_aod/baseline_homews.yaml
python scripts/train_obb.py --config experiments/ucas_aod/a_p2_homews.yaml
python scripts/train_obb.py --config experiments/ucas_aod/b_pki_lite_homews.yaml
python scripts/train_obb.py --config experiments/ucas_aod/ab_p2_pki_lite_homews.yaml
```

建议按 baseline、A、B、AB 的顺序运行。`args.yaml` 会保留 `batch=-1`，不会记录自动选择后的具体 batch；本轮可由每 epoch 批次数确认四种结构实际采用了不同 batch。严格论文消融建议最终用共同固定 batch 复核。

## 评估

训练完成后统一在 `test` split 上评估全尺度和小目标指标：

```bash
python scripts/evaluate_obb.py --model runs/obb/ucas_aod_baseline_yolo11n_obb/weights/best.pt --data UCAS-AOD.yaml --split test --mode both
python scripts/evaluate_obb.py --model runs/obb/ucas_aod_A_p2/weights/best.pt --data UCAS-AOD.yaml --split test --mode both
python scripts/evaluate_obb.py --model runs/obb/ucas_aod_B_pki_lite/weights/best.pt --data UCAS-AOD.yaml --split test --mode both
python scripts/evaluate_obb.py --model runs/obb/ucas_aod_AB_p2_pki_lite/weights/best.pt --data UCAS-AOD.yaml --split test --mode both
```

## 当前结果

四组实验已于 2026-07-17 完成，并统一在 `test` split 上重评：

| 模型 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| baseline | 0.9770 | 0.8017 | 0.9226 | 0.7393 |
| A-P2 | 0.9781 | 0.7946 | 0.9216 | 0.7291 |
| B-PKI-Lite | **0.9787** | **0.8026** | **0.9287** | **0.7434** |
| A+B-PKI-Lite | 0.9752 | 0.7930 | 0.9208 | 0.7306 |

完整评估、参数量、训练期最佳 epoch 和公平性备注见 `weights/experiments/ucas_aod/eval_ucas_aod_test_2026-07-17.md`。

结论：B-PKI-Lite 在四项指标上均略高于 baseline；A-P2 和 AB 没有复现 DIOR-R 上的增益。因此 UCAS-AOD 可以支持 B 的跨数据集有效性，但当前不能用于声称 A 或 AB 在所有数据集上都稳定提升。

## 固定 batch=32 复核

保留上述 `batch=-1` 原始结果不动，另建四组固定 `batch=32` 的 `/home/ws` 复核实验。除 batch 和独立实验名外，其余设置与原实验保持一致，仍使用 1 号 GPU、RAM cache、`seed=42` 和相同预训练权重。

```bash
python scripts/train_obb.py --config experiments/ucas_aod/baseline_homews_batch32_verify.yaml
python scripts/train_obb.py --config experiments/ucas_aod/a_p2_homews_batch32_verify.yaml
python scripts/train_obb.py --config experiments/ucas_aod/b_pki_lite_homews_batch32_verify.yaml
python scripts/train_obb.py --config experiments/ucas_aod/ab_p2_pki_lite_homews_batch32_verify.yaml
```

对应输出目录为：

```text
runs/obb/ucas_aod_baseline_yolo11n_obb_b32_verify/
runs/obb/ucas_aod_A_p2_b32_verify/
runs/obb/ucas_aod_B_pki_lite_b32_verify/
runs/obb/ucas_aod_AB_p2_pki_lite_b32_verify/
```

四组复核已经完成，统一 `test --mode both` 结果如下：

| 模型 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| baseline | **0.9785** | **0.8024** | 0.9199 | 0.7371 |
| A-P2 | 0.9755 | 0.7921 | 0.9239 | 0.7321 |
| B-PKI-Lite | 0.9764 | 0.8006 | **0.9246** | **0.7410** |
| A+B-PKI-Lite | 0.9752 | 0.7930 | 0.9208 | 0.7306 |

固定 batch 后，A 和 AB 仍低于 baseline；B 的小目标 mAP50/mAP50-95 稳定提升 +0.0047/+0.0039，但全尺度 mAP50-95 低 0.0018。完整双轮对照见 `weights/experiments/ucas_aod/eval_ucas_aod_test_batch32_2026-07-17.md`。
