# Chapter 4 DIOR-R FDConv-Lite Screening Evaluation

- Generated: `2026-08-13T11:11:16`
- Data: `ultralytics/cfg/datasets/DIOR-official-homews.yaml`
- Split: `test`
- Image size: `640`
- Device: `1`
- Workers: `8`
- Small-object rule: `wh < 1024 px^2`

| Dataset | Seed | Variant | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---:|---|---:|---:|---:|---:|
| DIOR-R | 42 | Baseline | 73.68 | 56.87 | 27.69 | 18.14 |
| DIOR-R | 42 | FDF | 73.60 | 56.92 | 29.31 | 19.47 |
| DIOR-R | 42 | FDConv-Lite | 73.41 | 56.80 | 28.94 | 19.05 |
| DIOR-R | 42 | FDConv-Lite+FDF | 73.28 | 56.53 | 28.77 | 18.92 |

## Screening Note

FDConv-Lite and FDConv-Lite+FDF do not meet the Chapter 4 screening target under seed 42. Compared with the LSKNet-T baseline, FDConv-Lite reduces all-object mAP50/mAP50:95 by `0.27/0.06` points while improving small-object mAP50/mAP50:95 by `1.25/0.91` points. FDConv-Lite+FDF further drops all-object mAP50/mAP50:95 by `0.41/0.34` points and is lower than both single FDF and single FDConv-Lite on all four reported metrics. This direction is therefore kept as a screening record rather than expanded to three seeds.
