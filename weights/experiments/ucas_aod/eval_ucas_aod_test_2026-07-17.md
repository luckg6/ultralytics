# UCAS-AOD 四组消融评估记录（2026-07-17）

## 评估协议

- 数据集：UCAS-AOD
- 数据配置：`ultralytics/cfg/datasets/UCAS-AOD.yaml`
- 划分：`test`，453 张图像、4610 个 OBB
- 输入尺寸：640
- 全尺度：正常评估全部目标
- 小目标：项目自定义协议，仅保留输入尺度下 `w*h<1024` 的 GT 和预测框，共 3282 个 GT
- 入口：`scripts/evaluate_obb.py --data UCAS-AOD.yaml --split test --mode both`

## 总体结果

| 模型 | Params | GFLOPs | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| YOLO11n-OBB baseline | 2,654,113 | 6.6 | 0.9770 | 0.8017 | 0.9226 | 0.7393 |
| A-P2 | 2,695,964 | 10.5 | 0.9781 | 0.7946 | 0.9216 | 0.7291 |
| B-PKI-Lite | 2,696,163 | 6.8 | **0.9787** | **0.8026** | **0.9287** | **0.7434** |
| A+B-PKI-Lite | 2,738,014 | 10.7 | 0.9752 | 0.7930 | 0.9208 | 0.7306 |

## 相对 baseline

| 模型 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| A-P2 | +0.0011 | -0.0071 | -0.0010 | -0.0102 |
| B-PKI-Lite | **+0.0017** | **+0.0009** | **+0.0061** | **+0.0041** |
| A+B-PKI-Lite | -0.0018 | -0.0087 | -0.0018 | -0.0087 |

## 训练期验证摘要

| 模型 | 最佳 epoch | 最佳 val mAP50-95 |
|---|---:|---:|
| baseline | 92 | 0.80092 |
| A-P2 | 81 | 0.78874 |
| B-PKI-Lite | 58 | 0.80470 |
| A+B-PKI-Lite | 89 | 0.78923 |

## 结论

- B-PKI-Lite 是 UCAS-AOD 上唯一在全尺度和小目标四项指标中均超过 baseline 的改进，方向与 DIOR-R 一致，但提升幅度较小。
- A-P2 在 UCAS-AOD 上只提升了全尺度 mAP50，mAP50-95 和小目标指标均下降。该数据集的 baseline 小目标精度已经较高，额外 P2 分支没有复现 DIOR-R 上的明显收益。
- A+B-PKI-Lite 没有超过 baseline、A 或 B，说明 A 与 B 在 UCAS-AOD 上未形成 DIOR-R 中的正向互补。
- 四组服务器配置都使用 `batch=-1`，自动 batch 导致每个 epoch 的批次数分别为 14、23、16、24。Ultralytics 会通过梯度累积接近名义 batch，但严格论文消融仍建议在最终结果确定后用共同固定 batch 复核。
- A 的 `args.yaml` 记录原始运行名为 `ucas_aod_A_p22`，当前整理目录名为 `ucas_aod_A_p2`；权重与日志来自该次完整 100 epoch 训练。

## 归档位置

- 权重：`weights/experiments/ucas_aod/{baseline,a_p2,b_pki_lite,ab_p2_pki_lite}/best.pt`
- 日志：`experiments/logs/ucas_aod/{baseline,a_p2,b_pki_lite,ab_p2_pki_lite}/`

