# LSKNet-T + OAC + FDF DIOR-R Official Test Evaluation

Date: 2026-08-03

## Command

All-object evaluation:

```bash
C:\F\Anaconda\envs\yololuck\python.exe scripts\evaluate_obb.py --model runs/obb/dior_official_lsknet_t_oac_fdf/weights/best.pt --data ultralytics/cfg/datasets/DIOR-official.yaml --split test --mode all --imgsz 640 --device 0 --workers 0
```

Small-object evaluation was run separately with `batch=1` because the local RTX 4060 hit memory limits when all-object and small-object evaluation were executed back-to-back:

```bash
C:\F\Anaconda\envs\yololuck\python.exe -c "<small-only evaluation with batch=1>"
```

Raw logs:

- `experiments/chapter4/eval_lsknet_t_oac_fdf_all_precise_2026-08-04.log`
- `experiments/chapter4/eval_lsknet_t_oac_fdf_raw_2026-08-03.log` (first all-object pass plus small-pass OOM record)
- `experiments/chapter4/eval_lsknet_t_oac_fdf_small_raw_2026-08-03.log`

## Run

- Train run: `runs/obb/dior_official_lsknet_t_oac_fdf/`
- Checkpoint: `runs/obb/dior_official_lsknet_t_oac_fdf/weights/best.pt`
- Model YAML: `ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-oac-fdf.yaml`
- Train config: `experiments/chapter4/lsknet_t_oac_fdf_dior_official_homews.yaml`
- Server training settings: `device=1`, `batch=16`, `cache=ram`, `epochs=100`, `seed=42`
- Best validation epoch by `metrics/mAP50-95(B)`: epoch 100
- Best validation metrics: `mAP50=0.82197`, `mAP50:95=0.66789`

## Model Size

The evaluation script reports:

- Params: 5,842,159
- GFLOPs: 18.9

## Test Metrics

Accuracy values are percentages.

| Model | Params (M) | GFLOPs | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---:|---:|---:|---:|---:|---:|
| LSKNet-T baseline | 5.728 | 18.7 | 73.72 | 56.88 | 27.69 | 18.15 |
| LSKNet-T + FDF | 5.758 | 18.7 | 73.59 | 56.92 | 29.33 | 19.47 |
| LSKNet-T + OAC | 5.813 | 18.9 | 74.02 | 56.75 | 29.62 | 19.47 |
| LSKNet-T + OAC + FDF | 5.842 | 18.9 | 74.26 | 57.37 | 29.67 | 19.59 |

## Delta vs LSKNet-T Baseline

| Metric | Delta |
|---|---:|
| Params | +0.114M |
| GFLOPs | +0.2 |
| All mAP50 | +0.54 |
| All mAP50:95 | +0.49 |
| Small mAP50 | +1.98 |
| Small mAP50:95 | +1.44 |

## Interpretation

The combined OAC+FDF model is the first Chapter 4 candidate that improves all four DIOR-R official test metrics over the LSKNet-T baseline. OAC mainly restores all-object mAP50 and orientation-sensitive responses, while FDF supplies fine-detail fusion gains in the top-down neck. Their combination also recovers the all-object mAP50:95 drop observed in the single OAC experiment.

This result supports keeping OAC and FDF as the current C/D pair for the next stage. The next decision should be whether to run the second dataset and multi-seed validation directly, or first inspect qualitative examples to confirm that the gains are not driven by a narrow subset of classes.
