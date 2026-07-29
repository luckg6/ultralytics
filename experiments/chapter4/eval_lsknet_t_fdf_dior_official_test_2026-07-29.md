# LSKNet-T + FDF DIOR-R Official Test Evaluation

Date: 2026-07-29

## Command

```bash
C:\F\Anaconda\envs\yololuck\python.exe scripts\evaluate_obb.py --model runs/obb/dior_official_lsknet_t_fdf/weights/best.pt --data ultralytics/cfg/datasets/DIOR-official.yaml --split test --mode both --imgsz 640 --device 0 --workers 0
```

## Run

- Train run: `runs/obb/dior_official_lsknet_t_fdf/`
- Checkpoint: `runs/obb/dior_official_lsknet_t_fdf/weights/best.pt`
- Model YAML: `ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-fdf.yaml`
- Train config: `experiments/chapter4/lsknet_t_fdf_dior_official_homews.yaml`
- Server training settings: `device=1`, `batch=16`, `cache=ram`, `epochs=100`, `seed=42`

## Model Size

The evaluation script reports:

- Params: 5,757,591
- GFLOPs: 18.7

The initialization dry-run report before training reports 5.794M parameters and 19.0 GFLOPs. The small difference is caused by the Ultralytics loaded-checkpoint summary format; use the evaluation-script values when comparing evaluated checkpoints.

## Test Metrics

| Model | Params (M) | GFLOPs | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---:|---:|---:|---:|---:|---:|
| LSKNet-T baseline | 5.728 | 18.7 | 73.72 | 56.88 | 27.69 | 18.15 |
| LSKNet-T + FDF | 5.758 | 18.7 | 73.59 | 56.92 | 29.33 | 19.47 |

## Delta vs LSKNet-T Baseline

| Metric | Delta |
|---|---:|
| Params | +0.030M |
| GFLOPs | +0.0 |
| All mAP50 | -0.13 |
| All mAP50:95 | +0.04 |
| Small mAP50 | +1.64 |
| Small mAP50:95 | +1.32 |

## Interpretation

FDF is positive for small-object detection on DIOR-R official: both small-object metrics improve clearly over the LSKNet-T baseline. The all-object mAP50:95 also increases slightly, but all-object mAP50 drops by 0.13 points. Therefore, FDF is a promising Chapter 4 D candidate, but it is not yet a fully dominant single-module improvement.

This result supports the frequency-detail fusion direction, especially for the small-object weakness exposed by the LSKNet-T baseline. The next step should either add an orientation-aware C module to recover all-scale mAP50 while preserving the small-object gains, or make a slightly stronger FDF-plus variant if C is not ready.
