"""Evaluate an OBB model on all objects and/or small objects.

Examples:
    python scripts/evaluate_obb.py
    python scripts/evaluate_obb.py --model weights/baselines/dior-r/yolo11n-obb-dior-r-best.pt --data DIOR.yaml
    python scripts/evaluate_obb.py --model path/to/best.pt --data DOTAv1.yaml --mode all
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a YOLO OBB model.")
    parser.add_argument(
        "--model",
        default="weights/baselines/dior-r/yolo11n-obb-dior-r-best.pt",
        help="Path to model weights.",
    )
    parser.add_argument("--data", default="DIOR.yaml", help="Dataset YAML, for example DIOR.yaml or DOTAv1.yaml.")
    parser.add_argument("--split", default="test", help="Dataset split to evaluate: val or test.")
    parser.add_argument("--device", default="0", help="Device passed to Ultralytics, for example 0 or cpu.")
    parser.add_argument("--workers", type=int, default=0, help="Number of dataloader workers.")
    parser.add_argument(
        "--mode",
        choices=("all", "small", "both"),
        default="both",
        help="Evaluate all objects, small objects, or both.",
    )
    return parser.parse_args()


def run_eval(model, args: argparse.Namespace, small_only: bool):
    os.environ["EVAL_SMALL_ONLY"] = "1" if small_only else "0"
    label = "small objects (area < 1024)" if small_only else "all objects"

    print("\n" + "=" * 60)
    print(f"Evaluating {Path(args.model)} on {args.data} [{args.split}], {label}")
    print("=" * 60)

    return model.val(data=args.data, split=args.split, device=args.device, workers=args.workers)


def print_metrics(name: str, metrics) -> None:
    print(f"{name} mAP50:    {metrics.box.map50:.4f}")
    print(f"{name} mAP50-95: {metrics.box.map:.4f}")


def main() -> None:
    args = parse_args()

    from ultralytics import YOLO

    model = YOLO(args.model)

    metrics_all = None
    metrics_small = None

    if args.mode in {"all", "both"}:
        metrics_all = run_eval(model, args, small_only=False)

    if args.mode in {"small", "both"}:
        metrics_small = run_eval(model, args, small_only=True)

    print("\n" + "=" * 60)
    print("Evaluation summary")
    print("=" * 60)
    if metrics_all is not None:
        print_metrics("All", metrics_all)
    if metrics_small is not None:
        print_metrics("Small", metrics_small)


if __name__ == "__main__":
    main()
