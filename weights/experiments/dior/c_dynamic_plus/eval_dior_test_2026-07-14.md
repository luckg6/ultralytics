# C-Dynamic-Plus DIOR-R Test 评估记录

- 评估日期：2026-07-14
- 模型权重：`weights/experiments/dior/c_dynamic_plus/best.pt`
- 原始训练输出：`runs/obb/dior_C_dynamic_plus/weights/best.pt`
- 数据集配置：`DIOR.yaml`
- 数据划分：`test`
- 评估脚本：`scripts/evaluate_obb.py`
- 评估命令：

```bash
python scripts/evaluate_obb.py --model weights/experiments/dior/c_dynamic_plus/best.pt --data DIOR.yaml --split test --mode both
```

## 模型规模

- Ultralytics 评估摘要：185 layers, 2,696,431 parameters, 6.7 GFLOPs
- checkpoint 参数求和：2,704,215
- 论文表格建议使用与其他实验一致的 Ultralytics 评估摘要口径，即 Params=2,696,431、GFLOPs=6.7。

## Test 结果

| 评估范围 | mAP50 | mAP50-95 |
|---|---:|---:|
| 全尺度目标 | 0.8588 | 0.6896 |
| 小目标 | 0.5268 | 0.3541 |

## 备注

- 小目标评估使用仓库自定义协议：`EVAL_SMALL_ONLY=1`，只保留 `w * h < 1024` 的 GT 框和预测框。
- DIOR-R test 缓存扫描时仍有 15 张标签坐标越界图片被 Ultralytics 忽略，和前面评估保持同一数据处理口径。
- 训练日志已整理到 `experiments/logs/dior/c_dynamic_plus/`。
