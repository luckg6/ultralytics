# 服务器训练说明

当前服务器训练说明已经合并到 [SERVER_VENV_SETUP.md](SERVER_VENV_SETUP.md)。

旧版本文档包含早期 DIOR-R 8:1:1、A-P2、C-Dynamic 和 `batch=4` 时代的操作说明，已归档到 `paper/archive/md_cleanup_20260728/SERVER_TRAINING.md`。后续请不要按旧文档复现小论文主实验。

快速原则：

- 论文主实验看 `experiments/dior_official/` 和 `experiments/hrsid/`。
- 第四章 `/home/ws` 新增实验统一 `device=1`、`batch=16`、`cache=ram`；旧配置中的 `batch=-1` 仅用于历史复现。
- 复现论文表格时按 `paper/ippr2026/main.pdf`：DIOR-R official 使用 batch 32，HRSID-derived OBB 使用 batch 8。
- 所有模型从同一个官方参考 checkpoint 独立起训，不从 A/B 的 `best.pt` 拼接续训。
