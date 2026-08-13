# 脚本入口

当前只保留与遥感 OBB 实验直接相关的通用脚本。

```text
scripts/
  train_obb.py          # 统一训练入口，读取 experiments/ 和 environments/
  evaluate_obb.py       # 统一评估入口，支持全尺度和小目标评估
  evaluate_experiment_suite.py # 通用批量评估入口，读取评估清单或训练配置
  check_server_env.py   # 本地/服务器环境自检
```

本地显存不足时，可以在 resume 时临时覆盖 batch。示例：

```bash
python scripts/train_obb.py --config experiments/dior_official/ab_p2_pki_lite.yaml --resume runs/obb/<run-name>/weights/last.pt --batch 4
```

注意：这类覆盖适合临时续训或排查 OOM。复现当前论文表格时，应按 `paper/ippr2026/main.pdf` 中的固定协议执行。

不要再新增只改一两个硬编码路径的训练脚本。新增实验优先新增或更新：

```text
experiments/<dataset>/<variant>.yaml
ultralytics/cfg/models/11/remote_obb/<model>.yaml
environments/<env>.yaml
```

批量评估同理，不要再新增写死某个组合名的专用脚本。新增筛选方向时优先新增或更新：

```text
experiments/<chapter>/<eval_suite>.yaml
```

然后运行：

```bash
python scripts/evaluate_experiment_suite.py --suite experiments/chapter4/eval_fdconv_screen_homews.yaml
```

脚本会优先使用清单中显式列出的权重路径，并自动从训练配置的 `name` 推导
`runs/obb/<name>/weights/best.pt`，最后持久化生成同名 `.csv` 和 `.md`。
