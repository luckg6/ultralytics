# /home/ws 服务器 venv 环境与训练说明

本文档是当前服务器操作主入口。旧版服务器说明已经归档到 `paper/archive/md_cleanup_20260728/`。

## 目录约定

```text
/home/ws/ultralytics
/home/ws/datasets/YOLODIOR-R-official
/home/ws/datasets/HRSID-YOLO
```

第四章继续新增实验时，`/home/ws` 服务器统一使用：

- `device=1`
- `batch=16`
- `cache=ram`

如果要复现当前 IPPR 2026 论文表格，则按论文固定协议：

| 数据集 | batch | cache | seeds |
| --- | ---: | --- | ---: |
| DIOR-R official | 32 | RAM | 3 |
| HRSID-derived OBB | 8 | disk | 3 |

## 安装环境

服务器没有 conda 时使用 venv：

```bash
cd /home/ws
git clone <repo-url> ultralytics
cd /home/ws/ultralytics

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
```

按服务器 CUDA 版本安装 PyTorch。示例为 CUDA 12.1 wheel；如果机器镜像已经自带合适 PyTorch，可以跳过这一行。

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

安装本仓库的改动版 Ultralytics：

```bash
pip install -e .
```

必须使用 `-e`，因为仓库内 `ultralytics/` 包含 FSPB、LPCF、OBB head 等本项目改动，不能依赖 pip 上的官方包。

## 自检

```bash
source /home/ws/ultralytics/.venv/bin/activate
cd /home/ws/ultralytics

python - <<'PY'
import torch, ultralytics
print("torch", torch.__version__)
print("cuda", torch.cuda.is_available())
print("gpu0", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")
print("ultralytics", ultralytics.__file__)
PY
```

`ultralytics.__file__` 必须指向 `/home/ws/ultralytics/ultralytics/`，不能指向系统 `site-packages` 中的官方包。

## 数据集检查

DIOR-R official：

```bash
ls /home/ws/datasets/YOLODIOR-R-official/train/images | head
ls /home/ws/datasets/YOLODIOR-R-official/val/images | head
ls /home/ws/datasets/YOLODIOR-R-official/test/images | head
```

HRSID-derived OBB：

```bash
ls /home/ws/datasets/HRSID-YOLO/train/images | head
ls /home/ws/datasets/HRSID-YOLO/val/images | head
ls /home/ws/datasets/HRSID-YOLO/test/images | head
```

## 训练入口

统一训练命令：

```bash
python scripts/train_obb.py --config <experiment.yaml>
```

当前论文主实验目录：

```text
experiments/dior_official/
experiments/hrsid/
```

不要把旧 `experiments/dior/` 的 8:1:1 配置当作论文 DIOR-R official 主实验。

## 评估入口

```bash
python scripts/evaluate_obb.py \
  --model runs/obb/<run-name>/weights/best.pt \
  --data <dataset.yaml> \
  --split test \
  --mode both \
  --imgsz 640
```

`--mode both` 会同时给出全尺度和本项目小目标诊断指标。小目标定义为 `wh < 1024 px^2`。

## 常见问题

- 如果导入到了官方 `site-packages/ultralytics`，重新执行 `pip install -e .`。
- 如果 RAM cache 不够，临时改为 `cache=disk`，但正式复现实验要记录变化。
- 多卡 DDP 不支持自动 batch 时，手动指定能被 GPU 数量整除的 batch。
- 普通训练输出权重不要提交；`weights/pretrained/` 中服务器复现必需的预训练和混合初始化权重允许随 Git 同步。
