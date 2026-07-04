# YOLO11n-OBB 遥感小目标检测实验仓库

本仓库基于 Ultralytics YOLO 源码，用于完成一篇面向 EI 会议的遥感图像小目标旋转框检测论文。当前主线任务是以 YOLO11n-OBB 为基础模型，在 DIOR-R 和第二个遥感 OBB 数据集上完成 baseline、三个创新点和融合消融实验。

## 研究目标

- 任务：遥感图像小目标检测，采用 OBB 旋转框检测形式。
- 基础模型：`yolo11n-obb.pt`。
- 主数据集：DIOR-R。
- 第二数据集候选：DOTA-v1.0 或 HRSC2016。
- 论文实验目标：设计 3 个轻量、可解释、可消融的模型改进点，并验证单独改进和组合改进的效果。

## 当前 Baseline

DIOR-R baseline 使用以下流程：

```text
yolo11n-obb.pt -> DIOR-R 训练 -> runs/obb/train10/weights/best.pt
```

当前训练脚本：

```bash
python scripts/baseline_train_dior.py
```

当前 DIOR-R baseline 关键设置：

- 模型结构：`yolo11n-obb.yaml`
- 预训练权重：`yolo11n-obb.pt`
- 数据集配置：`DIOR.yaml`
- 训练轮数：`epochs=100`
- 输入尺寸：`imgsz=640`
- batch：`batch=16`
- 随机种子：`seed=42`
- 确定性训练：`deterministic=True`
- 缓存：`cache='disk'`
- 学习率策略：`cos_lr=True`

当前 `runs/obb/train10/results.csv` 中的 DIOR-R baseline 验证指标约为：

- mAP50：0.849
- mAP50-95：0.670

## 跨数据集 Baseline 原则

第二个数据集的 baseline 不能使用 DIOR-R 训练得到的 `best.pt` 继续训练。正确做法是每个数据集都从同一个官方预训练权重起跑：

```text
DIOR-R:
yolo11n-obb.pt -> DIOR-R baseline/A/B/C/AB/ABC

第二数据集:
yolo11n-obb.pt -> 第二数据集 baseline/A/B/C/AB/ABC
```

除非论文明确做“跨数据集迁移学习”，否则不要把 DIOR-R 的 `best.pt` 用作第二数据集的初始化权重。

## 实验矩阵

每个数据集上建议保留 1 个 baseline 和 5 个改进实验：

1. Baseline：YOLO11n-OBB。
2. 创新点 A：小目标特征增强，例如 P2 检测层或轻量加权特征融合。
3. 创新点 B：遥感上下文注意力，例如 LSK 类大选择核注意力。
4. 创新点 C：旋转目标几何适应，例如轻量 DCN/DCNv3 或动态检测头。
5. 双创新点融合：优先尝试 A + B。
6. 三创新点融合：A + B + C。

如果按“改进实验”计数，两个数据集是 `5 x 2 = 10` 个实验；如果按论文表格行数计数，两个数据集都包含 baseline，则是 `6 x 2 = 12` 行。

## 验证脚本

统一使用：

```bash
python scripts/evaluate_obb.py
```

常用命令：

```bash
python scripts/evaluate_obb.py --model runs/obb/train10/weights/best.pt --data DIOR.yaml --mode both
python scripts/evaluate_obb.py --model path/to/best.pt --data DOTAv1.yaml --split test --mode all
python scripts/evaluate_obb.py --model path/to/best.pt --data DIOR.yaml --mode small
```

说明：

- `--mode all`：评估全尺度目标。
- `--mode small`：只评估小目标。
- `--mode both`：先评估全尺度目标，再评估小目标。
- 小目标评估依赖 `ultralytics/models/yolo/obb/val.py` 中的 `EVAL_SMALL_ONLY` 开关。
- 当前小目标定义是模型输入尺度下 `w * h < 1024`，在 `imgsz=640` 时约等价于小于 `32x32`。

## 顶会论文与代码沉淀

相关论文、官方代码入口和迁移计划放在：

```text
research/top_conference/
```

当前优先参考：

- EfficientDet / BiFPN：用于小目标多尺度特征融合。
- LSKNet：用于遥感场景长程上下文和大选择核注意力。
- InternImage / DCNv3：用于动态空间采样和旋转目标几何适应。
- Dynamic Head：作为检测头注意力的备选方向。

这些论文负责提供动机和模块设计依据；实际实现时要以 YOLO11n-OBB 的轻量化、可复现和消融清晰为第一优先级。

## 项目备注

更详细的实验约定、脚本状态和后续开发注意事项见：

```text
AGENTS.md
```

官方 Ultralytics 文档请参考：https://docs.ultralytics.com/
