# 实验 A：P2/4 小目标检测分支

## 选择原因

EfficientDet/BiFPN 提供了多尺度特征融合对小目标有帮助的论文动机，但实验 A 第一版不直接移植 EfficientDet 代码。原因是本项目的 baseline 是 YOLO11n-OBB，目标是用最小结构改动验证小目标高分辨率特征是否有效。

## 当前落地方式

- 结构配置：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-a-p2.yaml`
- 实验配置：`experiments/dior/a_p2.yaml`
- 变化：OBB head 从 `P3, P4, P5` 扩展为 `P2, P3, P4, P5`
- 预训练权重：`weights/pretrained/yolo11n-obb.pt`

## 训练命令

先检查配置：

```bash
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --dry-run
```

正式训练：

```bash
python scripts/train_obb.py --config experiments/dior/a_p2.yaml
```

## 是否需要下载论文或代码

当前不需要手动下载 PDF，也不需要把 EfficientDet 开源代码放入本仓库。论文链接和官方代码入口已经在本目录 README 中记录。后续如果要做 BiFPN 加权融合版本，再按需抽取最小必要实现。

