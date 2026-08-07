# Chapter 4 DIOR-R Official Multi-Seed Commands

This file lists the `/home/ws` commands for completing DIOR-R official multi-seed validation of the Chapter 4 LSKNet-T route.

Fixed settings:

- Dataset: `ultralytics/cfg/datasets/DIOR-official-homews.yaml`
- Seeds: `42`, `3407`, `2026`
- Current v2 ablation variants: baseline, FDF, OAC, OAC+FDF-Blend.
- Configs below use `batch=16`, `device=1`, `cache=ram`, `epochs=100`.
- The seed-42 configs use `s42` run names to avoid overwriting earlier unsuffixed seed-42 runs.

## One-Shot Command: OAC+FDF-Blend Three-Seed Ablation

```bash
cd /home/ws/ultralytics && source .venv/bin/activate && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_baseline_dior_official_homews_s42.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdf_dior_official_homews_s42.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_dior_official_homews_s42.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_fdf_blend_dior_official_homews_s42.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_baseline_dior_official_homews_s3407.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdf_dior_official_homews_s3407.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_dior_official_homews_s3407.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_fdf_blend_dior_official_homews_s3407.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_baseline_dior_official_homews_s2026.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdf_dior_official_homews_s2026.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_dior_official_homews_s2026.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_fdf_blend_dior_official_homews_s2026.yaml
```

If you only want to reuse existing baseline/FDF/OAC runs from seed 3407 and 2026, run the three Blend-only configs:

```bash
cd /home/ws/ultralytics && source .venv/bin/activate && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_fdf_blend_dior_official_homews_s42.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_fdf_blend_dior_official_homews_s3407.yaml && \
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_fdf_blend_dior_official_homews_s2026.yaml
```

## Seed 42

```bash
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_baseline_dior_official_homews_s42.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdf_dior_official_homews_s42.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_dior_official_homews_s42.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_fdf_blend_dior_official_homews_s42.yaml
```

## Seed 3407

```bash
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_baseline_dior_official_homews_s3407.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdf_dior_official_homews_s3407.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_dior_official_homews_s3407.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_fdf_blend_dior_official_homews_s3407.yaml
```

## Seed 2026

```bash
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_baseline_dior_official_homews_s2026.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdf_dior_official_homews_s2026.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_dior_official_homews_s2026.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_fdf_blend_dior_official_homews_s2026.yaml
```

After training, use the persistent evaluation wrapper so mAP values are written to CSV and Markdown:

```bash
python scripts/evaluate_chapter4_multiseed.py --combo blend --data ultralytics/cfg/datasets/DIOR-official-homews.yaml --split test --imgsz 640 --device 1 --workers 8
```

It writes:

- `experiments/chapter4/dior_official_multiseed_blend_eval_2026-08-07.csv`
- `experiments/chapter4/dior_official_multiseed_blend_eval_2026-08-07.md`

If GPU memory is insufficient for small-object evaluation, add `--small-batch 1`.
