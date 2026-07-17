"""Convert the official VEDAI-1024 release to Ultralytics YOLO-OBB format."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw


CLASS_MAP = {
    1: (0, "car"),
    2: (1, "truck"),
    4: (2, "tractor"),
    5: (3, "camping_car"),
    9: (4, "van"),
    10: (5, "other"),
    11: (6, "pickup"),
    23: (7, "boat"),
    31: (8, "plane"),
}
# Fold 10 has the class histogram closest to one tenth of the full benchmark;
# fold 2 is the next closest and is held out for checkpoint selection.
SPLIT_FOLDS = {"train": (1, 3, 4, 5, 6, 7, 8, 9), "val": (2,), "test": (10,)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("C:/E/datasets/VEDAI-1024"))
    parser.add_argument("--output", type=Path, default=Path("C:/E/datasets/VEDAI-1024-YOLO"))
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing converted dataset.")
    parser.add_argument(
        "--copy-mode",
        choices=("hardlink", "copy"),
        default="hardlink",
        help="Hard links save local disk space and remain normal files when uploaded.",
    )
    return parser.parse_args()


def read_ids(path: Path) -> list[str]:
    ids = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if any(len(image_id) != 8 or not image_id.isdigit() for image_id in ids):
        raise ValueError(f"Invalid image id in {path}")
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate image id in {path}")
    return ids


def load_official_folds(annotation_dir: Path) -> tuple[dict[int, set[str]], dict[str, list[str]]]:
    folds = {fold: set(read_ids(annotation_dir / f"fold{fold:02d}test.txt")) for fold in range(1, 11)}
    seen: set[str] = set()
    for fold, ids in folds.items():
        overlap = seen & ids
        if overlap:
            raise ValueError(f"Official test folds overlap at fold {fold}: {sorted(overlap)[:5]}")
        seen.update(ids)

    for fold in range(1, 11):
        official_train = set(read_ids(annotation_dir / f"fold{fold:02d}.txt"))
        expected_train = seen - folds[fold]
        if official_train != expected_train:
            raise ValueError(f"fold{fold:02d}.txt is not the complement of its test fold")

    split_ids = {
        split: sorted(set().union(*(folds[fold] for fold in fold_ids)))
        for split, fold_ids in SPLIT_FOLDS.items()
    }
    if set(split_ids["train"]) & set(split_ids["val"]) or set(split_ids["train"]) & set(split_ids["test"]):
        raise ValueError("Generated train/val/test splits overlap")
    return folds, split_ids


def load_annotations(path: Path) -> tuple[dict[str, list[dict]], Counter]:
    annotations: dict[str, list[dict]] = defaultdict(list)
    raw_classes: Counter = Counter()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        values = line.split()
        if len(values) != 15:
            raise ValueError(f"Expected 15 columns at {path}:{line_number}, found {len(values)}")
        image_id = values[0]
        raw_class = int(values[12])
        raw_classes[raw_class] += 1
        annotations[image_id].append(
            {
                "raw_class": raw_class,
                "points": [(float(values[4 + i]), float(values[8 + i])) for i in range(4)],
                "flags": (int(values[13]), int(values[14])),
            }
        )
    return annotations, raw_classes


def polygon_area(points: list[tuple[float, float]]) -> float:
    return abs(
        sum(
            points[i][0] * points[(i + 1) % len(points)][1]
            - points[(i + 1) % len(points)][0] * points[i][1]
            for i in range(len(points))
        )
    ) / 2


def order_clockwise(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    cx = sum(point[0] for point in points) / len(points)
    cy = sum(point[1] for point in points) / len(points)
    return sorted(points, key=lambda point: math.atan2(point[1] - cy, point[0] - cx))


def clip_polygon(points: list[tuple[float, float]], width: int, height: int) -> tuple[list[tuple[float, float]], bool]:
    clipped = [(min(max(x, 0.0), width - 1.0), min(max(y, 0.0), height - 1.0)) for x, y in points]
    changed = any(abs(a - b) > 1e-6 for before, after in zip(points, clipped) for a, b in zip(before, after))
    return order_clockwise(clipped), changed


def place_image(source: Path, destination: Path, copy_mode: str) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if copy_mode == "hardlink":
        try:
            os.link(source, destination)
            return "hardlink"
        except OSError:
            pass
    shutil.copy2(source, destination)
    return "copy"


def prepare_output(source: Path, output: Path, overwrite: bool) -> None:
    source = source.resolve()
    output = output.resolve()
    if output == source or source in output.parents or output in source.parents:
        raise ValueError("Source and output must be separate, non-nested directories")
    if output.exists():
        if not overwrite:
            raise FileExistsError(f"Output already exists: {output}. Use --overwrite to replace it.")
        shutil.rmtree(output)
    output.mkdir(parents=True)


def draw_preview(output: Path, preview: tuple[str, str, list[tuple[int, list[tuple[float, float]]]]]) -> None:
    split, image_id, labels = preview
    image_path = output / "images" / split / f"{image_id}.png"
    with Image.open(image_path).convert("RGB") as image:
        draw = ImageDraw.Draw(image)
        for class_id, points in labels:
            draw.line(points + [points[0]], fill=(255, 40, 40), width=3)
            draw.text(points[0], CLASS_MAP[next(raw for raw, mapped in CLASS_MAP.items() if mapped[0] == class_id)][1], fill=(255, 255, 0))
        image.save(output / "conversion_preview.jpg", quality=92)


def convert(args: argparse.Namespace) -> dict:
    source = args.source.resolve()
    output = args.output.resolve()
    annotation_dir = source / "Annotations1024"
    image_dir = source / "Vehicules1024"
    required = [annotation_dir / "annotation1024.txt", image_dir]
    if any(not path.exists() for path in required):
        raise FileNotFoundError(f"Incomplete VEDAI-1024 source under {source}")

    prepare_output(source, output, args.overwrite)
    folds, split_ids = load_official_folds(annotation_dir)
    annotations, raw_classes = load_annotations(annotation_dir / "annotation1024.txt")
    report = {
        "source": str(source),
        "output": str(output),
        "modality": "color (_co.png)",
        "split_protocol": "official folds 01,03-09=train, fold02=val, fold10=test",
        "class_map": {str(raw): {"id": mapped[0], "name": mapped[1]} for raw, mapped in CLASS_MAP.items()},
        "raw_class_counts": dict(sorted(raw_classes.items())),
        "ignored_raw_classes": {},
        "splits": {},
        "clipped_boxes": 0,
        "discarded_boxes": 0,
        "image_transfer": Counter(),
    }
    preview_candidates: list[tuple[int, str, str, list[tuple[int, list[tuple[float, float]]]]]] = []

    selected_ids = set().union(*(set(ids) for ids in split_ids.values()))
    for raw_class, count in raw_classes.items():
        if raw_class not in CLASS_MAP:
            report["ignored_raw_classes"][str(raw_class)] = count

    for split, image_ids in split_ids.items():
        class_counts: Counter = Counter()
        small_counts: Counter = Counter()
        object_count = 0
        empty_images = 0
        for image_id in image_ids:
            source_image = image_dir / f"{image_id}_co.png"
            if not source_image.exists():
                raise FileNotFoundError(source_image)
            with Image.open(source_image) as image:
                width, height = image.size
            if (width, height) != (1024, 1024):
                raise ValueError(f"Unexpected image size {width}x{height}: {source_image}")

            transfer = place_image(source_image, output / "images" / split / f"{image_id}.png", args.copy_mode)
            report["image_transfer"][transfer] += 1
            converted: list[tuple[int, list[tuple[float, float]]]] = []
            lines: list[str] = []
            for annotation in annotations.get(image_id, []):
                raw_class = annotation["raw_class"]
                if raw_class not in CLASS_MAP:
                    continue
                class_id, class_name = CLASS_MAP[raw_class]
                points, changed = clip_polygon(annotation["points"], width, height)
                if changed:
                    report["clipped_boxes"] += 1
                area = polygon_area(points)
                if area <= 1.0:
                    report["discarded_boxes"] += 1
                    continue
                normalized = [(x / width, y / height) for x, y in points]
                coords = " ".join(f"{value:.6f}" for point in normalized for value in point)
                lines.append(f"{class_id} {coords}")
                converted.append((class_id, points))
                class_counts[class_name] += 1
                object_count += 1
                if area * (640 / width) * (640 / height) < 1024:
                    small_counts[class_name] += 1

            label_path = output / "labels" / split / f"{image_id}.txt"
            label_path.parent.mkdir(parents=True, exist_ok=True)
            label_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="ascii")
            if not lines:
                empty_images += 1
            preview_candidates.append((len(lines), split, image_id, converted))

        report["splits"][split] = {
            "folds": list(SPLIT_FOLDS[split]),
            "images": len(image_ids),
            "objects": object_count,
            "empty_images": empty_images,
            "class_counts": dict(class_counts),
            "small_objects_at_imgsz640": sum(small_counts.values()),
            "small_class_counts_at_imgsz640": dict(small_counts),
        }

    unselected_annotations = set(annotations) - selected_ids
    report["unselected_annotated_images"] = len(unselected_annotations)
    report["official_fold_images"] = len(set().union(*folds.values()))
    report["image_transfer"] = dict(report["image_transfer"])
    (output / "conversion_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="ascii")

    _, split, image_id, labels = max(preview_candidates, key=lambda item: item[0])
    draw_preview(output, (split, image_id, labels))
    return report


def main() -> None:
    args = parse_args()
    report = convert(args)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
