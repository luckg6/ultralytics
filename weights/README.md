# 权重文件管理

本目录统一管理论文实验相关权重，避免把 `.pt` 文件散落在仓库根目录、`modelPt/` 或临时 run 目录中。

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
```

## 使用原则

- 官方预训练权重统一放在 `weights/pretrained/`。
- 数据集 baseline 权重统一放在 `weights/baselines/<dataset>/`。
- DIOR-R baseline 权重是 `weights/baselines/dior-r/yolo11n-obb-dior-r-best.pt`。
- A/B/C/AB/ABC 等结构变体训练出来的权重，后续建议放在 `weights/experiments/<dataset>/<variant>/`，或保留在对应 `runs/` 目录并在实验日志中登记。
- 不要再把新的 `.pt` 文件直接放在仓库根目录。

