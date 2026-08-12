# HRSC2016 消融实验

> 状态：已完成并冻结的快速筛选记录。AB 低于 baseline，且 test 小目标数量有限，不进入当前论文主表，也没有待执行训练。

## 数据与转换

- 原始下载包：`C:/E/datasets/HRSC2016_dataset.zip.zip`。
- 解压目录：`C:/E/datasets/HRSC2016/HRSC2016/`。
- YOLO-OBB 数据：`C:/E/datasets/HRSC2016-YOLO/`。
- 转换脚本：`scripts/convert_hrsc2016_to_yolo_obb.py`。
- 服务器数据目录：`/home/ws/datasets/HRSC2016-YOLO/`。

发布包为两层 ZIP，内层包含 `HRSC2016.part01.rar` 至 `part05.rar`。五个 RAR 是同一连续分卷，从 `part01.rar` 解压即可自动合并。原始 `FullDataSet` 有 1680 张图，其中额外 610 张未进入检测划分；本项目只采用发布包 `ImageSets` 中互不重叠的 436 train、181 val、453 test，共 1070 张图。

| split | 图片 | OBB | 空背景图 | `imgsz=640` 小目标 |
|---|---:|---:|---:|---:|
| train | 436 | 1207 | 0 | 69 |
| val | 181 | 541 | 0 | 25 |
| test | 453 | 1228 | 15 | 61 |

小目标仍采用本项目统一协议：letterbox 到 `imgsz=640` 后旋转框面积 `<1024`。HRSC2016 中符合该协议的实例较少，因此它主要用于快速验证全尺度 OBB 泛化，小目标结果需结合 61 个 test 实例谨慎解释。

重新转换：

```bash
python scripts/convert_hrsc2016_to_yolo_obb.py --overwrite
```

## 本地训练

四组统一使用 `batch=4`、`imgsz=640`、`epochs=100`、`seed=42`、`device=0`、`cache=disk`，并从 `weights/pretrained/yolo11n-obb.pt` 独立起训：

```bash
python scripts/train_obb.py --config experiments/hrsc2016/baseline.yaml
python scripts/train_obb.py --config experiments/hrsc2016/a_p2.yaml
python scripts/train_obb.py --config experiments/hrsc2016/b_pki_lite.yaml
python scripts/train_obb.py --config experiments/hrsc2016/ab_p2_pki_lite.yaml
```

建议先跑 baseline 和 AB；只有 AB 的全尺度与小目标 mAP50-95 均高于 baseline，再补 A、B。

实际筛选已完成 baseline 与 AB。AB 四项均低于 baseline，因此按预设停止条件不再补 A/B，也不再换 seed。

| 模型 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| baseline | **0.9584** | **0.8289** | **0.3665** | **0.2852** |
| A+B-PKI-Lite | 0.9530 | 0.7900 | 0.3498 | 0.2805 |

AB 相对 baseline 变化为 `-0.0054/-0.0389/-0.0167/-0.0047`。HRSC2016 全尺度精度接近饱和，且 test 只有 61 个小目标，不适合作为当前 A+B 主方法的第二数据集。详细记录见 `weights/experiments/hrsc2016/eval_hrsc2016_test_2026-07-19.md`。

## `/home/ws` 训练

服务器配置统一使用 `batch=32`、`device=1`、`cache=ram`：

```bash
python scripts/train_obb.py --config experiments/hrsc2016/baseline_homews_batch32.yaml
python scripts/train_obb.py --config experiments/hrsc2016/a_p2_homews_batch32.yaml
python scripts/train_obb.py --config experiments/hrsc2016/b_pki_lite_homews_batch32.yaml
python scripts/train_obb.py --config experiments/hrsc2016/ab_p2_pki_lite_homews_batch32.yaml
```

## 评估

```bash
python scripts/evaluate_obb.py --model runs/obb/hrsc2016_baseline_yolo11n_obb/weights/best.pt --data HRSC2016.yaml --split test --mode both --imgsz 640 --device 0 --workers 0
python scripts/evaluate_obb.py --model runs/obb/hrsc2016_AB_p2_pki_lite/weights/best.pt --data HRSC2016.yaml --split test --mode both --imgsz 640 --device 0 --workers 0
```
