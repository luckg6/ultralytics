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

建议按 baseline、A、B、AB 的顺序运行。服务器实际采用的自动 batch 会写入各自的 `args.yaml`，整理论文表格时需要一并记录。

## 评估

训练完成后统一在 `test` split 上评估全尺度和小目标指标：

```bash
python scripts/evaluate_obb.py --model runs/obb/ucas_aod_baseline_yolo11n_obb/weights/best.pt --data UCAS-AOD.yaml --split test --mode both
python scripts/evaluate_obb.py --model runs/obb/ucas_aod_A_p2/weights/best.pt --data UCAS-AOD.yaml --split test --mode both
python scripts/evaluate_obb.py --model runs/obb/ucas_aod_B_pki_lite/weights/best.pt --data UCAS-AOD.yaml --split test --mode both
python scripts/evaluate_obb.py --model runs/obb/ucas_aod_AB_p2_pki_lite/weights/best.pt --data UCAS-AOD.yaml --split test --mode both
```

论文消融表必须保留四行，重点检查 `B > baseline` 以及 `AB > A` 是否在 UCAS-AOD 上同时成立。
