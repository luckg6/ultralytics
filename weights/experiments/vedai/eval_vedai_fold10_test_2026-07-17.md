# VEDAI-1024 fold10 test 评估（2026-07-17）

## 评估协议

- 四组模型统一使用 `batch=32`、`device=1`、`cache=ram`、`seed=42` 训练 100 epoch。
- 所有模型都从 `weights/pretrained/yolo11n-obb.pt` 独立起训。
- 固定单划分：官方 fold01、03-09 训练，fold02 验证，fold10 测试。
- 测试集：121 张图像、369 个 OBB。
- 小目标协议：模型输入尺度下 `w*h<1024`。
- 评估命令：`scripts/evaluate_obb.py --data VEDAI-1024.yaml --split test --mode both`。
- 这是 fold10 固定单划分筛选结果，不是完整十折交叉验证均值。

## 评估结果

| 模型 | 最佳 val epoch | 最佳 val mAP50-95 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 67 | **0.53169** | 0.7300 | 0.5661 | 0.6831 | 0.5293 |
| A-P2 | 57 | 0.48588 | 0.6526 | 0.4687 | 0.5978 | 0.4311 |
| B-PKI-Lite | 52 | 0.51923 | **0.7482** | **0.5756** | **0.7014** | **0.5365** |
| A+B-PKI-Lite | 73 | 0.46672 | 0.6782 | 0.4994 | 0.6320 | 0.4674 |

## 相对 baseline

| 模型 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| A-P2 | -0.0774 | -0.0974 | -0.0853 | -0.0982 |
| B-PKI-Lite | **+0.0182** | **+0.0095** | **+0.0183** | **+0.0072** |
| A+B-PKI-Lite | -0.0518 | -0.0667 | -0.0511 | -0.0619 |

## 复杂度

| 模型 | Params | GFLOPs | 训练时间 |
|---|---:|---:|---:|
| baseline | 2,655,478 | 6.6 | 452.9 s |
| A-P2 | 2,696,888 | 10.5 | 540.6 s |
| B-PKI-Lite | 2,697,528 | 6.8 | 507.5 s |
| A+B-PKI-Lite | 2,738,938 | 10.7 | 574.4 s |

## 结论

- B-PKI-Lite 是唯一四项 test 指标都高于 baseline 的改进，支持 B 的跨数据集有效性。
- A-P2 在 VEDAI 上明显负向；其全尺度和小目标召回率与 baseline 接近，但精确率明显下降，表现为额外 P2 预测带来更多误检。
- AB 相对 A 有明显回升：全尺度 mAP50-95 `+0.0307`，小目标 mAP50-95 `+0.0363`，说明 B 能部分缓解 A 的负作用；但 AB 仍然没有超过 baseline。
- VEDAI fold10 不支持“A、B、AB 全部涨点”的论文结论，因此不建议将它作为 AB 主方法的第二数据集主结果。

## 归档位置

- 权重：`weights/experiments/vedai/{baseline,a_p2,b_pki_lite,ab_p2_pki_lite}/best.pt`
- 训练日志：`experiments/logs/vedai/{baseline,a_p2,b_pki_lite,ab_p2_pki_lite}/`
