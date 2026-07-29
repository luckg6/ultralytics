# LSKNet-T Baseline DIOR-R Official Test Evaluation

Date: 2026-07-29

## Run

- Run directory: `runs/obb/dior_official_lsknet_t_baseline/`
- Model: `ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-baseline.yaml`
- Weight: `runs/obb/dior_official_lsknet_t_baseline/weights/best.pt`
- Data: `ultralytics/cfg/datasets/DIOR-official.yaml`
- Split: `test`
- Image size: `640`
- Evaluation command:

```bash
python scripts/evaluate_obb.py --model runs/obb/dior_official_lsknet_t_baseline/weights/best.pt --data ultralytics/cfg/datasets/DIOR-official.yaml --split test --mode both --imgsz 640 --device 0 --workers 0
```

## Training Summary

- Server training args recorded in `args.yaml`: `device=1`, `batch=16`, `cache=ram`, `epochs=100`, `seed=42`.
- Best validation epoch by `metrics/mAP50-95(B)`: epoch 99.
- Best validation metrics:
  - precision: 0.86207
  - recall: 0.76854
  - mAP50: 0.82330
  - mAP50-95: 0.66724
- Last epoch validation metrics:
  - mAP50: 0.82316
  - mAP50-95: 0.66710

## Test Results

| Model | Params (M) | GFLOPs | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---:|---:|---:|---:|---:|---:|
| YOLO11n-OBB baseline | 2.658 | 6.6 | 71.11 | 54.31 | 27.32 | 17.96 |
| LSKNet-T baseline | 5.728 | 18.7 | 73.72 | 56.88 | 27.69 | 18.15 |

## Delta vs YOLO11n-OBB Baseline

| Metric | Delta |
|---|---:|
| Params | +3.070 M |
| GFLOPs | +12.1 |
| All mAP50 | +2.61 |
| All mAP50:95 | +2.57 |
| Small mAP50 | +0.37 |
| Small mAP50:95 | +0.19 |

## Interpretation

The pure LSKNet-T backbone baseline has been successfully integrated and trained with the YOLO11n-OBB neck/head. Its all-object metrics are higher than the YOLO11n-OBB baseline under this protocol, but the model is also much larger and more expensive, so this result should not be used to claim that LSKNet-T is fairly superior to the native YOLO11 backbone. Compared with the Chapter 3 A+B model, it has higher all-object mAP but lower small-object mAP, exposing a useful Chapter 4 design space rather than a strict cross-chapter win.

This result is a baseline for Chapter 4 only. It does not include Chapter 3 FSPB/LPCF and should not be reported as a new innovation by itself. Subsequent C/D modules should first be judged by their controlled improvements over this LSKNet-T baseline.
