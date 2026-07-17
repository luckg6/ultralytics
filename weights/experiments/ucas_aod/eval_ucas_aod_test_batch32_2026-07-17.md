# UCAS-AOD 固定 batch=32 复核评估（2026-07-17）

## 评估协议

- 四组模型统一使用 `batch=32`、`device=1`、`cache=ram`、`seed=42` 训练 100 epoch。
- 所有模型都从 `weights/pretrained/yolo11n-obb.pt` 独立起训。
- 测试集：UCAS-AOD `test`，453 张图像、4610 个 OBB。
- 小目标协议：输入尺度下 `w*h<1024`，共 3282 个 GT。
- 评估命令：`scripts/evaluate_obb.py --data UCAS-AOD.yaml --split test --mode both`。

## 固定 batch=32 结果

| 模型 | 最佳 val epoch | 最佳 val mAP50-95 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 68 | 0.80149 | **0.9785** | **0.8024** | 0.9199 | 0.7371 |
| A-P2 | 89 | 0.79205 | 0.9755 | 0.7921 | 0.9239 | 0.7321 |
| B-PKI-Lite | 81 | **0.80278** | 0.9764 | 0.8006 | **0.9246** | **0.7410** |
| A+B-PKI-Lite | 89 | 0.78923 | 0.9752 | 0.7930 | 0.9208 | 0.7306 |

## 相对固定 batch baseline

| 模型 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| A-P2 | -0.0030 | -0.0103 | +0.0040 | -0.0050 |
| B-PKI-Lite | -0.0021 | -0.0018 | **+0.0047** | **+0.0039** |
| A+B-PKI-Lite | -0.0033 | -0.0094 | +0.0009 | -0.0065 |

## 与自动 batch 结果对照

| 模型 | 设置 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---|---:|---:|---:|---:|
| baseline | 自动 batch | 0.9770 | 0.8017 | 0.9226 | 0.7393 |
| baseline | batch=32 | 0.9785 | 0.8024 | 0.9199 | 0.7371 |
| A-P2 | 自动 batch | 0.9781 | 0.7946 | 0.9216 | 0.7291 |
| A-P2 | batch=32 | 0.9755 | 0.7921 | 0.9239 | 0.7321 |
| B-PKI-Lite | 自动 batch | 0.9787 | 0.8026 | 0.9287 | 0.7434 |
| B-PKI-Lite | batch=32 | 0.9764 | 0.8006 | 0.9246 | 0.7410 |
| A+B-PKI-Lite | 自动 batch | 0.9752 | 0.7930 | 0.9208 | 0.7306 |
| A+B-PKI-Lite | batch=32 | 0.9752 | 0.7930 | 0.9208 | 0.7306 |

## 结论

- 固定 batch 后 A-P2 和 AB 仍低于 baseline，说明它们在 UCAS-AOD 上的负向结果不是自动 batch 差异造成的。
- B-PKI-Lite 在两轮设置中都稳定提升小目标指标：小目标 mAP50-95 分别提升 +0.0041 和 +0.0039。
- B 的全尺度提升不稳定：自动 batch 时 mAP50-95 为 +0.0009，固定 batch 时为 -0.0018，因此不能声称 B 在 UCAS-AOD 全尺度指标上稳定优于 baseline。
- UCAS-AOD 可以作为 B 对小目标有效性的辅助证据，但当前不支持 A-P2 或 AB 的跨数据集普适提升。若论文主方法必须是 AB，应更换更能体现真实微小目标与多尺度难度的第二数据集。

## 归档位置

- 权重：`weights/experiments/ucas_aod/{baseline,a_p2,b_pki_lite,ab_p2_pki_lite}_batch32_verify/best.pt`
- 日志：`experiments/logs/ucas_aod/{baseline,a_p2,b_pki_lite,ab_p2_pki_lite}_batch32_verify/`

