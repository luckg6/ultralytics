# Git 工作流：本地 Codex 开发 + 服务器训练

长期方案不再推荐反复手动打包 zip。推荐方式是：本地 Codex 改代码并提交到 Git，服务器只负责 `git pull` 更新代码和运行训练。`pip install -e .` 只需要首次部署时执行；editable 安装后，后续 `git pull` 的源码改动会直接生效，除非新增了依赖。

如果服务器没有 conda，准备用 Python `venv`，按 `SERVER_VENV_SETUP.md` 操作。该文档包含 venv 创建、PyTorch 安装、本仓库 `pip install -e .`、自检、训练和结果回传流程。

当前你的服务器根目录是 `/home/ws`，因此优先使用：

```bash
python scripts/check_server_env.py --env homews --require-cuda
python scripts/train_obb.py --config experiments/dior/c_dynamic.yaml --env homews --dry-run
python scripts/train_obb.py --config experiments/dior/c_dynamic.yaml --env homews
```

对应数据集配置是 `ultralytics/cfg/datasets/DIOR-homews.yaml`，数据集应放在 `/home/ws/datasets/YOLODIOR-R/`。

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
environments/company5090.yaml    # 公司 5090 服务器路径和 cache
```

训练脚本支持 `--env`：

```bash
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --env local --dry-run
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --env autodl --dry-run
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --env company5090 --dry-run
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

- `weights/` 下的 `.pt` 允许 Git 跟踪，可以通过 Git 同步。
- `yolo11n-obb.pt` 是实验初始化权重。
- `yolo26n.pt` 用于 Ultralytics AMP 检查，放好后服务器离线也不需要下载。
- 如果公司服务器不能从 Git 拉到权重，再手动放一次即可。

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

本地 8GB 显存如果 batch=16 频繁 OOM，可以在中断后用较小 batch 续训：

```bash
python scripts/train_obb.py \
  --config experiments/dior/a_p2.yaml \
  --env local \
  --resume runs/obb/runs/obb/dior_A_p2/weights/last.pt \
  --batch 4
```

当前项目已经决定后续正式主实验统一使用 `batch=4`。如果当前 A-P2 run 是从较大 batch 中途改成 batch=4 的，它可以作为组会阶段结果；最终论文主表建议 baseline/A/B/C/AB/ABC 都从头按 batch=4 跑。

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

## 10. 公司 5090 和本机交替训练

这个方案可行：公司 5090 工作日每天跑 2 小时，结束后提交 `last.pt`；本机晚上或周末拉取 `last.pt` 继续训练。

前提：

- 两边代码处在同一个 Git commit，至少不要在同一个实验中途换未提交的代码。
- 两边 DIOR-R split、标签和类别顺序完全一致。
- 两边都使用同一个实验配置，例如 `experiments/dior/a_p2.yaml`。
- 尽量固定 batch。当前主实验统一为 `batch=4`，公司 5090 和本机接力时也保持一致。

公司 5090 首次准备：

```bash
cd /data
git clone https://github.com/luckg6/ultralytics.git
cd ultralytics
pip install -e .
python scripts/check_server_env.py --env company5090 --require-cuda
```

公司 5090 接力训练：

```bash
git pull
python scripts/train_obb.py \
  --config experiments/dior/a_p2.yaml \
  --env company5090 \
  --resume weights/experiments/dior/a_p2/last.pt
```

如果是第一次在公司 5090 上跑，还没有 `weights/experiments/dior/a_p2/last.pt`，就从头启动：

```bash
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --env company5090
```

每次训练结束后，把最新 checkpoint 整理进 Git 跟踪目录：

```bash
mkdir -p weights/experiments/dior/a_p2
cp runs/obb/dior_A_p2/weights/best.pt weights/experiments/dior/a_p2/best.pt
cp runs/obb/dior_A_p2/weights/last.pt weights/experiments/dior/a_p2/last.pt
git add weights/experiments/dior/a_p2
git commit -m "Update DIOR A-P2 checkpoint"
git push
```

本机接力：

```powershell
git pull
python scripts/train_obb.py `
  --config experiments/dior/a_p2.yaml `
  --env local `
  --resume weights/experiments/dior/a_p2/last.pt
```

如果本机显存吃紧：

```powershell
python scripts/train_obb.py `
  --config experiments/dior/a_p2.yaml `
  --env local `
  --resume weights/experiments/dior/a_p2/last.pt `
  --batch 4
```

注意：频繁交替机器本身没有问题，`last.pt` 包含 optimizer、scaler、epoch 等训练状态。但如果中途频繁改变 batch，严格论文实验要在日志里记录；最终正式结果最好固定同一套训练参数重跑。

## 11. 结果回传

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

## 12. 已废弃的方案

不再使用 zip 打包更新服务器代码。常规流程固定为本地 `git push`，服务器 `git pull`。
