# Claude Code 服务器部署执行清单

本文档给服务器上的 Claude Code 使用。目标是在 `/home/ws/ultralytics` 中完成 Python venv 环境安装、自检，并确认训练脚本可以运行。

## 前提

仓库已经 clone 到：

```text
/home/ws/ultralytics
```

DIOR-R 数据集应放到：

```text
/home/ws/datasets/YOLODIOR-R/
```

目录结构必须是：

```text
/home/ws/datasets/YOLODIOR-R/
  train/images
  train/labels
  val/images
  val/labels
  test/images
  test/labels
```

本仓库是定制版 Ultralytics，不能只安装官方 `ultralytics` 包。必须在仓库根目录执行 editable install：

```bash
pip install -e .
```

## 1. 进入仓库

```bash
cd /home/ws/ultralytics
git status
```

确认当前分支包含最新提交，至少应包含这些文件：

```text
SERVER_VENV_SETUP.md
environments/homews.yaml
ultralytics/cfg/datasets/DIOR-homews.yaml
ultralytics/cfg/models/11/remote_obb/yolo11n-obb-c-dynamic.yaml
ultralytics/nn/modules/remote_obb_blocks.py
```

如果不是最新代码：

```bash
git pull
```

## 2. 创建并激活 venv

如果 `.venv` 不存在：

```bash
python3 --version
python3 -m venv .venv
```

激活：

```bash
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

建议 Python 版本为 3.10 或 3.11。

## 3. 安装 PyTorch

先检查 venv 里是否已有 torch：

```bash
python - <<'PY'
try:
    import torch
    print("torch:", torch.__version__)
    print("cuda:", torch.cuda.is_available())
    print("torch cuda version:", torch.version.cuda)
    print("gpu:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU only")
except Exception as e:
    print("torch import failed:", repr(e))
PY
```

如果没有 torch，按服务器 CUDA 版本安装 PyTorch。以官网选择器为准：

```text
https://pytorch.org/get-started/locally/
```

示例，CUDA 12.6 wheel：

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```

不要安装 CPU 版，除非只是临时验证脚本；正式训练必须让 `torch.cuda.is_available()` 为 `True`。

## 4. 安装本仓库定制版 Ultralytics

在仓库根目录执行：

```bash
cd /home/ws/ultralytics
source .venv/bin/activate
pip install -e .
```

验证导入路径：

```bash
python - <<'PY'
import ultralytics
from pathlib import Path
print(Path(ultralytics.__file__).resolve())
PY
```

输出必须位于：

```text
/home/ws/ultralytics/ultralytics/
```

如果输出在 `site-packages/ultralytics`，说明环境用的是官方包，需要重新在仓库根目录执行：

```bash
pip install -e .
```

## 5. 准备权重

确认存在：

```bash
ls -lh weights/pretrained/yolo11n-obb.pt
ls -lh weights/pretrained/yolo26n.pt
```

说明：

- `yolo11n-obb.pt` 是所有主实验的初始化权重。
- `yolo26n.pt` 用于 Ultralytics AMP 检查，放好后可避免联网下载。

如果文件不存在，需要从本地或远程仓库补齐后再训练。

## 6. 检查数据集配置

当前服务器环境配置：

```text
environments/homews.yaml
```

内容应指向：

```text
ultralytics/cfg/datasets/DIOR-homews.yaml
```

数据集 YAML 的根路径应为：

```text
/home/ws/datasets/YOLODIOR-R/
```

检查：

```bash
cat environments/homews.yaml
cat ultralytics/cfg/datasets/DIOR-homews.yaml
```

## 7. 服务器自检

```bash
cd /home/ws/ultralytics
source .venv/bin/activate
python scripts/check_server_env.py --env homews --require-cuda
```

期望结果：

- torch import 成功。
- CUDA available 为 `True`。
- pretrained weight 存在。
- `train/val/test images` 均为 OK，并显示图片数量。
- 最后一行是：

```text
[RESULT] server environment looks ready.
```

