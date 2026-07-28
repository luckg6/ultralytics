# 给服务器端 Claude Code 的说明

当前服务器安装和训练步骤已经合并到 [SERVER_VENV_SETUP.md](SERVER_VENV_SETUP.md)。

接手时请先确认：

1. 仓库位于 `/home/ws/ultralytics`。
2. 使用 venv，并已执行 `pip install -e .`。
3. `python -c "import ultralytics; print(ultralytics.__file__)"` 指向 `/home/ws/ultralytics/ultralytics/`。
4. DIOR-R official 数据位于 `/home/ws/datasets/YOLODIOR-R-official/`。
5. HRSID-derived OBB 数据位于 `/home/ws/datasets/HRSID-YOLO/`。
6. 小论文主结果以 `paper/ippr2026/main.pdf` 为准，不使用旧 8:1:1 DIOR-R 结果覆盖。

旧版 Claude 安装长文档已归档到 `paper/archive/md_cleanup_20260728/CLAUDE_SERVER_SETUP.md`，其中包含的 `YOLODIOR-R` 旧路径、`batch=4` 和 C-Dynamic 示例不再作为当前操作依据。
