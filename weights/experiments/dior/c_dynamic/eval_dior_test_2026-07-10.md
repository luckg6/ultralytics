# C-Dynamic 在 DIOR-R test split 上的评估记录

评估日期：2026-07-10

## 模型与数据

- 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-c-dynamic.yaml`
- 权重：`weights/experiments/dior/c_dynamic/best.pt`
- 数据集配置：`DIOR.yaml`
- split：`test`
- 评估入口：`scripts/evaluate_obb.py`
- 小目标协议：`EVAL_SMALL_ONLY=1`，保留输入尺度下 `w * h < 1024` 的目标。

## 评估命令

```bash
python scripts/evaluate_obb.py --model weights/experiments/dior/c_dynamic/best.pt --data DIOR.yaml --split test --mode both
```

## 模型规模

- Params：2,676,940
- GFLOPs：6.6

## 评估结果

| 评估范围 | mAP50 | mAP50-95 |
|---|---:|---:|
| 全尺度目标 | 0.8562 | 0.6884 |
| 小目标 | 0.5173 | 0.3527 |

## 归档文件

- 训练权重：`weights/experiments/dior/c_dynamic/best.pt`
- 训练日志：`experiments/logs/dior/c_dynamic/`
- 全尺度评估图：`experiments/logs/dior/c_dynamic/eval_all/`
- 小目标评估图：`experiments/logs/dior/c_dynamic/eval_small/`

## 结论

C-Dynamic 相对 baseline 的全尺度 mAP50 略低，但 mAP50-95 和小目标指标略有提升，属于轻微正向但不强的单点改进。当前不如 A-P2 明显，后续若做融合，优先尝试 A+C，而不是把当前 B-LSK 直接加入。
