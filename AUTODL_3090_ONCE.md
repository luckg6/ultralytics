# AutoDL 3090 一次性续训说明

这份说明只服务本次 `dior_ABC_p2_pki_chol_lite` 续训。长期服务器仍优先使用 `/home/ws` 配置。

## 机器建议

- GPU：RTX 3090 24GB
- 镜像：PyTorch 镜像即可，截图里的 PyTorch 2.8.0 / Python 3.12 / CUDA 12.8 可以用。
- 代码目录建议：`/root/autodl-tmp/ultralytics`
- 数据集目录建议：`/root/autodl-tmp/datasets/YOLODIOR-R`

数据集目录结构应为：

```text
/root/autodl-tmp/datasets/YOLODIOR-R/
  train/images
  train/labels
  val/images
  val/labels
  test/images
  test/labels
```

对应数据集配置文件为 `ultralytics/cfg/datasets/DIOR-autodl.yaml`。

## 首次进入服务器

```bash
cd /root/autodl-tmp
git clone git@github.com:luckg6/ultralytics.git
cd /root/autodl-tmp/ultralytics
```

如果服务器没有配 GitHub SSH key，也可以用 HTTPS：

```bash
git clone https://github.com/luckg6/ultralytics.git
```

## 安装环境

如果镜像已有 PyTorch，不要额外重装 torch。只安装项目依赖和本地包：

```bash
cd /root/autodl-tmp/ultralytics
python -m pip install -U pip
pip install -e .
```

如果 `pip install -e .` 因为仓库裁剪缺少官方打包文件失败，改用直接源码运行即可，先补最小依赖：

```bash
pip install ultralytics pyyaml opencv-python pillow pandas matplotlib tqdm
```

## 检查配置

```bash
python scripts/train_obb.py \
  --config experiments/dior/abc_p2_pki_chol_lite_autodl3090.yaml \
  --env autodl_3090_once \
  --resume runs/obb/dior_ABC_p2_pki_chol_lite/weights/last_autodl3090.pt \
  --dry-run
```

期望看到：

```text
data:   ultralytics/cfg/datasets/DIOR-autodl.yaml
device: 0
batch:  -1
cache:  ram
```

## 开始续训

```bash
python scripts/train_obb.py \
  --config experiments/dior/abc_p2_pki_chol_lite_autodl3090.yaml \
  --env autodl_3090_once \
  --resume runs/obb/dior_ABC_p2_pki_chol_lite/weights/last_autodl3090.pt
```

说明：

- 断点已经单独准备为 `last_autodl3090.pt`，内部 `train_args` 指向 `/root/autodl-tmp/ultralytics/runs/obb/dior_ABC_p2_pki_chol_lite`。
- `batch=-1` 会在 3090 上自动估计 batch；如果显存仍不稳，可改命令追加 `--batch 8` 或 `--batch 4`。
- `cache=ram` 适合该机器 90GB 内存；如果数据集缓存失败，再追加 `--cache disk`。

## 训练后回传

训练完成后建议提交：

```bash
git status
git add -f runs/obb/dior_ABC_p2_pki_chol_lite
git commit -m "Add AutoDL ABC Chol run results"
git push origin main
```

本地拉取后再用：

```bash
python scripts/evaluate_obb.py --model runs/obb/dior_ABC_p2_pki_chol_lite/weights/best.pt --data DIOR.yaml --split test --mode both
```
