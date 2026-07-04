# 遥感旋转框小目标检测实验记录

这个仓库当前用于做一篇偏 EI 会议水准的遥感图像小目标检测论文。任务方向是 OBB 旋转框检测，基础模型选用 YOLO11n-OBB，主数据集先用 DIOR-R，后续再补第二个遥感 OBB 数据集。

## 基线设定

- 任务：遥感图像旋转框检测，`task=obb`。
- 当前 DIOR-R 基线脚本：`scripts/baseline_train_dior.py`。
- DIOR-R 基线初始化方式：
  - 模型结构：`yolo11n-obb.yaml`
  - 预训练权重：`yolo11n-obb.pt`
  - 数据集配置：`DIOR.yaml`
- DIOR-R 数据集配置文件：`ultralytics/cfg/datasets/DIOR.yaml`。
- DIOR-R 本地路径：`C:/E/datasets/YOLODIOR-R/`。
- 当前 DIOR-R 基线训练参数：
  - `epochs=100`
  - `batch=16`
  - `imgsz=640`
  - `seed=42`
  - `deterministic=True`
  - `amp=True`
  - `cache='disk'`
  - `cos_lr=True`
- 当前 DIOR-R 基线结果：`runs/obb/train10/weights/best.pt`。
- 当前 DIOR-R 基线在 `runs/obb/train10/results.csv` 中的验证指标：
  - mAP50 约为 0.849
  - mAP50-95 约为 0.670

## 跨数据集基线原则

第二个数据集的 baseline 不应该使用 DIOR-R 训练得到的 `best.pt` 继续训练。

正确做法：

```text
yolo11n-obb.pt -> 第二个数据集训练 -> 第二个数据集 baseline best.pt
```

不推荐做法：

```text
yolo11n-obb.pt -> DIOR-R 训练得到 best.pt -> 第二个数据集继续训练
```

原因：DIOR-R 训练后的 `best.pt` 已经带有 DIOR-R 的领域适配信息，如果再拿它作为第二个数据集的 baseline 初始化，会让 baseline 不再是纯粹的 YOLO11n-OBB baseline，后续消融对比也不公平。

两个数据集上的实验应保持同一逻辑：

```text
DIOR-R:
baseline/A/B/C/AB/ABC 都从 yolo11n-obb.pt 起训

第二数据集:
baseline/A/B/C/AB/ABC 也都从 yolo11n-obb.pt 起训
```

除非论文明确做“跨数据集迁移学习”实验，否则不要把 DIOR-R 的 `best.pt` 用到第二个数据集的主实验里。

## 数据集说明

- DIOR-R 是第一个数据集，也建议作为论文主数据集。
- 最终论文表格建议统一使用同一个 split，例如都用 `split='test'`，确保所有模型公平比较。
- `cache='disk'` 会在 images 文件夹下生成 `.npy` 缓存文件，统计原始图片数量时不要把 `.npy` 算进去。
- 第二个数据集候选：
  - DOTA-v1.0：最适合遥感 OBB 检测论文，但训练成本更高。
  - HRSC2016：船舶旋转框数据集，体量更轻，适合作为第二数据集补实验。

## 小目标评估

仓库当前在 `ultralytics/models/yolo/obb/val.py` 里加入了自定义小目标评估开关，通过环境变量 `EVAL_SMALL_ONLY` 控制。注意这里的 `val.py` 是 Ultralytics 的 OBB 核心验证器文件，不是 `scripts/val.py` 这个项目脚本。

- `EVAL_SMALL_ONLY=0`：正常评估所有尺度目标。
- `EVAL_SMALL_ONLY=1`：只保留 `w * h < 1024` 的 GT 框和预测框。
- 在 `imgsz=640` 时，这大致对应模型输入尺度下小于 `32x32` 的目标。
- 论文中建议表述为“自定义小目标评估协议”，不要写成官方 Ultralytics 原生指标。

## 验证脚本现状

- 当前统一评估入口：`scripts/evaluate_obb.py`。
- 旧的 `scripts/val.py` 和 `scripts/val_new.py` 已删除，避免后续误用。
- `scripts/evaluate_obb.py` 支持传参，不再需要为每个模型手改硬编码路径。
- 默认会评估 `runs/obb/train10/weights/best.pt` 在 `DIOR.yaml` 的 `test` split 上的全尺度和小目标结果。

常用命令：

```bash
python scripts/evaluate_obb.py
python scripts/evaluate_obb.py --model runs/obb/train10/weights/best.pt --data DIOR.yaml --mode both
python scripts/evaluate_obb.py --model path/to/best.pt --data DOTAv1.yaml --split test --mode all
python scripts/evaluate_obb.py --model path/to/best.pt --data DIOR.yaml --mode small
```

## 实验矩阵

每个数据集上建议做 1 个 baseline 加 5 个改进实验：

1. Baseline：YOLO11n-OBB。
2. 创新点 A。
3. 创新点 B。
4. 创新点 C。
5. 双创新点融合：等 A/B/C 单独结果出来后，选择最强且兼容的一组融合。
6. 三创新点融合：A + B + C。

如果按“改进实验”计数，两个数据集是 `5 x 2 = 10` 个实验。
如果按论文表格行数计数，两个数据集都要包含 baseline，因此是 `6 x 2 = 12` 行。

建议论文表格：

- 主结果表：P、R、mAP50、mAP50-95、Params、GFLOPs、FPS 或 inference time。
- 消融实验表：baseline、A、B、C、最佳双融合、A+B+C。
- 小目标表：baseline 和最终模型的全尺度 mAP、小目标 mAP。
- 分类别表：可选，DIOR-R 上可以重点看 vehicle、ship、bridge、harbor、storagetank 等类别。

## 创新点方向候选

优先选择小而清楚、容易写论文动机、容易单独消融的改动：

- 小目标特征增强：增加 P2/4 检测层，或加强浅层特征融合。
- 轻量注意力或上下文模块：放在 neck 或 backbone 中，增强复杂遥感背景下的目标特征。
- OBB 定位相关改动：例如旋转框定位损失、角度分支、样本分配策略等。

做消融时，除非某个实验明确研究训练策略，否则要固定训练设置。不要随意改变 `imgsz`、epochs、优化器、数据增强、数据 split，否则很难说明提升来自模型结构本身。

## 命名规范

后续实验建议显式指定 run name，避免 `train10`、`train11` 这种名字混乱：

- `dior_baseline_yolo11n_obb`
- `dior_A_<short_name>`
- `dior_B_<short_name>`
- `dior_C_<short_name>`
- `dior_AB_<short_name>`
- `dior_ABC_<short_name>`
- 第二数据集把 `dior` 替换成对应数据集名，例如 `dota` 或 `hrsc`。

写论文表格前，要单独整理一份实验日志，记录每个实验的模型路径、训练参数、最终指标和验证命令。
