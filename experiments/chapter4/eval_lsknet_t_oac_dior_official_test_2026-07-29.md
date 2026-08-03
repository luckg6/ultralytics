# LSKNet-T + OAC DIOR-R Official Test Evaluation

Date: 2026-07-29

## Command

```bash
C:\F\Anaconda\envs\yololuck\python.exe scripts\evaluate_obb.py --model runs/obb/dior_official_lsknet_t_oac/weights/best.pt --data ultralytics/cfg/datasets/DIOR-official.yaml --split test --mode both --imgsz 640 --device 0 --workers 0
```

## Run

- Train run: `runs/obb/dior_official_lsknet_t_oac/`
- Checkpoint: `runs/obb/dior_official_lsknet_t_oac/weights/best.pt`
- Model YAML: `ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-oac.yaml`
- Train config: `experiments/chapter4/lsknet_t_oac_dior_official_homews.yaml`
- Server training settings: `device=1`, `batch=16`, `cache=ram`, `epochs=100`, `seed=42`

## Model Size

The evaluation script reports:

- Params: 5,812,565
- GFLOPs: 18.9

## Test Metrics

| Model | Params (M) | GFLOPs | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---:|---:|---:|---:|---:|---:|
| LSKNet-T baseline | 5.728 | 18.7 | 73.72 | 56.88 | 27.69 | 18.15 |
| LSKNet-T + FDF | 5.758 | 18.7 | 73.59 | 56.92 | 29.33 | 19.47 |
| LSKNet-T + OAC | 5.813 | 18.9 | 74.02 | 56.75 | 29.62 | 19.47 |

## Delta vs LSKNet-T Baseline

| Metric | Delta |
|---|---:|
| Params | +0.085M |
| GFLOPs | +0.2 |
| All mAP50 | +0.30 |
| All mAP50:95 | -0.13 |
| Small mAP50 | +1.93 |
| Small mAP50:95 | +1.32 |

## Interpretation

OAC is positive for DIOR-R official mAP50 and small-object detection. It improves all-object mAP50 by 0.30 points and small-object mAP50 / mAP50:95 by 1.93 / 1.32 points over the LSKNet-T baseline. However, all-object mAP50:95 decreases by 0.13 points, so OAC is not yet a four-metric dominant single-module improvement.

Compared with FDF, OAC recovers and exceeds all-object mAP50 while matching FDF on small-object mAP50:95. The next useful experiment is the combined C+D model, because OAC and FDF improve different parts of the metric profile.
