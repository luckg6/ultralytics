# LSKNet-T Baseline Initialization Report

- Generated: `2026-07-28T16:04:27`
- Model YAML: `ultralytics\cfg\models\11\remote_obb\yolo11n-obb-lsknet-t-baseline.yaml`
- Output checkpoint: `weights\pretrained\lsknet\yolo11n_obb_lsknet_t_hybrid_init.pt`

## Stage Outputs

| Stage | Shape with 640x640 input |
|---|---|
| C2 | `(1, 32, 160, 160)` |
| C3 | `(1, 64, 80, 80)` |
| C4 | `(1, 160, 40, 40)` |
| C5 | `(1, 256, 20, 20)` |

## Model Size

- Layers: 376
- Params: 5,763,985
- Gradients: 5,763,969
- GFLOPs at 640: 18.9

## Weight Loading

- DOTA checkpoint: `weights\pretrained\lsknet\lsk_t_fpn_1x_dota_le90_20230206-3ccee254.pth`
- DOTA `backbone.*` keys considered: 478
- DOTA backbone keys loaded: 478
- DOTA backbone keys skipped: 0
- DOTA loaded tensor parameters: 3,997,644
- YOLO11n-OBB checkpoint: `weights\pretrained\yolo11n-obb.pt`
- YOLO neck/head keys considered: 355
- YOLO neck/head keys loaded: 304
- YOLO neck/head keys skipped: 51
- YOLO loaded tensor parameters: 1,676,219
- YOLO skipped prefixes: `model.23.cv3.0`, `model.23.cv3.1`, `model.23.cv3.2`

## Randomly Initialized Module Prefixes

- `model.21.cv3`
- `model.5.bn`
- `model.5.conv`
- `model.6.bn`
- `model.6.conv`