如果数据集路径 MISSING，先不要训练，检查 `/home/ws/datasets/YOLODIOR-R/` 的目录结构。

## 8. 训练脚本 dry-run

当前优先训练 C-Dynamic：

```bash
python scripts/train_obb.py --config experiments/dior/c_dynamic.yaml --env homews --dry-run
```

期望输出包含：

```text
Experiment config is ready.
model:      ultralytics/cfg/models/11/remote_obb/yolo11n-obb-c-dynamic.yaml
data:       ultralytics/cfg/datasets/DIOR-homews.yaml
name:       dior_C_dynamic
epochs:     100
batch:      4
imgsz:      640
device:     0
cache:      ram
workers:    8
```

## 9. 正式训练

dry-run 通过后启动：

```bash
python scripts/train_obb.py --config experiments/dior/c_dynamic.yaml --env homews
```

其他实验命令：

```bash
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --env homews
python scripts/train_obb.py --config experiments/dior/b_lsk.yaml --env homews
python scripts/train_obb.py --config experiments/dior/c_dynamic.yaml --env homews
```

注意：B-LSK 已评估未提升；当前建议优先跑 C-Dynamic。

## 10. 断点续训

如果训练中断：

```bash
python scripts/train_obb.py \
  --config experiments/dior/c_dynamic.yaml \
  --env homews \
  --resume runs/obb/dior_C_dynamic/weights/last.pt
```

`--resume` 是恢复 optimizer、scaler、epoch 等状态，不是把 `last.pt` 当新的 pretrained。

## 11. 训练完成后整理结果

训练完成后整理权重：

```bash
mkdir -p weights/experiments/dior/c_dynamic
cp runs/obb/dior_C_dynamic/weights/best.pt weights/experiments/dior/c_dynamic/best.pt
cp runs/obb/dior_C_dynamic/weights/last.pt weights/experiments/dior/c_dynamic/last.pt
```

整理日志：

```bash
mkdir -p experiments/logs/dior/c_dynamic
cp runs/obb/dior_C_dynamic/results.csv experiments/logs/dior/c_dynamic/results.csv
cp runs/obb/dior_C_dynamic/args.yaml experiments/logs/dior/c_dynamic/args.yaml
cp runs/obb/dior_C_dynamic/results.png experiments/logs/dior/c_dynamic/results.png
```

提交回传：

```bash
git add weights/experiments/dior/c_dynamic experiments/logs/dior/c_dynamic
git commit -m "Add DIOR C-Dynamic results"
git push
```

## 12. 常见问题

### 找不到 `C3k2Geo` 或 `SPPFLSK`

说明没有使用本仓库源码，或没有执行 editable install。

处理：

```bash
cd /home/ws/ultralytics
source .venv/bin/activate
pip install -e .
```

### CUDA 不可用

检查：

```bash
nvidia-smi
python - <<'PY'
import torch
print(torch.__version__)
print(torch.cuda.is_available())
print(torch.version.cuda)
PY
```

如果 `torch.cuda.is_available()` 是 `False`，通常是 PyTorch wheel 与 CUDA/驱动不匹配，需要重新按 PyTorch 官网命令安装 GPU 版 torch。

### 数据集 MISSING

确认路径：

```bash
ls -lh /home/ws/datasets/YOLODIOR-R/train/images | head
ls -lh /home/ws/datasets/YOLODIOR-R/val/images | head
ls -lh /home/ws/datasets/YOLODIOR-R/test/images | head
```

如果数据集实际放在别处，修改：

```text
ultralytics/cfg/datasets/DIOR-homews.yaml
```

里的 `path`。

### 后续代码更新

普通更新：

```bash
cd /home/ws/ultralytics
source .venv/bin/activate
git pull
```

不需要重新 `pip install -e .`。

只有以下情况才需要重新安装：

- 修改了 `pyproject.toml`。
- 新增或删除 Python 依赖。
- 重建了 `.venv`。
- 发现 Python 导入的是官方 `site-packages/ultralytics`，不是 `/home/ws/ultralytics/ultralytics/`。
