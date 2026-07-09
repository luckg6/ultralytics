# 运行环境配置

`experiments/` 记录实验本身，例如模型结构、训练轮数、batch、imgsz、seed。

`environments/` 记录机器差异，例如数据集路径、GPU 编号、cache 策略、dataloader workers。

这样本地和服务器可以跑同一个实验配置，只在命令里切换环境：

```bash
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --env local --dry-run
python scripts/train_obb.py --config experiments/dior/c_dynamic.yaml --env homews --dry-run
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --env company5090 --dry-run
```

优先级：

```text
命令行参数 > environments/*.yaml > experiments/*.yaml
```

建议不要把 `epochs`、`batch`、`imgsz`、`seed` 这类消融核心参数放进环境配置，除非明确要做训练策略实验。

当前环境：

```text
local.yaml        # 本机 RTX 4060 Laptop，默认 cache=disk
homews.yaml       # /home/ws Linux 服务器，默认 cache=ram
autodl.yaml       # AutoDL/Linux 服务器，默认 cache=ram
company5090.yaml  # 公司 RTX 5090 Linux 服务器，默认 cache=ram
```
