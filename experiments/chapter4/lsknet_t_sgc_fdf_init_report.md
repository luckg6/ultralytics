# LSKNet-T Hybrid Initialization Report

- Generated: `2026-08-13T11:34:34`
- Model YAML: `ultralytics\cfg\models\11\remote_obb\yolo11n-obb-lsknet-t-sgc-fdf.yaml`
- Output checkpoint: `weights\pretrained\lsknet\yolo11n_obb_lsknet_t_sgc_fdf_hybrid_init.pt`

## Stage Outputs

| Stage | Shape with 640x640 input |
|---|---|
| C2 | `(1, 32, 160, 160)` |
| C3 | `(1, 64, 80, 80)` |
| C4 | `(1, 160, 40, 40)` |
| C5 | `(1, 256, 20, 20)` |

## Model Size

- Layers: 481
- Params: 5,864,272
- Gradients: 5,864,256
- GFLOPs at 640: 19.2

## Weight Loading

- YOLO layer mapping: `{9: 9, 10: 10, 13: 13, 16: 15, 17: 16, 19: 18, 20: 19, 22: 21, 23: 22}`
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
- `model.11.channel_gate`
- `model.11.gamma`
- `model.11.local`
- `model.11.reduce`
- `model.11.restore`
- `model.11.router`
- `model.11.spatial_gate`
- `model.11.strip_hv`
- `model.11.strip_vh`
- `model.12.deep_gate`
- `model.12.deep_scale`
- `model.12.detail_gate`
- `model.12.detail_scale`
- `model.12.lateral_channel`
- `model.14.deep_gate`
- `model.14.deep_scale`
- `model.14.detail_gate`
- `model.14.detail_scale`
- `model.14.lateral_channel`
- `model.22.cv3`
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
- `model.7.bn`
- `model.7.conv`
- `model.8.branch_norm`
- `model.8.channel_gate`
- `model.8.gamma`
- `model.8.local`
- `model.8.reduce`
- `model.8.restore`
- `model.8.router`
- `model.8.spatial_gate`
- `model.8.strip_hv`
- `model.8.strip_vh`
