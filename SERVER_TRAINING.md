# Git 工作流：本地 Codex 开发 + 服务器训练

长期方案不再推荐反复手动打包 zip。推荐方式是：本地 Codex 改代码并提交到 Git，服务器只负责 `git pull` 更新代码和运行训练。`pip install -e .` 只需要首次部署时执行；editable 安装后，后续 `git pull` 的源码改动会直接生效，除非新增了依赖。

## 1. 分工

- 本地 Windows：Codex 改代码、改模型 YAML、改实验配置、写文档、提交 Git。
- Git 远端：同步代码。当前仓库已有 `origin=https://github.com/luckg6/ultralytics.git`。
- Linux 服务器：`git pull` 更新代码，运行训练和验证。
- 数据集和大权重：不进普通 Git，服务器首次准备一次即可。

## 2. 环境配置

实验配置和机器配置分开：

```text
experiments/dior/a_p2.yaml       # 实验本身：模型、epoch、batch、imgsz、seed
environments/local.yaml          # 本地路径和 cache
environments/autodl.yaml         # 服务器路径和 cache
```

训练脚本支持 `--env`：

```bash
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --env local --dry-run
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --env autodl --dry-run
```

优先级：

```text
命令行参数 > environments/*.yaml > experiments/*.yaml
```

因此服务器上通常不用再手写 `--data ... --cache ram`，直接 `--env autodl` 即可。

## 3. 服务器选择

推荐优先选：

- PyTorch 镜像。
- CUDA 12.1、12.2 或 12.4。
- 显存不低于 16GB，优先 24GB。

从当前候选看：

- `RTX 3090 24GB / 内存 90GB / PyTorch 2.5.1 / CUDA 12.4`：推荐优先选。
- `RTX 3080 Ti 12GB / 内存 90GB`：可用，但 A-P2 仍可能接近显存上限。

3090 24GB 能降低 OOM 和 CPU fallback 风险。90GB 内存下 DIOR-R 推荐 `cache=ram`，已经写入 `environments/autodl.yaml`。

开机后检查：

```bash
python - <<'PY'
import torch
print(torch.__version__)
print(torch.cuda.is_available())
print(torch.version.cuda)
print(torch.cuda.get_device_name(0))
PY
```

## 4. 服务器首次部署

建议目录：

```text
/root/autodl-tmp/ultralytics
/root/autodl-tmp/datasets/YOLODIOR-R
```

克隆代码：

```bash
cd /root/autodl-tmp
git clone https://github.com/luckg6/ultralytics.git
cd ultralytics
```

如果仓库改成私有仓库，服务器需要配置 GitHub token 或 SSH key。

首次安装：

```bash
pip install -e .
```

后续普通代码更新不需要重复执行 `pip install -e .`。只有 `pyproject.toml`、依赖列表或包入口发生变化时，才重新执行一次。

## 5. 首次准备数据和权重

数据集放到：

```text
/root/autodl-tmp/datasets/YOLODIOR-R/
```

目录应类似：

```text
YOLODIOR-R/
  train/images
  train/labels
  val/images
  val/labels
  test/images
  test/labels
```

预训练权重放到：

```text
weights/pretrained/yolo11n-obb.pt
weights/pretrained/yolo26n.pt
```

说明：

- `.pt` 权重默认被 `.gitignore` 忽略，不会通过普通 Git 同步。
- `yolo11n-obb.pt` 是实验初始化权重。
- `yolo26n.pt` 用于 Ultralytics AMP 检查，放好后服务器离线也不需要下载。
- 这一步每台服务器首次做一次即可，后续代码更新不需要重复。

## 6. 服务器自检

```bash
cd /root/autodl-tmp/ultralytics
python scripts/check_server_env.py --env autodl --require-cuda
```

如果要检查某个断点：

```bash
python scripts/check_server_env.py \
  --env autodl \
  --resume runs/obb/dior_A_p2/weights/last.pt \
  --require-cuda
```

## 7. 启动训练

先 dry-run：

```bash
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --env autodl --dry-run
```

正式训练：

```bash
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --env autodl
```

以后 B/C/AB/ABC 只换 `--config`：

```bash
python scripts/train_obb.py --config experiments/dior/b_lsk.yaml --env autodl
python scripts/train_obb.py --config experiments/dior/ab_p2_lsk.yaml --env autodl
```

如果实验配置还是 `status: planned`，脚本会拒绝训练。实现完成并 dry-run 通过后，再改为 `status: ready`。

## 8. 断点续训

使用 `--resume`，这是真正恢复 optimizer/scaler/epoch 的断点续训，不是把 `last.pt` 当成新的 pretrained。

```bash
python scripts/train_obb.py \
  --config experiments/dior/a_p2.yaml \
  --env autodl \
  --resume runs/obb/dior_A_p2/weights/last.pt
```

如果 run 路径不同，按服务器实际路径填写。

## 9. 本地改代码后如何更新服务器

本地：

```powershell
git status
git add AGENTS.md README.md SERVER_TRAINING.md scripts ultralytics experiments environments research weights/README.md
git commit -m "Update remote OBB experiment workflow"
git push origin <你的分支名>
```

服务器：

```bash
cd /root/autodl-tmp/ultralytics
git status
git pull
```

如果服务器工作区只用于训练，原则上不要在服务器上改代码。训练产生的 `runs/` 已经被忽略，不会影响 `git pull`；需要回传的权重应整理到 `weights/experiments/` 后再提交。

只有新增依赖或包配置变化时，再运行：

```bash
pip install -e .
```

## 10. 结果回传

训练结束后，建议把关键权重整理进 `weights/` 后提交 Git。当前项目允许 Git 跟踪 `weights/` 下的 `.pt` 文件；根目录临时下载的 `.pt` 仍然忽略。

至少保留这些文件：

```text
runs/.../<run_name>/weights/best.pt
runs/.../<run_name>/weights/last.pt
runs/.../<run_name>/results.csv
runs/.../<run_name>/args.yaml
runs/.../<run_name>/results.png
```

本地建议整理到：

```text
weights/experiments/<dataset>/<variant>/
experiments/logs/<dataset>/
```

服务器上也可以直接整理并提交：

```bash
mkdir -p weights/experiments/dior/a_p2
cp runs/obb/dior_A_p2/weights/best.pt weights/experiments/dior/a_p2/best.pt
cp runs/obb/dior_A_p2/weights/last.pt weights/experiments/dior/a_p2/last.pt
git add weights/experiments/dior/a_p2
git commit -m "Add DIOR A-P2 weights"
git push
```

写论文表格前记录：

- Git commit。
- 实验 YAML。
- 环境 YAML。
- 模型 YAML。
- 初始化权重。
- 数据集 YAML。
- cache 策略。
- batch、imgsz、epochs、seed。
- best.pt 路径。
- 全尺度 mAP 和小目标 mAP。

## 11. 不再推荐的方案

`scripts/prepare_server_package.py` 仍保留为无 Git 或网络异常时的兜底工具，但常规开发不要再优先使用 zip 打包更新代码。
