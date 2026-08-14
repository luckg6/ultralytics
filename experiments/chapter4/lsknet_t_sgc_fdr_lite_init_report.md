# LSKNet-T Hybrid Initialization Report

- Generated: `2026-08-14T10:33:45`
- Model YAML: `ultralytics\cfg\models\11\remote_obb\yolo11n-obb-lsknet-t-sgc-fdr-lite.yaml`
- Output checkpoint: `weights\pretrained\lsknet\yolo11n_obb_lsknet_t_sgc_fdr_lite_hybrid_init.pt`

## Stage Outputs

| Stage | Shape with 640x640 input |
|---|---|
| C2 | `(1, 32, 160, 160)` |
| C3 | `(1, 64, 80, 80)` |
| C4 | `(1, 160, 40, 40)` |
| C5 | `(1, 256, 20, 20)` |

## Model Size

- Layers: 517
- Params: 5,894,546
- Gradients: 5,894,530
- GFLOPs at 640: 19.4

## Weight Loading

- YOLO layer mapping: `{9: 11, 10: 12, 13: 17, 16: 20, 17: 21, 19: 23, 20: 24, 22: 26, 23: 27}`
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

- `model.10.channel_gate`
- `model.10.context`
- `model.10.gamma`
- `model.10.local`
- `model.10.reduce`
- `model.10.restore`
- `model.10.spatial_gate`
- `model.13.branch_norm`
- `model.13.channel_gate`
- `model.13.gamma`
- `model.13.local`
- `model.13.reduce`
- `model.13.restore`
- `model.13.router`
- `model.13.spatial_gate`
- `model.13.strip_hv`
- `model.13.strip_vh`
- `model.14.channel_gate`
- `model.14.context`
- `model.14.gamma`
- `model.14.local`
- `model.14.reduce`
- `model.14.restore`
- `model.14.spatial_gate`
- `model.27.cv3`
- `model.5.bn`
- `model.5.conv`
- `model.6.branch_norm`
- `model.6.channel_gate`
- `model.6.gamma`
- `model.6.local`
- `model.6.reduce`
- `model.6.restore`
- `model.6.router`
- `model.6.spatial_gate`
- `model.6.strip_hv`
- `model.6.strip_vh`
- `model.7.channel_gate`
- `model.7.context`
- `model.7.gamma`
- `model.7.local`
- `model.7.reduce`
- `model.7.restore`
- `model.7.spatial_gate`
- `model.8.bn`
- `model.8.conv`
- `model.9.branch_norm`
- `model.9.channel_gate`
- `model.9.gamma`
- `model.9.local`
- `model.9.reduce`
- `model.9.restore`
- `model.9.router`
- `model.9.spatial_gate`
- `model.9.strip_hv`
- `model.9.strip_vh`
