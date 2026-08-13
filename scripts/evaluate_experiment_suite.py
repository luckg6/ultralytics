"""Evaluate a configurable set of OBB experiment checkpoints.

The script is intentionally generic: a suite YAML or a list of training
configs is enough to resolve ``runs/obb/<name>/weights/best.pt``, evaluate
all objects and small objects, and persist both CSV and Markdown summaries.

Examples:
    python scripts/evaluate_experiment_suite.py --suite experiments/chapter4/eval_fdconv_screen_homews.yaml
    python scripts/evaluate_experiment_suite.py --configs experiments/chapter4/lsknet_t_fdconv_dior_official_homews.yaml
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@dataclass
class EvalItem:
    dataset: str
    seed: str
    variant: str
    weights: tuple[Path, ...]
    config: Path | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", help="Evaluation suite YAML with defaults and experiments.")
    parser.add_argument("--configs", nargs="*", help="Training config YAML files to evaluate.")
    parser.add_argument("--weights", nargs="*", help="Explicit checkpoints to evaluate when no training config is used.")
    parser.add_argument("--variants", nargs="*", help="Variant names for --weights entries.")
    parser.add_argument("--dataset", default="DIOR-R", help="Dataset label used for --configs/--weights rows.")
    parser.add_argument("--data", help="Override dataset YAML passed to Ultralytics validation.")
    parser.add_argument("--split", help="Override dataset split.")
    parser.add_argument("--imgsz", type=int, help="Override evaluation image size.")
    parser.add_argument("--device", help="Override evaluation device.")
    parser.add_argument("--workers", type=int, help="Override dataloader workers.")
    parser.add_argument("--project", help="Override Ultralytics validation output project.")
    parser.add_argument("--out", help="Output stem for .csv and .md summaries.")
    parser.add_argument("--batch", type=int, help="Optional validation batch size for all-object evaluation.")
    parser.add_argument("--small-batch", type=int, help="Optional validation batch size for small-object evaluation.")
    parser.add_argument("--skip-missing", action="store_true", help="Skip missing checkpoints instead of failing.")
    parser.add_argument("--dry-run", action="store_true", help="Only print resolved checkpoints.")
    return parser.parse_args()


def resolve(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def load_yaml(path: str | Path) -> dict[str, Any]:
    import yaml

    with resolve(path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def config_to_item(config_path: str | Path, default_dataset: str) -> EvalItem:
    path = resolve(config_path)
    cfg = load_yaml(path)
    run_name = cfg.get("name")
    if not run_name:
        raise ValueError(f"Training config has no 'name': {path}")
    variant = str(cfg.get("variant") or run_name)
    seed = str(cfg.get("seed", ""))
    dataset = str(cfg.get("dataset_label") or default_dataset)
    return EvalItem(
        dataset=dataset,
        seed=seed,
        variant=variant,
        weights=(ROOT / "runs" / "obb" / str(run_name) / "weights" / "best.pt",),
        config=path,
    )


def suite_to_items(suite: dict[str, Any], default_dataset: str) -> list[EvalItem]:
    items = []
    for entry in suite.get("experiments", []):
        config = entry.get("config")
        weights = [resolve(p) for p in entry.get("weights", [])]

        cfg: dict[str, Any] = {}
        config_path = resolve(config) if config else None
        if config_path is not None:
            cfg = load_yaml(config_path)
            run_name = entry.get("run_name") or cfg.get("name")
            if run_name:
                weights.append(ROOT / "runs" / "obb" / str(run_name) / "weights" / "best.pt")
        elif entry.get("run_name"):
            weights.append(ROOT / "runs" / "obb" / str(entry["run_name"]) / "weights" / "best.pt")

        if not weights:
            raise ValueError(f"Evaluation entry has no config, run_name, or weights: {entry}")

        items.append(
            EvalItem(
                dataset=str(entry.get("dataset") or cfg.get("dataset_label") or default_dataset),
                seed=str(entry.get("seed") or cfg.get("seed", "")),
                variant=str(
                    entry.get("variant")
                    or cfg.get("variant")
                    or entry.get("run_name")
                    or (config_path.stem if config_path is not None else weights[0].stem)
                ),
                weights=tuple(weights),
                config=config_path,
            )
        )
    return items


def explicit_weights_to_items(args: argparse.Namespace) -> list[EvalItem]:
    variants = args.variants or []
    items = []
    for index, weight in enumerate(args.weights or []):
        path = resolve(weight)
        variant = variants[index] if index < len(variants) else path.parents[1].name if len(path.parents) > 1 else path.stem
        items.append(EvalItem(dataset=args.dataset, seed="", variant=variant, weights=(path,)))
    return items


def first_existing(paths: tuple[Path, ...]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def val(model, args: argparse.Namespace, item: EvalItem, small_only: bool):
    os.environ["EVAL_SMALL_ONLY"] = "1" if small_only else "0"
    kind = "small" if small_only else "all"
    name_parts = [item.dataset, item.seed, item.variant, kind]
    safe_name = "_".join(part for part in name_parts if part).lower().replace("+", "_").replace("/", "_")
    kwargs: dict[str, Any] = {
        "data": args.data,
        "split": args.split,
        "imgsz": args.imgsz,
        "device": args.device,
        "workers": args.workers,
        "project": args.project,
        "name": safe_name,
        "exist_ok": True,
    }
    if small_only and args.small_batch is not None:
        kwargs["batch"] = args.small_batch
    elif not small_only and args.batch is not None:
        kwargs["batch"] = args.batch
    return model.val(**kwargs)


def pct(x: float) -> float:
    return round(float(x) * 100.0, 4)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["dataset", "seed", "variant", "all_map50", "all_map50_95", "small_map50", "small_map50_95", "weight"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, rows: list[dict[str, object]], args: argparse.Namespace, title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {title}",
        "",
        f"- Generated: `{datetime.now().isoformat(timespec='seconds')}`",
        f"- Data: `{args.data}`",
        f"- Split: `{args.split}`",
        f"- Image size: `{args.imgsz}`",
        f"- Device: `{args.device}`",
        f"- Workers: `{args.workers}`",
        f"- Small-object rule: `wh < 1024 px^2`",
        "",
        "| Dataset | Seed | Variant | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['dataset']} | {row['seed']} | {row['variant']} | "
            f"{row['all_map50']:.2f} | {row['all_map50_95']:.2f} | "
            f"{row['small_map50']:.2f} | {row['small_map50_95']:.2f} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def apply_defaults(args: argparse.Namespace, suite: dict[str, Any]) -> tuple[argparse.Namespace, str]:
    defaults = suite.get("defaults", {})
    args.data = args.data or defaults.get("data") or "ultralytics/cfg/datasets/DIOR-official-homews.yaml"
    args.split = args.split or defaults.get("split") or "test"
    args.imgsz = args.imgsz or int(defaults.get("imgsz", 640))
    args.device = args.device or str(defaults.get("device", "1"))
    args.workers = args.workers if args.workers is not None else int(defaults.get("workers", 8))
    args.project = args.project or defaults.get("project") or "runs/obb/experiment_suite_eval"
    if args.batch is None and defaults.get("batch") is not None:
        args.batch = int(defaults["batch"])
    if args.small_batch is None and defaults.get("small_batch") is not None:
        args.small_batch = int(defaults["small_batch"])
    if args.out is None:
        args.out = defaults.get("out") or f"experiments/eval_suite_{datetime.now():%Y-%m-%d}"
    return args, str(suite.get("title") or "OBB Experiment Suite Evaluation")


def main() -> None:
    args = parse_args()
    suite = load_yaml(args.suite) if args.suite else {}
    args, title = apply_defaults(args, suite)

    items: list[EvalItem] = []
    if suite:
        items.extend(suite_to_items(suite, args.dataset))
    if args.configs:
        items.extend(config_to_item(config, args.dataset) for config in args.configs)
    if args.weights:
        items.extend(explicit_weights_to_items(args))
    if not items:
        raise ValueError("No experiments to evaluate. Use --suite, --configs, or --weights.")

    resolved: list[tuple[EvalItem, Path]] = []
    missing: list[EvalItem] = []
    for item in items:
        checkpoint = first_existing(item.weights)
        if checkpoint is None:
            missing.append(item)
        else:
            resolved.append((item, checkpoint))

    if missing and not args.skip_missing:
        details = []
        for item in missing:
            details.append(f"- {item.variant}: " + ", ".join(str(path) for path in item.weights))
        raise FileNotFoundError("Missing checkpoint(s):\n" + "\n".join(details))

    if args.dry_run:
        for item, checkpoint in resolved:
            print(f"{item.dataset} seed={item.seed} variant={item.variant}: {checkpoint}")
        if missing:
            print(f"Skipped missing: {len(missing)}")
        return

    from ultralytics import YOLO

    out_stem = resolve(args.out)
    rows: list[dict[str, object]] = []
    for item, checkpoint in resolved:
        print("\n" + "=" * 80)
        print(f"Evaluating dataset={item.dataset}, seed={item.seed}, variant={item.variant}")
        print(f"Checkpoint: {checkpoint}")
        print("=" * 80)
        model = YOLO(str(checkpoint))
        metrics_all = val(model, args, item, small_only=False)
        metrics_small = val(model, args, item, small_only=True)
        rows.append(
            {
                "dataset": item.dataset,
                "seed": item.seed,
                "variant": item.variant,
                "all_map50": pct(metrics_all.box.map50),
                "all_map50_95": pct(metrics_all.box.map),
                "small_map50": pct(metrics_small.box.map50),
                "small_map50_95": pct(metrics_small.box.map),
                "weight": str(checkpoint),
            }
        )
        write_csv(out_stem.with_suffix(".csv"), rows)
        write_md(out_stem.with_suffix(".md"), rows, args, title)
        print(f"Persisted partial summary to {out_stem.with_suffix('.csv')}")

    print("\nDone.")
    print(f"CSV: {out_stem.with_suffix('.csv')}")
    print(f"MD:  {out_stem.with_suffix('.md')}")


if __name__ == "__main__":
    main()
