"""Evaluate Chapter 4 DIOR-R multi-seed checkpoints and persist metrics.

This wrapper avoids losing the mAP summary printed by Ultralytics validation.
It evaluates all objects and small objects separately for each checkpoint,
then writes both CSV and Markdown summaries.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


RUNS_FDCONV_FDF = [
    (
        "42",
        "Baseline",
        (
            "weights/checkpoints/chapter4/dior_official/seed42/baseline/best.pt",
            "runs/obb/dior_official_lsknet_t_baseline/weights/best.pt",
        ),
    ),
    (
        "42",
        "FDF",
        (
            "weights/checkpoints/chapter4/dior_official/seed42/fdf/best.pt",
            "runs/obb/dior_official_lsknet_t_fdf/weights/best.pt",
        ),
    ),
    ("42", "FDConv-Lite", ("runs/obb/dior_official_lsknet_t_fdconv/weights/best.pt",)),
    ("42", "FDConv-Lite+FDF", ("runs/obb/dior_official_lsknet_t_fdconv_fdf/weights/best.pt",)),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="ultralytics/cfg/datasets/DIOR-official-homews.yaml")
    parser.add_argument("--split", default="test")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="1")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--project", default="runs/obb/chapter4_multiseed_eval")
    parser.add_argument("--out", default=None)
    parser.add_argument("--combo", choices=("fdconv_fdf",), default="fdconv_fdf")
    parser.add_argument("--small-batch", type=int, default=None, help="Optional batch size for small-object eval.")
    return parser.parse_args()


def resolve(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def resolve_checkpoint(candidates: tuple[str, ...]) -> Path:
    """Use the local checkpoint archive first, then the original server run path."""
    paths = [resolve(candidate) for candidate in candidates]
    for path in paths:
        if path.exists():
            return path
    formatted = "\n".join(f"  - {path}" for path in paths)
    raise FileNotFoundError(f"Missing checkpoint; checked:\n{formatted}")


def val(model, args: argparse.Namespace, seed: str, variant: str, small_only: bool):
    os.environ["EVAL_SMALL_ONLY"] = "1" if small_only else "0"
    kind = "small" if small_only else "all"
    kwargs = {
        "data": args.data,
        "split": args.split,
        "imgsz": args.imgsz,
        "device": args.device,
        "workers": args.workers,
        "project": args.project,
        "name": f"{seed}_{variant.lower().replace('+', '_')}_{kind}",
        "exist_ok": True,
    }
    if small_only and args.small_batch is not None:
        kwargs["batch"] = args.small_batch
    return model.val(**kwargs)


def pct(x: float) -> float:
    return round(float(x) * 100.0, 4)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, rows: list[dict[str, object]], args: argparse.Namespace) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Chapter 4 DIOR-R Official Multi-Seed Evaluation",
        "",
        f"- Generated: `{datetime.now().isoformat(timespec='seconds')}`",
        f"- Data: `{args.data}`",
        f"- Split: `{args.split}`",
        f"- Image size: `{args.imgsz}`",
        f"- Device: `{args.device}`",
        f"- Workers: `{args.workers}`",
        "",
        "| Seed | Variant | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['seed']} | {row['variant']} | {row['all_map50']:.2f} | {row['all_map50_95']:.2f} | "
            f"{row['small_map50']:.2f} | {row['small_map50_95']:.2f} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    if args.out is None:
        args.out = f"experiments/chapter4/dior_official_multiseed_fdconv_fdf_eval_{datetime.now():%Y-%m-%d}"
    out_stem = resolve(args.out)
    runs = RUNS_FDCONV_FDF

    from ultralytics import YOLO

    rows = []
    for seed, variant, candidates in runs:
        weight_path = resolve_checkpoint(candidates)

        print("\n" + "=" * 80)
        print(f"Evaluating seed={seed}, variant={variant}, weight={weight_path}")
        print("=" * 80)
        model = YOLO(str(weight_path))
        metrics_all = val(model, args, seed, variant, small_only=False)
        metrics_small = val(model, args, seed, variant, small_only=True)
        row = {
            "seed": seed,
            "variant": variant,
            "all_map50": pct(metrics_all.box.map50),
            "all_map50_95": pct(metrics_all.box.map),
            "small_map50": pct(metrics_small.box.map50),
            "small_map50_95": pct(metrics_small.box.map),
            "weight": str(weight_path),
        }
        rows.append(row)
        write_csv(out_stem.with_suffix(".csv"), rows)
        write_md(out_stem.with_suffix(".md"), rows, args)
        print(f"Persisted partial summary to {out_stem.with_suffix('.csv')}")

    print("\nDone.")
    print(f"CSV: {out_stem.with_suffix('.csv')}")
    print(f"MD:  {out_stem.with_suffix('.md')}")


if __name__ == "__main__":
    main()
