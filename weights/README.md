# 权重与评估记录管理

本目录用于本地整理预训练权重、实验权重和轻量评估记录。当前 git 已忽略 `.pt`、`.pth`、`.ckpt`、`.safetensors` 等大文件，远程仓库不再承担权重传输。

## 当前规则

- 预训练权重本地放在 `weights/pretrained/`。
- baseline 权重本地可放在 `weights/baselines/<dataset>/`。
- A/B/C/AB/ABC 等实验权重本地可放在 `weights/experiments/<dataset>/<variant>/`。
- Markdown 评估记录可以提交，用于追踪结果；权重文件不要提交。
- 论文主结果以 `paper/ippr2026/main.pdf` 为准，早期权重目录中的旧 DIOR-R 8:1:1 记录只作为历史证据。

## 目录示例

```text
weights/
  pretrained/
    yolo11n-obb.pt
  baselines/
    dior-r/
  experiments/
    dior/
    hrsid/
    ssdd_rbox/
    vedai/
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
