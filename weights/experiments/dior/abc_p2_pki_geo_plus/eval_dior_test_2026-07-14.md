# A+B-PKI-Lite+C-Plus DIOR-R test 评估记录

- 日期：2026-07-14
- 模型：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-abc-p2-pki-geo-plus.yaml`
- 权重：`weights/experiments/dior/abc_p2_pki_geo_plus/best.pt`
- 原始输出权重：`runs/obb/dior_ABC_p2_pki_geo_plus/weights/best.pt`
- 数据集：`DIOR.yaml`
- split：`test`
- imgsz：640
- 评估 batch：4
- 小目标协议：`EVAL_SMALL_ONLY=1` 时只保留 `w * h < 1024` 的目标和预测框

## 训练配置摘要

- 本地配置：`experiments/dior/abc_p2_pki_geo_plus.yaml`
- `/home/ws` 服务器配置：`experiments/dior/abc_p2_pki_geo_plus_homews.yaml`
- 服务器训练使用：`batch=-1`，`cache=ram`
- 原始 run 目录：`runs/obb/dior_ABC_p2_pki_geo_plus`
- 归档日志目录：`experiments/logs/dior/abc_p2_pki_geo_plus/`

## 模型复杂度

- Ultralytics 评估摘要 Params：2,784,390
- GFLOPs：11.1

## DIOR-R test 结果

| 评估模式 | mAP50 | mAP50-95 |
|---|---:|---:|
| 全尺度 | 0.8832 | 0.7149 |
| 小目标 | 0.5838 | 0.4242 |

## 备注

本机评估时默认 val batch 对 P2 组合模型显存压力较高，因此使用 `batch=4` 完成全尺度和小目标评估。
