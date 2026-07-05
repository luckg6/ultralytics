# 实验配置登记

这个目录用于登记 EI 会议论文和毕业学位论文的训练实验配置。它不是 Ultralytics 官方配置目录，而是本课题的实验台账。

## 原则

- 每个数据集单独一个子目录。
- 每个实验变体单独一个 YAML。
- YAML 记录模型结构、预训练权重、数据集、训练超参、run name 和当前状态。
- `status: planned` 表示只登记计划，还没有可运行结构。
- `status: ready` 表示可以直接用统一训练脚本运行。

统一训练脚本：

```bash
python scripts/train_obb.py --config experiments/dior/baseline.yaml
```

正式训练前可先加 `--dry-run` 检查配置和路径：

```bash
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --dry-run
```
