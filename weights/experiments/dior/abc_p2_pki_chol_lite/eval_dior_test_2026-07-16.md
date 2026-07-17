# A+B-PKI-Lite+C-Chol-Lite DIOR-R Test 评估

- 日期：2026-07-16
- 模型：`runs/obb/dior_ABC_p2_pki_chol_lite/weights/best.pt`
- 归档权重：`weights/experiments/dior/abc_p2_pki_chol_lite/best.pt`
- 数据集：`DIOR.yaml`
- split：`test`
- 评估命令：

```bash
python scripts/evaluate_obb.py --model runs/obb/dior_ABC_p2_pki_chol_lite/weights/best.pt --data DIOR.yaml --split test --mode both
```

## 评估摘要

- Params：2,819,058
- GFLOPs：10.7
- 全尺度 mAP50：0.8862
- 全尺度 mAP50-95：0.7190
- 小目标 mAP50：0.5774
- 小目标 mAP50-95：0.4209

## 训练摘要

- 输出目录：`runs/obb/dior_ABC_p2_pki_chol_lite/`
- 训练配置：`experiments/dior/abc_p2_pki_chol_lite_autodl3090.yaml`
- AutoDL 双 RTX 3090 续训配置：`environments/autodl_3090_once.yaml`
- 续训 batch：16 起训，后续使用 `--batch 32` 提速
- 训练期最佳 val mAP50-95：0.70558，出现在 epoch 100
- epoch 100 val mAP50：0.88188

