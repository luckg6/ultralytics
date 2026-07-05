# 权重文件管理

本目录统一管理论文实验相关权重，避免把 `.pt` 文件散落在仓库根目录、旧的 `modelPt/` 或临时 run 目录中。

当前项目允许 Git 跟踪 `weights/` 下的 `.pt` 文件，方便服务器训练完成后提交权重，本地直接 `git pull` 获取结果。根目录临时下载的 `.pt` 文件仍然会被 `.gitignore` 忽略。

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
- A/B/C/AB/ABC 等结构变体训练出的关键权重，建议整理到 `weights/experiments/<dataset>/<variant>/` 后提交。
- 不要再把新的 `.pt` 文件直接放在仓库根目录。
- 如果单个权重超过 GitHub 普通文件限制，再考虑 Git LFS；当前 YOLO11n/YOLO11s 相关权重体积较小，可以直接 Git 管理。
