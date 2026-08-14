# 第四章 DIOR-R `/home/ws` 命令

更新日期：2026-08-14

固定环境：`device=1`、`batch=16`、`cache=ram`、`epochs=100`。SGC 路线的 DIOR-R official seed 42 筛选已经完成：单 SGC 成立，直接 SGC+FDF 组合不成立。当前待运行的是更温和的 `FDR-Lite` 单 D 与 `SGC+FDR-Lite` 组合筛选。

## 当前应运行

```bash
cd /home/ws/ultralytics && source .venv/bin/activate && python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdr_lite_dior_official_homews.yaml && python scripts/train_obb.py --config experiments/chapter4/lsknet_t_sgc_fdr_lite_dior_official_homews.yaml
```

训练后持久化评估：

```bash
cd /home/ws/ultralytics && source .venv/bin/activate && python scripts/evaluate_experiment_suite.py --suite experiments/chapter4/eval_sgc_fdr_lite_screen_homews.yaml
```

## SGC 筛选记录

```bash
cd /home/ws/ultralytics && source .venv/bin/activate && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_sgc_dior_official_homews.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_sgc_fdf_dior_official_homews.yaml
```

训练后执行持久化评估：

```bash
cd /home/ws/ultralytics && source .venv/bin/activate && \
python scripts/evaluate_experiment_suite.py --suite experiments/chapter4/eval_sgc_screen_homews.yaml
```

输出：

- `experiments/chapter4/dior_official_sgc_screen_eval.csv`
- `experiments/chapter4/dior_official_sgc_screen_eval.md`

若小目标评估显存不足，追加 `--small-batch 1`。

SGC seed 42 结果：单 SGC 四项指标均超过 baseline 和单 FDF；直接 SGC+FDF 四项均低于 SGC 和 FDF，因此不继续运行该组合三 seed。

## FDConv-Lite 筛选记录

```bash
cd /home/ws/ultralytics && source .venv/bin/activate && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdconv_dior_official_homews.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdconv_fdf_dior_official_homews.yaml
```

训练后执行持久化评估：

```bash
cd /home/ws/ultralytics && source .venv/bin/activate && \
python scripts/evaluate_experiment_suite.py --suite experiments/chapter4/eval_fdconv_screen_homews.yaml
```

输出：

- `experiments/chapter4/dior_official_fdconv_screen_eval.csv`
- `experiments/chapter4/dior_official_fdconv_screen_eval.md`

若小目标评估显存不足，追加 `--small-batch 1`。

后续新增网络时，复制并修改 `eval_fdconv_screen_homews.yaml` 中的 `experiments` 列表即可；通用脚本会从训练配置的 `name` 自动寻找 `runs/obb/<name>/weights/best.pt`，不需要再为每个组合新增 Python 脚本。

FDConv-Lite seed 42 结果：组合模型在四项指标上均低于单 FDF，也低于单 FDConv-Lite，因此不继续运行三 seed。

## 已完成，不再重复运行

以下三 seed 组已经完成：

- Baseline、FDF、OAC、OAC+FDF；
- OAC+FDF-Blend 稳健组合。
- FDConv-Lite、FDConv-Lite+FDF seed 42 筛选。
- SGC、SGC+FDF seed 42 筛选。
- FDR-Lite、SGC+FDR-Lite seed 42 筛选配置已生成，结果待训练后补充。

它们的配置继续保留用于追溯，但不是当前待运行任务。结果入口：

- `dior_official_multiseed_summary_2026-08-07.md`
- `dior_official_multiseed_eval_2026-08-07.md`
- `dior_official_multiseed_blend_eval_2026-08-07.md`

OAC+FDF 的组合 All mAP50 三 seed 均值只比 baseline 高 `0.07`，Blend 也没有稳定优于单模块，因此两条路线均停止扩展。
