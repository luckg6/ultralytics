# B-PKI-Lite 在 DIOR-R test split 上的评估记录

评估日期：2026-07-11

## 模型与数据

- 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-b-pki-lite.yaml`
- 权重：`weights/experiments/dior/b_pki_lite/best.pt`
- 数据集配置：`DIOR.yaml`
- split：`test`
- 评估入口：`scripts/evaluate_obb.py`
- 小目标协议：`EVAL_SMALL_ONLY=1`，保留输入尺度下 `w * h < 1024` 的目标。

## 训练状态

- 训练配置：`experiments/dior/b_pki_lite_homews.yaml`
- 服务器 batch：`-1`
- 初始训练日志：`runs/obb/dior_B_pki_lite/results.csv`，记录到 epoch 83/100。
- 本机续训日志：`C:/home/ws/ultralytics/runs/obb/dior_B_pki_lite/results.csv`，记录 epoch 84-100。
- 归档续训日志：`experiments/logs/dior/b_pki_lite/resume_epoch84_100_results.csv`。
- 训练已续训到 epoch 100。
- 训练期 val 最佳 mAP50-95 出现在 epoch 81，值为 0.67137。

说明：本记录的主结果基于 `best.pt` 做 test split 正式评估。续训到 epoch 100 后，`last_epoch100.pt` 的 test 指标低于 `best.pt`，因此论文主表仍建议使用 `best.pt`。

## 评估命令

```bash
python scripts/evaluate_obb.py --model weights/experiments/dior/b_pki_lite/best.pt --data DIOR.yaml --split test --mode both
```

## 模型规模

- Params：2,699,673
- GFLOPs：6.8

## 评估结果

| 评估范围 | mAP50 | mAP50-95 |
|---|---:|---:|
| 全尺度目标 | 0.8588 | 0.6885 |
| 小目标 | 0.5249 | 0.3621 |

## 100 epoch last.pt 补充评估

评估命令：

```bash
python scripts/evaluate_obb.py --model weights/experiments/dior/b_pki_lite/last_epoch100.pt --data DIOR.yaml --split test --mode both
```

| 权重 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| `best.pt` | 0.8588 | 0.6885 | 0.5249 | 0.3621 |
| `last_epoch100.pt` | 0.8560 | 0.6846 | 0.5225 | 0.3601 |

## 归档文件

- 最佳权重：`weights/experiments/dior/b_pki_lite/best.pt`
- 100 epoch 最终权重：`weights/experiments/dior/b_pki_lite/last_epoch100.pt`
- 训练日志：`experiments/logs/dior/b_pki_lite/`
- 全尺度评估图：`experiments/logs/dior/b_pki_lite/eval_all/`
- 小目标评估图：`experiments/logs/dior/b_pki_lite/eval_small/`
- 100 epoch 全尺度评估图：`experiments/logs/dior/b_pki_lite/eval_last100_all/`
- 100 epoch 小目标评估图：`experiments/logs/dior/b_pki_lite/eval_last100_small/`

## 结论

B-PKI-Lite 相对 baseline 的全尺度 mAP50 基本持平，mAP50-95 和小目标指标有小幅提升；相对旧 B-LSK 明显更好。它说明把 B 从 SPPF 单点上下文改到 neck 多核融合是更合理的方向，但单独效果仍弱于 A-P2。续训到 100 epoch 后的 `last_epoch100.pt` 略低于 `best.pt`，因此后续对比优先使用 `best.pt`。
