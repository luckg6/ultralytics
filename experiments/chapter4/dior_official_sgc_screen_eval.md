# Chapter 4 DIOR-R SGC Screening Evaluation

- Generated: `2026-08-14T10:06:56`
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
| DIOR-R | 42 | SGC | 73.92 | 57.35 | 29.62 | 19.79 |
| DIOR-R | 42 | SGC+FDF | 73.38 | 56.68 | 28.81 | 18.91 |

## Screening Note

SGC is the strongest single-module Chapter 4 candidate so far under seed 42. Compared with the LSKNet-T baseline, it improves all-object mAP50/mAP50:95 by `0.23/0.48` points and small-object mAP50/mAP50:95 by `1.93/1.64` points. It also exceeds single FDF on all four reported metrics.

The direct SGC+FDF combination is not valid in this form. It is lower than SGC and FDF on all four metrics, suggesting that the strip-guided geometry calibration and current FDF top-down frequency gate interact destructively when both are inserted simultaneously. Keep SGC as the current C candidate, but do not expand this direct SGC+FDF combination to three seeds.
