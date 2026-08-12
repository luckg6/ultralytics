# 第四章 DIOR-R `/home/ws` 命令

更新日期：2026-08-12

固定环境：`device=1`、`batch=16`、`cache=ram`、`epochs=100`。当前先做 FDConv-Lite 路线的 seed 42 筛选；三 seed 命令要等该组合成立后再生成，避免继续运行已经淘汰的组合。

## 当前应运行

```bash
cd /home/ws/ultralytics && source .venv/bin/activate && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdconv_dior_official_homews.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdconv_fdf_dior_official_homews.yaml
```

训练后执行持久化评估：

```bash
cd /home/ws/ultralytics && source .venv/bin/activate && \
python scripts/evaluate_chapter4_multiseed.py --combo fdconv_fdf \
  --data ultralytics/cfg/datasets/DIOR-official-homews.yaml \
  --split test --imgsz 640 --device 1 --workers 8
```

输出：

- `experiments/chapter4/dior_official_multiseed_fdconv_fdf_eval_<date>.csv`
- `experiments/chapter4/dior_official_multiseed_fdconv_fdf_eval_<date>.md`

若小目标评估显存不足，追加 `--small-batch 1`。

## 已完成，不再重复运行

以下三 seed 组已经完成：

- Baseline、FDF、OAC、OAC+FDF；
- OAC+FDF-Blend 稳健组合。

它们的配置继续保留用于追溯，但不是当前待运行任务。结果入口：

- `dior_official_multiseed_summary_2026-08-07.md`
- `dior_official_multiseed_eval_2026-08-07.md`
- `dior_official_multiseed_blend_eval_2026-08-07.md`

OAC+FDF 的组合 All mAP50 三 seed 均值只比 baseline 高 `0.07`，Blend 也没有稳定优于单模块，因此两条路线均停止扩展。
