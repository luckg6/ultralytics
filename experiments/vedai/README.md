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
