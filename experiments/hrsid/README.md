# HRSID 消融实验

## 数据协议

- 官方仓库：`research/external_repos/HRSID/`。
- 官方 JPG 包：`C:/E/datasets/HRSID/HRSID_JPG/`。
- YOLO-OBB 输出：`C:/E/datasets/HRSID-YOLO/`。
- 转换脚本：`scripts/convert_hrsid_to_yolo_obb.py`。
- `/home/ws` 数据目录：`/home/ws/datasets/HRSID-YOLO/`。

转换使用官方 COCO 实例轮廓，通过 OpenCV `minAreaRect` 生成最小面积四点旋转框。保留官方 1962 张 test；从官方 3642 张 train 中按 inshore/offshore 分层、`seed=42` 固定抽取 10% 作为 val。

| split | 图片 | OBB | `imgsz=640` 小目标 |
|---|---:|---:|---:|
| train | 3278 | 9974 | 9067 |
| val | 364 | 1064 | 989 |
| test | 1962 | 5918 | 5350 |

原始 train/test JSON 共 16969 条实例标注；最小外接框转换时丢弃 13 个面积不超过 1 像素的退化轮廓，最终保留 16956 个 OBB。小目标协议为 letterbox 到 `imgsz=640` 后旋转框面积 `<1024`。

## 本地训练

本地四组统一 `batch=8`、`imgsz=640`、`epochs=100`、`seed=42`、`device=0`、`cache=disk`：

```bash
python scripts/train_obb.py --config experiments/hrsid/baseline.yaml
python scripts/train_obb.py --config experiments/hrsid/a_p2.yaml
python scripts/train_obb.py --config experiments/hrsid/b_pki_lite.yaml
python scripts/train_obb.py --config experiments/hrsid/ab_p2_pki_lite.yaml
```

四组 seed42 已全部完成；seed2024 只复核了 A/AB，用于判断组合排序，不与 seed42 拼接消融表。

## 本地结果

统一在官方 test 上使用 `scripts/evaluate_obb.py --mode both` 评估，指标顺序为全尺度 mAP50、全尺度 mAP50-95、小目标 mAP50、小目标 mAP50-95：

| seed | 模型 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---:|---|---:|---:|---:|---:|
| 42 | baseline | 0.7550 | 0.4098 | 0.7303 | 0.3971 |
| 42 | A-P2 | **0.9354** | **0.6737** | **0.9167** | **0.6676** |
| 42 | B-PKI-Lite | 0.7400 | 0.4152 | 0.7072 | 0.3982 |
| 42 | A+B-PKI-Lite | 0.9343 | 0.6634 | 0.9166 | 0.6587 |
| 2024 | A-P2 | **0.9390** | **0.6761** | **0.9189** | **0.6669** |
| 2024 | A+B-PKI-Lite | 0.9371 | 0.6736 | 0.9147 | 0.6633 |
| 3407 | baseline | 0.7513 | 0.3963 | 0.7160 | 0.3736 |
| 3407 | A-P2 | 0.9371 | 0.6706 | 0.9178 | 0.6610 |
| 3407 | B-PKI-Lite | 0.7620 | 0.4191 | 0.7273 | 0.3888 |
| 3407 | A+B-PKI-Lite | **0.9396** | **0.6765** | **0.9212** | **0.6687** |

seed42 下，A 与 AB 相对 baseline 均有大幅提升；B 的全尺度/小目标 mAP50-95 分别微升 0.0054/0.0011，但两个 mAP50 下降。AB 相对 baseline 的全尺度/小目标 mAP50-95 分别提升 0.2536/0.2616，但仍低于 A 0.0103/0.0089。seed2024 下仍是 A 略高于 AB；seed3407 首次实现 AB 四项全部超过 A，当前待补 baseline/B。

结论：seed3407 四组已经完整实现 `AB > A > B > baseline`，且全尺度/小目标的 mAP50 与 mAP50-95 四项排序一致。HRSID 可正式作为 DIOR-R 之外的第二数据集结果。详细记录见 `weights/experiments/hrsid/eval_hrsid_test_2026-07-19.md`。

## seed3407 最终消融（已完成）

四组除 seed 和输出目录外，均与 seed42 本地配置一致。建议先训练 AB、A 并评估；只有 AB 的全尺度和小目标 mAP50-95 都高于 A，才继续补 baseline、B：

```bash
python scripts/train_obb.py --config experiments/hrsid/ab_p2_pki_lite_s3407.yaml
python scripts/train_obb.py --config experiments/hrsid/a_p2_s3407.yaml
python scripts/train_obb.py --config experiments/hrsid/baseline_s3407.yaml
python scripts/train_obb.py --config experiments/hrsid/b_pki_lite_s3407.yaml
```

对应输出目录分别为 `hrsid_AB_p2_pki_lite_s3407`、`hrsid_A_p2_s3407`、`hrsid_baseline_yolo11n_obb_s3407`、`hrsid_B_pki_lite_s3407`。该 seed 的四行必须独立成表，不得与 seed42/2024 结果拼接。

四组均已完成。baseline test 四项为 `0.7513/0.3963/0.7160/0.3736`；A 为 `0.9371/0.6706/0.9178/0.6610`；B 为 `0.7620/0.4191/0.7273/0.3888`；AB 为 `0.9396/0.6765/0.9212/0.6687`。B 相对 baseline 为 `+0.0107/+0.0228/+0.0113/+0.0152`；AB 相对 A 为 `+0.0025/+0.0059/+0.0034/+0.0077`，相对 baseline 为 `+0.1883/+0.2802/+0.2052/+0.2951`。

## `/home/ws` 训练

服务器四组统一 `batch=32`、`device=1`、`cache=ram`：

```bash
python scripts/train_obb.py --config experiments/hrsid/baseline_homews_batch32.yaml
python scripts/train_obb.py --config experiments/hrsid/a_p2_homews_batch32.yaml
python scripts/train_obb.py --config experiments/hrsid/b_pki_lite_homews_batch32.yaml
python scripts/train_obb.py --config experiments/hrsid/ab_p2_pki_lite_homews_batch32.yaml
```

## 评估

```bash
python scripts/evaluate_obb.py --model runs/obb/hrsid_baseline_yolo11n_obb/weights/best.pt --data HRSID.yaml --split test --mode both --imgsz 640 --device 0 --workers 0
python scripts/evaluate_obb.py --model runs/obb/hrsid_A_p2/weights/best.pt --data HRSID.yaml --split test --mode both --imgsz 640 --device 0 --workers 0
python scripts/evaluate_obb.py --model runs/obb/hrsid_B_pki_lite/weights/best.pt --data HRSID.yaml --split test --mode both --imgsz 640 --device 0 --workers 0
python scripts/evaluate_obb.py --model runs/obb/hrsid_AB_p2_pki_lite/weights/best.pt --data HRSID.yaml --split test --mode both --imgsz 640 --device 0 --workers 0
```
