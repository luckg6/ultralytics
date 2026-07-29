"""Prepare a hybrid LSKNet-T + YOLO11n-OBB initialization checkpoint.

The Chapter 4 baseline uses an LSKNet-T backbone with the original YOLO11n-OBB
neck and OBB head. This script builds that model, loads official LSKNet-T DOTA
backbone weights into layer 0, maps compatible YOLO11n-OBB neck/head weights by
layer index, leaves channel adapters randomly initialized, and writes a small
audit report.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_MODEL = "ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-baseline.yaml"
DEFAULT_DOTA = "weights/pretrained/lsknet/lsk_t_fpn_1x_dota_le90_20230206-3ccee254.pth"
DEFAULT_YOLO = "weights/pretrained/yolo11n-obb.pt"
DEFAULT_OUT = "weights/pretrained/lsknet/yolo11n_obb_lsknet_t_hybrid_init.pt"
DEFAULT_REPORT = "experiments/chapter4/lsknet_t_baseline_init_report.md"

YOLO_TO_LSK_YOLO_LAYERS = {
    9: 7,  # SPPF
    10: 8,  # C2PSA
    13: 11,  # top-down P5->P4 C3k2
    16: 14,  # top-down P4->P3 C3k2
    17: 15,  # PAN P3->P4 downsample
    19: 17,  # PAN P4 C3k2
    20: 18,  # PAN P4->P5 downsample
    22: 20,  # PAN P5 C3k2
    23: 21,  # OBB head
}

YOLO_TO_LSK_FDF_LAYERS = {
    9: 7,  # SPPF
    10: 8,  # C2PSA
    13: 10,  # top-down P5->P4 C3k2 after FDF
    16: 12,  # top-down P4->P3 C3k2 after FDF
    17: 13,  # PAN P3->P4 downsample
    19: 15,  # PAN P4 C3k2
    20: 16,  # PAN P4->P5 downsample
    22: 18,  # PAN P5 C3k2
    23: 19,  # OBB head
}


def resolve(path: str | Path) -> Path:
    """Resolve a repository-relative or absolute path."""
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Chapter 4 model YAML path.")
    parser.add_argument("--dota", default=DEFAULT_DOTA, help="Official LSKNet-T DOTA checkpoint.")
    parser.add_argument("--yolo", default=DEFAULT_YOLO, help="YOLO11n-OBB pretrained checkpoint.")
    parser.add_argument("--out", default=DEFAULT_OUT, help="Output hybrid initialization checkpoint.")
    parser.add_argument("--report", default=DEFAULT_REPORT, help="Markdown audit report path.")
    return parser.parse_args()


def tensor_params(state_dict: dict[str, torch.Tensor]) -> int:
    """Count tensor parameters in a state dict-like mapping."""
    return sum(v.numel() for v in state_dict.values() if torch.is_tensor(v))


def trusted_torch_load(path: Path) -> dict:
    """Load trusted local checkpoints across PyTorch 2.1-2.6+ defaults."""
    try:
        return torch.load(path, map_location="cpu", weights_only=False)
    except TypeError:
        return torch.load(path, map_location="cpu")


def load_lsk_backbone(target: dict[str, torch.Tensor], dota_path: Path) -> tuple[dict[str, torch.Tensor], list[str], list[str]]:
    """Map official DOTA ``backbone.*`` keys into Ultralytics ``model.0.*`` keys."""
    ckpt = trusted_torch_load(dota_path)
    source = ckpt.get("state_dict", ckpt)
    mapped, skipped = {}, []
    for key, value in source.items():
        if not key.startswith("backbone.") or not torch.is_tensor(value):
            continue
        new_key = "model.0." + key.removeprefix("backbone.")
        if new_key in target and target[new_key].shape == value.shape:
            mapped[new_key] = value
        else:
            skipped.append(key)
    return mapped, skipped, [k for k in source if k.startswith("backbone.")]


def choose_yolo_mapping(model_path: Path) -> dict[int, int]:
    """Choose the compatible YOLO11 layer-index mapping for a Chapter 4 model."""
    return YOLO_TO_LSK_FDF_LAYERS if "fdf" in model_path.stem else YOLO_TO_LSK_YOLO_LAYERS


def load_yolo_neck_head(
    target: dict[str, torch.Tensor], yolo_path: Path, layer_mapping: dict[int, int]
) -> tuple[dict[str, torch.Tensor], list[str], list[str]]:
    """Map compatible YOLO11n-OBB neck/head layers into the LSKNet baseline."""
    ckpt = trusted_torch_load(yolo_path)
    source_model = ckpt["model"] if isinstance(ckpt, dict) and "model" in ckpt else ckpt
    source = source_model.float().state_dict()
    mapped, skipped, considered = {}, [], []
    for key, value in source.items():
        if not key.startswith("model.") or not torch.is_tensor(value):
            continue
        parts = key.split(".", 2)
        if len(parts) < 3 or not parts[1].isdigit():
            continue
        old_layer = int(parts[1])
        if old_layer not in layer_mapping:
            continue
        considered.append(key)
        new_key = f"model.{layer_mapping[old_layer]}.{parts[2]}"
        if new_key in target and target[new_key].shape == value.shape:
            mapped[new_key] = value
        else:
            skipped.append(key)
    return mapped, skipped, considered


def summarize_random_layers(target: dict[str, torch.Tensor], loaded_keys: set[str]) -> list[str]:
    """Return module prefixes that remain randomly initialized."""
    prefixes = set()
    for key, value in target.items():
        if torch.is_tensor(value) and key not in loaded_keys and not key.endswith("num_batches_tracked"):
            parts = key.split(".")
            prefixes.add(".".join(parts[:3]) if len(parts) >= 3 else key)
    return sorted(prefixes)


def summarize_prefixes(keys: list[str]) -> list[str]:
    """Summarize state-dict keys by the first few module-name components."""
    prefixes = set()
    for key in keys:
        parts = key.split(".")
        prefixes.add(".".join(parts[:4]) if len(parts) >= 4 else key)
    return sorted(prefixes)


def main() -> None:
    """Build the model, load hybrid weights, save checkpoint, and write report."""
    args = parse_args()
    model_path = resolve(args.model)
    dota_path = resolve(args.dota)
    yolo_path = resolve(args.yolo)
    out_path = resolve(args.out)
    report_path = resolve(args.report)

    for label, path in {"model": model_path, "dota": dota_path, "yolo": yolo_path}.items():
        if not path.exists():
            raise FileNotFoundError(f"{label} path does not exist: {path}")

    from ultralytics import YOLO

    yolo = YOLO(str(model_path))
    model = yolo.model
    target = model.state_dict()

    lsk_mapped, lsk_skipped, lsk_considered = load_lsk_backbone(target, dota_path)
    layer_mapping = choose_yolo_mapping(model_path)
    yolo_mapped, yolo_skipped, yolo_considered = load_yolo_neck_head(target, yolo_path, layer_mapping)
    merged = {**lsk_mapped, **yolo_mapped}
    model.load_state_dict(merged, strict=False)

    dummy = torch.zeros(1, 3, 640, 640)
    with torch.no_grad():
        lsk_outs = model.model[0](dummy)
    stage_summary = [(i + 1, tuple(x.shape)) for i, x in enumerate(lsk_outs)]
    layers, params, gradients, gflops = model.info(verbose=True, imgsz=640)

    random_prefixes = summarize_random_layers(target, set(merged))
    skipped_yolo_prefixes = summarize_prefixes(yolo_skipped)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    ckpt = {
        "date": datetime.now().isoformat(timespec="seconds"),
        "model": deepcopy(model).float(),
        "train_args": {
            "model": str(model_path.relative_to(ROOT)),
            "task": "obb",
            "source": "LSKNet-T DOTA backbone + YOLO11n-OBB compatible neck/head",
        },
    }
    torch.save(ckpt, out_path)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = [
        "# LSKNet-T Hybrid Initialization Report",
        "",
        f"- Generated: `{datetime.now().isoformat(timespec='seconds')}`",
        f"- Model YAML: `{model_path.relative_to(ROOT)}`",
        f"- Output checkpoint: `{out_path.relative_to(ROOT)}`",
        "",
        "## Stage Outputs",
        "",
        "| Stage | Shape with 640x640 input |",
        "|---|---|",
    ]
    report.extend(f"| C{stage + 1} | `{shape}` |" for stage, shape in stage_summary)
    report.extend(
        [
            "",
            "## Model Size",
            "",
            f"- Layers: {layers}",
            f"- Params: {params:,}",
            f"- Gradients: {gradients:,}",
            f"- GFLOPs at 640: {gflops:.1f}",
            "",
            "## Weight Loading",
            "",
            f"- YOLO layer mapping: `{layer_mapping}`",
            f"- DOTA checkpoint: `{dota_path.relative_to(ROOT)}`",
            f"- DOTA `backbone.*` keys considered: {len(lsk_considered)}",
            f"- DOTA backbone keys loaded: {len(lsk_mapped)}",
            f"- DOTA backbone keys skipped: {len(lsk_skipped)}",
            f"- DOTA loaded tensor parameters: {tensor_params(lsk_mapped):,}",
            f"- YOLO11n-OBB checkpoint: `{yolo_path.relative_to(ROOT)}`",
            f"- YOLO neck/head keys considered: {len(yolo_considered)}",
            f"- YOLO neck/head keys loaded: {len(yolo_mapped)}",
            f"- YOLO neck/head keys skipped: {len(yolo_skipped)}",
            f"- YOLO loaded tensor parameters: {tensor_params(yolo_mapped):,}",
            f"- YOLO skipped prefixes: {', '.join(f'`{p}`' for p in skipped_yolo_prefixes) if skipped_yolo_prefixes else 'None'}",
            "",
            "## Randomly Initialized Module Prefixes",
            "",
        ]
    )
    report.extend(f"- `{prefix}`" for prefix in random_prefixes)
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"Saved hybrid checkpoint: {out_path}")
    print(f"Wrote report: {report_path}")
    print(f"Loaded LSK backbone keys: {len(lsk_mapped)}/{len(lsk_considered)}")
    print(f"Loaded YOLO neck/head keys: {len(yolo_mapped)}/{len(yolo_considered)}")


if __name__ == "__main__":
    main()
