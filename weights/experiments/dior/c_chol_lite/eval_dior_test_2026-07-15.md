# C-Chol-Lite DIOR-R test 评估记录（2026-07-15）

## 基本信息

- 实验名：`dior_C_chol_lite`
- 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-c-chol-lite.yaml`
- 训练配置：`experiments/dior/c_chol_lite_homews.yaml`
- 训练输出：`runs/obb/dior_C_chol_lite/`
- 归档权重：`weights/experiments/dior/c_chol_lite/best.pt`
- 数据集：`DIOR.yaml`
- 评估 split：`test`
- 评估命令：

```bash
python scripts/evaluate_obb.py --model weights/experiments/dior/c_chol_lite/best.pt --data DIOR.yaml --split test --mode both
```

## 训练摘要

- 服务器配置：`batch=-1`，`cache=ram`
- 训练 epoch：100
- 训练期最佳 val mAP50-95：0.67428，出现在 epoch 99
- epoch 100 val mAP50-95：0.67426
- 训练日志归档：`experiments/logs/dior/c_chol_lite/`

## 参数量

- Ultralytics 评估摘要 Params：2,729,296
- GFLOPs：6.6
- 构建检查 Params：2,767,516

## test 评估结果

| 评估范围 | mAP50 | mAP50-95 |
|---|---:|---:|
| 全尺度 | 0.8577 | 0.6902 |
| 小目标 | 0.5282 | 0.3589 |

## 结论

C-Chol-Lite 是当前单独 C 方向中最好的版本：全尺度 mAP50-95 和小目标 mAP50-95 均超过 C-Dynamic-Plus、C-GRA-Lite 和 baseline。不过全尺度 mAP50 略低于 baseline，说明它主要改善更严格 IoU 阈值下的定位质量，而不是 mAP50。
