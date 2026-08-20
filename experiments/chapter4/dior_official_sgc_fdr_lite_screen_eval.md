# Chapter 4 DIOR-R SGC + FDR-Lite Screening Evaluation

- Generated: `2026-08-20T14:45:56`
- Data: `ultralytics/cfg/datasets/DIOR-official-homews.yaml`
- Split: `test`
- Image size: `640`
- Device: `1`
- Workers: `8`
- Small-object rule: `wh < 1024 px^2`

| Dataset | Seed | Variant | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---:|---|---:|---:|---:|---:|
| DIOR-R | 42 | Baseline | 73.68 | 56.87 | 27.69 | 18.14 |
| DIOR-R | 42 | SGC | 73.92 | 57.35 | 29.62 | 19.79 |
| DIOR-R | 42 | FDR-Lite | 73.93 | 56.83 | 28.77 | 18.91 |
| DIOR-R | 42 | SGC+FDR-Lite | 73.73 | 56.91 | 29.02 | 19.23 |

## Screening Note

FDR-Lite is milder than the direct FDF neck replacement and gives the highest All mAP50 by a negligible `0.01` point over SGC. However, it is lower than SGC on All mAP50:95 and both small-object metrics. The combined SGC+FDR-Lite model also fails to exceed SGC on all four metrics. This route is therefore retained as a screening record rather than expanded to three seeds.
