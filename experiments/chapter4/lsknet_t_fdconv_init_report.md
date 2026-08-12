# LSKNet-T Hybrid Initialization Report

- Generated: `2026-08-10T18:06:47`
- Model YAML: `ultralytics\cfg\models\11\remote_obb\yolo11n-obb-lsknet-t-fdconv.yaml`
- Output checkpoint: `weights\pretrained\lsknet\yolo11n_obb_lsknet_t_fdconv_hybrid_init.pt`

## Stage Outputs

| Stage | Shape with 640x640 input |
|---|---|
| C2 | `(1, 32, 160, 160)` |
| C3 | `(1, 64, 80, 80)` |
| C4 | `(1, 160, 40, 40)` |
| C5 | `(1, 256, 20, 20)` |

## Model Size

- Layers: 439
- Params: 5,832,118
- Gradients: 5,832,102
- GFLOPs at 640: 19.2

## Weight Loading

- YOLO layer mapping: `{9: 9, 10: 10, 13: 14, 16: 17, 17: 18, 19: 20, 20: 21, 22: 23, 23: 24}`
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

- `model.11.branch_norm`
- `model.11.dw3`
- `model.11.dw5`
- `model.11.dw7`
- `model.11.freq_channel`
- `model.11.freq_router`
- `model.11.gamma`
- `model.11.reduce`
- `model.11.restore`
- `model.11.spatial_gate`
- `model.24.cv3`
- `model.5.bn`
- `model.5.conv`
- `model.6.branch_norm`
- `model.6.dw3`
- `model.6.dw5`
- `model.6.dw7`
- `model.6.freq_channel`
- `model.6.freq_router`
- `model.6.gamma`
- `model.6.reduce`
- `model.6.restore`
- `model.6.spatial_gate`
- `model.7.bn`
- `model.7.conv`
- `model.8.branch_norm`
- `model.8.dw3`
- `model.8.dw5`
- `model.8.dw7`
- `model.8.freq_channel`
- `model.8.freq_router`
- `model.8.gamma`
- `model.8.reduce`
- `model.8.restore`
- `model.8.spatial_gate`
