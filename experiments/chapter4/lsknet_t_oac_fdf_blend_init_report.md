# LSKNet-T Hybrid Initialization Report

- Generated: `2026-08-07T15:56:09`
- Model YAML: `ultralytics\cfg\models\11\remote_obb\yolo11n-obb-lsknet-t-oac-fdf-blend.yaml`
- Output checkpoint: `weights\pretrained\lsknet\yolo11n_obb_lsknet_t_oac_fdf_blend_hybrid_init.pt`

## Stage Outputs

| Stage | Shape with 640x640 input |
|---|---|
| C2 | `(1, 32, 160, 160)` |
| C3 | `(1, 64, 80, 80)` |
| C4 | `(1, 160, 40, 40)` |
| C5 | `(1, 256, 20, 20)` |

## Model Size

- Layers: 500
- Params: 6,021,731
- Gradients: 6,021,715
- GFLOPs at 640: 19.9

## Weight Loading

- YOLO layer mapping: `{9: 9, 10: 10, 13: [14, 16], 16: [20, 22], 17: 24, 19: 26, 20: 27, 22: 29, 23: 30}`
- DOTA checkpoint: `weights\pretrained\lsknet\lsk_t_fpn_1x_dota_le90_20230206-3ccee254.pth`
- DOTA `backbone.*` keys considered: 478
- DOTA backbone keys loaded: 478
- DOTA backbone keys skipped: 0
- DOTA loaded tensor parameters: 3,997,644
- YOLO11n-OBB checkpoint: `weights\pretrained\yolo11n-obb.pt`
- YOLO neck/head keys considered: 355
- YOLO neck/head keys loaded: 352
- YOLO neck/head keys skipped: 51
- YOLO loaded tensor parameters: 1,820,675
- YOLO skipped prefixes: `model.23.cv3.0`, `model.23.cv3.1`, `model.23.cv3.2`

## Randomly Initialized Module Prefixes

- `model.11.branch_norm`
- `model.11.branches`
- `model.11.channel_gate`
- `model.11.gamma`
- `model.11.local_context`
- `model.11.reduce`
- `model.11.restore`
- `model.11.routing`
- `model.11.spatial_gate`
- `model.15.deep_gate`
- `model.15.deep_scale`
- `model.15.detail_gate`
- `model.15.detail_scale`
- `model.15.lateral_channel`
- `model.17.alpha`
- `model.21.deep_gate`
- `model.21.deep_scale`
- `model.21.detail_gate`
- `model.21.detail_scale`
- `model.21.lateral_channel`
- `model.23.alpha`
- `model.30.cv3`
- `model.5.bn`
- `model.5.conv`
- `model.6.branch_norm`
- `model.6.branches`
- `model.6.channel_gate`
- `model.6.gamma`
- `model.6.local_context`
- `model.6.reduce`
- `model.6.restore`
- `model.6.routing`
- `model.6.spatial_gate`
- `model.7.bn`
- `model.7.conv`
- `model.8.branch_norm`
- `model.8.branches`
- `model.8.channel_gate`
- `model.8.gamma`
- `model.8.local_context`
- `model.8.reduce`
- `model.8.restore`
- `model.8.routing`
- `model.8.spatial_gate`
