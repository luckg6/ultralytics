# 权重与评估记录管理

本目录用于整理预训练权重、实验权重和轻量评估记录。普通 `.pt`、`.pth`、`.ckpt`、`.safetensors` 训练输出由 git 忽略；`weights/pretrained/` 已在 `.gitignore` 中显式放行，用于同步服务器复现必需的官方预训练和混合初始化权重。

## 当前规则

- 预训练权重本地放在 `weights/pretrained/`。
- 训练完成后的长期保留权重统一放在 `weights/checkpoints/`，按章节、数据集、seed 和 variant 分层；见 [checkpoints/README.md](checkpoints/README.md)。
- `weights/experiments/` 只保留原始评估 Markdown，不再堆放训练权重。
- Markdown 评估记录可以提交，用于追踪结果。
- `weights/pretrained/` 中确属复现入口的权重可以提交；baseline 和实验 run 的 `best.pt`、`last.pt` 不提交。
- 论文主结果以 `paper/ippr2026/main.pdf` 为准，早期权重目录中的旧 DIOR-R 8:1:1 记录只作为历史证据。

## 目录示例

```text
weights/
  pretrained/
    yolo11n-obb.pt
  checkpoints/
    chapter3/
    chapter4/
  experiments/
    <evaluation records only>/
```

## 新服务器准备预训练权重

安装好本仓库环境后，可以在仓库根目录执行：

```bash
python - <<'PY'
from pathlib import Path
from ultralytics import YOLO

Path("weights/pretrained").mkdir(parents=True, exist_ok=True)
YOLO("yolo11n-obb.pt")
src = Path("yolo11n-obb.pt")
if src.exists():
    src.replace("weights/pretrained/yolo11n-obb.pt")
PY
```

如果服务器无法联网下载，请手动把 `yolo11n-obb.pt` 放到 `weights/pretrained/`。
