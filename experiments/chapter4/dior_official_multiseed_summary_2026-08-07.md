# Chapter 4 DIOR-R Official Three-Seed Summary

Date: 2026-08-07

Seeds: `42`, `3407`, `2026`.

The seed-42 values come from the existing single-seed evaluation records. The seed-3407 and seed-2026 values come from `experiments/chapter4/dior_official_multiseed_eval_2026-08-07.csv`.

## Per-Seed Results

Accuracy values are percentages.

| Seed | Variant | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---|---:|---:|---:|---:|
| 42 | Baseline | 73.72 | 56.88 | 27.69 | 18.15 |
| 42 | FDF | 73.59 | 56.92 | 29.33 | 19.47 |
| 42 | OAC | 74.02 | 56.75 | 29.62 | 19.47 |
| 42 | OAC+FDF | 74.26 | 57.37 | 29.67 | 19.59 |
| 3407 | Baseline | 73.83 | 56.94 | 27.91 | 18.26 |
| 3407 | FDF | 73.76 | 56.96 | 29.20 | 19.23 |
| 3407 | OAC | 73.91 | 56.90 | 29.05 | 19.09 |
| 3407 | OAC+FDF | 73.17 | 56.43 | 29.20 | 19.34 |
| 2026 | Baseline | 73.27 | 56.50 | 29.14 | 18.99 |
| 2026 | FDF | 73.55 | 56.62 | 29.14 | 18.82 |
| 2026 | OAC | 73.63 | 56.82 | 29.09 | 19.29 |
| 2026 | OAC+FDF | 73.62 | 56.91 | 29.76 | 19.59 |

## Mean and Std

The table reports mean +/- population standard deviation over the three seeds.

| Variant | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---:|---:|---:|---:|
| Baseline | 73.61 +/- 0.24 | 56.77 +/- 0.20 | 28.25 +/- 0.64 | 18.47 +/- 0.37 |
| FDF | 73.63 +/- 0.09 | 56.84 +/- 0.15 | 29.22 +/- 0.08 | 19.17 +/- 0.27 |
| OAC | 73.85 +/- 0.17 | 56.82 +/- 0.06 | 29.25 +/- 0.26 | 19.28 +/- 0.15 |
| OAC+FDF | 73.68 +/- 0.45 | 56.90 +/- 0.39 | 29.54 +/- 0.25 | 19.51 +/- 0.12 |

## Delta vs LSKNet-T Baseline Mean

| Variant | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---:|---:|---:|---:|
| FDF | +0.02 | +0.06 | +0.98 | +0.70 |
| OAC | +0.25 | +0.05 | +1.01 | +0.81 |
| OAC+FDF | +0.07 | +0.13 | +1.30 | +1.04 |

## Interpretation

The three-seed results support the small-object motivation of Chapter 4. FDF and OAC both improve the two small-object metrics on average, and OAC+FDF gives the best average small-object mAP50 and mAP50:95. The combined model also gives the best average all-object mAP50:95.

The result should not be overstated as a uniformly dominant all-scale improvement. On seed 3407, OAC+FDF drops in all-object mAP50 and mAP50:95 relative to the LSKNet-T baseline, while still improving small-object metrics. Across the three seeds, OAC alone has the best average all-object mAP50. A careful thesis statement is therefore:

> OAC+FDF provides the strongest average small-object performance and the best average mAP50:95, while OAC alone is slightly stronger for average all-object mAP50. This indicates that the two modules are useful but their interaction still has seed-dependent optimization variance.

For the next stage, keep OAC and FDF as the current C/D candidates, but avoid claiming that the combined model is strictly best on every metric and every seed.
