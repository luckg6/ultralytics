# 权重文件管理

本目录统一管理本机论文实验权重，避免把 `.pt` 文件散落在仓库根目录、旧的 `modelPt/` 或临时 run 目录中。

从 2026-07-17 起，Git 不再跟踪 `.pt`、`.pth`、`.ckpt`、`.safetensors` 等权重文件，只保留目录中的 Markdown 评估记录。这样服务器拉取代码时不会继续下载新增实验权重；本地已有权重不会因取消 Git 跟踪而被删除。

## 目录结构

```text
weights/
  pretrained/
    yolo11n-obb.pt
    yolo11n.pt
    yolo11s.pt
    yolo11s-obb.pt
    yolo26n.pt
  baselines/
    dior-r/
      yolo11n-obb-dior-r-best.pt
      yolo11n-obb-dior-r-last.pt
  experiments/
    <dataset>/
      <variant>/
        best.pt
        last.pt
```

## 使用原则

- 官方预训练权重统一放在 `weights/pretrained/`。
- 数据集 baseline 权重统一放在 `weights/baselines/<dataset>/`。
- A/B/C/AB/ABC 等结构变体训练出的关键权重，可以整理到 `weights/experiments/<dataset>/<variant>/` 本地归档，但不要提交到 Git。
- 不要再把新的 `.pt` 文件直接放在仓库根目录。
- 需要跨机器传输关键权重时，使用网盘、对象存储或单独的模型发布，不再通过代码仓库传输。

## 服务器准备基础权重

新服务器克隆仓库并安装环境后，在仓库根目录执行：

```bash
python -c "from pathlib import Path; from ultralytics import YOLO; YOLO('yolo11n-obb.pt'); Path('weights/pretrained').mkdir(parents=True, exist_ok=True); Path('yolo11n-obb.pt').replace('weights/pretrained/yolo11n-obb.pt')"
```

该命令会通过 Ultralytics 下载官方 `yolo11n-obb.pt`，并移动到当前实验配置统一使用的 `weights/pretrained/yolo11n-obb.pt`。
