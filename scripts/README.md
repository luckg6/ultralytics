# 脚本入口

当前只保留与遥感 OBB 实验直接相关的通用脚本。

```text
scripts/
  train_obb.py          # 统一训练入口，读取 experiments/ 和 environments/
  evaluate_obb.py       # 统一评估入口，支持全尺度和小目标评估
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
