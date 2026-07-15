# C-GRA-Lite DIOR-R test 评估记录

- 日期：2026-07-15
- 模型：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-c-gra-lite.yaml`
- 权重：`weights/experiments/dior/c_gra_lite/best.pt`
- 原始输出权重：`runs/obb/dior_C_gra_lite/weights/best.pt`
- 数据集：`DIOR.yaml`
- split：`test`
- imgsz：640
- 评估 batch：4
- 评估 workers：0
- 小目标协议：`EVAL_SMALL_ONLY=1` 时只保留 `w * h < 1024` 的目标和预测框

## 训练配置摘要

- 本地配置：`experiments/dior/c_gra_lite.yaml`
- `/home/ws` 服务器配置：`experiments/dior/c_gra_lite_homews.yaml`
- 服务器训练使用：`batch=-1`，`cache=ram`
- 原始 run 目录：`runs/obb/dior_C_gra_lite`
- 归档日志目录：`experiments/logs/dior/c_gra_lite/`
- 训练期 val 最佳 epoch：97
- 训练期 val 最佳 mAP50-95：0.67415

## 模型复杂度

- Ultralytics 评估摘要 Params：2,713,135
- GFLOPs：6.7
- checkpoint 参数求和：2,720,919

## DIOR-R test 结果

| 评估模式 | mAP50 | mAP50-95 |
|---|---:|---:|
| 全尺度 | 0.8583 | 0.6861 |
| 小目标 | 0.5219 | 0.3522 |

## 备注

Windows 本机后台评估时使用 `workers=0`，避免 dataloader 多进程启动错误。C-GRA-Lite 的 test mAP50-95 未超过 C-Dynamic-Plus。
