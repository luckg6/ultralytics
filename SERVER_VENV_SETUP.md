# Linux 服务器 venv 部署与训练流程

本文档适用于服务器没有 conda、准备使用 Python `venv` 的情况。

## 核心结论

本仓库是定制版 Ultralytics，已经改过 `ultralytics/` 源码、模型 YAML、训练脚本和评估逻辑。服务器必须使用本仓库源码运行，不能只安装官方 `ultralytics` 包。

首次部署需要执行：

```bash
pip install -e .
```

后续普通代码更新只需要：

```bash
git pull
```

只有修改依赖、修改 `pyproject.toml`、重建 venv 或误装官方包时，才需要重新执行 `pip install -e .`。

## 首次部署

你的服务器根目录如果是 `/home/ws`，建议目录：

```text
/home/ws/ultralytics
/home/ws/datasets/YOLODIOR-R
```

克隆仓库：

```bash
cd /home/ws
git clone https://github.com/luckg6/ultralytics.git
cd ultralytics
```

如果仓库是私有仓库，服务器需要提前配置 GitHub token 或 SSH key。

创建 venv：

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

建议 Python 使用 3.10 或 3.11。

## 安装 PyTorch

如果服务器镜像已经自带合适的 PyTorch，可以先检查：

```bash
python - <<'PY'
import torch
print(torch.__version__)
print(torch.cuda.is_available())
print(torch.version.cuda)
print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU only")
PY
```

如果 venv 里没有 torch，需要按服务器 CUDA 版本安装 PyTorch。以 PyTorch 官网安装选择器为准：

```text
https://pytorch.org/get-started/locally/
```

常见示例：

```bash
# 按服务器 CUDA 版本选择 cu126、cu128 等官方 wheel 源
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```

如果服务器镜像是 CUDA 12.1、12.4、12.6、12.8 等，优先选择官网对应命令。不要随便装 CPU 版，否则训练会非常慢。

## 安装本仓库

在仓库根目录执行：

```bash
cd /home/ws/ultralytics
source .venv/bin/activate
pip install -e .
```

`-e` 是 editable install，会让 Python 直接使用当前 Git 仓库里的源码。这样本地提交并推送后，服务器 `git pull` 就能使用最新的 `SPPFLSK`、`C3k2Geo`、小目标评估等改动。

验证导入路径：

```bash
python - <<'PY'
import ultralytics
from pathlib import Path
print(Path(ultralytics.__file__).resolve())
PY
```

输出应该位于：

```text
/home/ws/ultralytics/ultralytics/
```

## 准备数据和权重

DIOR-R 数据集放到：

```text
/home/ws/datasets/YOLODIOR-R/
```

目录结构应类似：

```text
YOLODIOR-R/
  train/images
  train/labels
  val/images
  val/labels
  test/images
  test/labels
```

预训练权重放到仓库内：

```text
weights/pretrained/yolo11n-obb.pt
weights/pretrained/yolo26n.pt
```

`yolo26n.pt` 用于 Ultralytics AMP 检查，放好后可以避免服务器联网下载。

## 自检

每次登录服务器后：

```bash
cd /home/ws/ultralytics
source .venv/bin/activate
python scripts/check_server_env.py --env homews --require-cuda
```

如果使用公司 5090 环境：

```bash
python scripts/check_server_env.py --env company5090 --require-cuda
```

## 启动训练

先 dry-run：

```bash
python scripts/train_obb.py --config experiments/dior/c_dynamic.yaml --env homews --dry-run
```

正式训练：

```bash
python scripts/train_obb.py --config experiments/dior/c_dynamic.yaml --env homews
```

其他实验只需要替换 `--config`：

```bash
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --env homews
python scripts/train_obb.py --config experiments/dior/b_lsk.yaml --env homews
python scripts/train_obb.py --config experiments/dior/c_dynamic.yaml --env homews
```

当前统一主实验 batch 是 `4`。

## 后续更新代码

本地 Codex 改完代码后提交并推送。服务器上：

```bash
cd /home/ws/ultralytics
source .venv/bin/activate
git pull
```

普通源码、YAML、脚本更新后，不需要重新 `pip install -e .`。

需要重新安装的情况：

- 改了 `pyproject.toml`。
- 新增或删除了 Python 依赖。
- 改了包入口配置。
- 删除或重建了 `.venv`。
- 发现导入的是官方 `site-packages/ultralytics`，不是当前仓库。

重新安装命令：

```bash
pip install -e .
```

## 断点续训

```bash
python scripts/train_obb.py \
  --config experiments/dior/c_dynamic.yaml \
  --env homews \
  --resume runs/obb/dior_C_dynamic/weights/last.pt
```

`--resume` 是恢复 optimizer、scaler、epoch 等训练状态，不是把 `last.pt` 当成新的预训练权重。

## 结果回传

训练结束后，建议把关键文件整理到 Git 跟踪目录：

```bash
mkdir -p weights/experiments/dior/c_dynamic
cp runs/obb/dior_C_dynamic/weights/best.pt weights/experiments/dior/c_dynamic/best.pt
cp runs/obb/dior_C_dynamic/weights/last.pt weights/experiments/dior/c_dynamic/last.pt
```

日志建议整理到：

```text
experiments/logs/dior/c_dynamic/
```

然后提交：

```bash
git add weights/experiments/dior/c_dynamic experiments/logs/dior/c_dynamic
git commit -m "Add DIOR C-Dynamic results"
git push
```
