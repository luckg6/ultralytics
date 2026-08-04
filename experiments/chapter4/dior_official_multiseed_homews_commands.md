# Chapter 4 DIOR-R Official Multi-Seed Commands

This file lists the `/home/ws` commands for completing DIOR-R official multi-seed validation of the Chapter 4 LSKNet-T route.

Fixed settings:

- Dataset: `ultralytics/cfg/datasets/DIOR-official-homews.yaml`
- Seeds: `42`, `3407`, `2026`
- Existing seed-42 runs: `dior_official_lsknet_t_baseline`, `dior_official_lsknet_t_fdf`, `dior_official_lsknet_t_oac`, `dior_official_lsknet_t_oac_fdf`
- New configs below use `batch=16`, `device=1`, `cache=ram`, `epochs=100`.

## Seed 3407

```bash
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_baseline_dior_official_homews_s3407.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdf_dior_official_homews_s3407.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_dior_official_homews_s3407.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_fdf_dior_official_homews_s3407.yaml
```

## Seed 2026

```bash
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_baseline_dior_official_homews_s2026.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdf_dior_official_homews_s2026.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_dior_official_homews_s2026.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_oac_fdf_dior_official_homews_s2026.yaml
```

After training, evaluate all eight new checkpoints on the official test split with `scripts/evaluate_obb.py --split test --mode both`. If local GPU memory is insufficient for small-object evaluation, run all-object and small-object evaluation separately and use `batch=1` for the small-object pass.
