"""Convert the official HRSID JPG release from COCO instance masks to YOLO-OBB."""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import shutil
from collections import Counter, defaultdict
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw


CLASS_NAME = "ship"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("C:/E/datasets/HRSID/HRSID_JPG"))
    parser.add_argument("--output", type=Path, default=Path("C:/E/datasets/HRSID-YOLO"))
    parser.add_argument("--val-fraction", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--copy-mode", choices=("hardlink", "copy"), default="hardlink")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def scene_ids(source: Path) -> dict[str, set[str]]:
    scenes = {}
    for scene in ("inshore", "offshore"):
        data = load_json(source / "inshore_offshore" / f"{scene}.json")
        scenes[scene] = {image["file_name"] for image in data["images"]}
    if scenes["inshore"] & scenes["offshore"]:
        raise ValueError("Inshore and offshore manifests overlap")
    return scenes


def build_splits(source: Path, val_fraction: float, seed: int) -> tuple[dict[str, list[dict]], dict[str, str], dict[str, list[dict]]]:
    if not 0 < val_fraction < 0.5:
        raise ValueError("val-fraction must be between 0 and 0.5")
    train_data = load_json(source / "annotations" / "train2017.json")
    test_data = load_json(source / "annotations" / "test2017.json")
    if train_data["categories"][-1]["name"] != CLASS_NAME or test_data["categories"][-1]["name"] != CLASS_NAME:
        raise ValueError("Unexpected HRSID categories")

    train_images = {image["file_name"]: image for image in train_data["images"]}
    test_images = {image["file_name"]: image for image in test_data["images"]}
    if set(train_images) & set(test_images):
        raise ValueError("Official train and test images overlap")
    if len(train_images) != 3642 or len(test_images) != 1962:
        raise ValueError(f"Unexpected official split sizes: {len(train_images)}/{len(test_images)}")

    scenes = scene_ids(source)
    scene_by_name = {name: scene for scene, names in scenes.items() for name in names}
    if set(scene_by_name) != set(train_images) | set(test_images):
        raise ValueError("Scene manifests do not match official train/test images")

    rng = random.Random(seed)
    val_names = set()
    for scene in ("inshore", "offshore"):
        candidates = sorted(name for name in train_images if scene_by_name[name] == scene)
        rng.shuffle(candidates)
        val_names.update(candidates[: round(len(candidates) * val_fraction)])

    split_images = {
        "train": [train_images[name] for name in sorted(set(train_images) - val_names)],
        "val": [train_images[name] for name in sorted(val_names)],
        "test": [test_images[name] for name in sorted(test_images)],
    }
    annotations: dict[str, list[dict]] = defaultdict(list)
    for data in (train_data, test_data):
        filename_by_id = {image["id"]: image["file_name"] for image in data["images"]}
        for annotation in data["annotations"]:
            annotations[filename_by_id[annotation["image_id"]]].append(annotation)
    return split_images, scene_by_name, annotations


def segmentation_points(annotation: dict) -> np.ndarray:
    segmentation = annotation.get("segmentation")
    if not isinstance(segmentation, list) or not segmentation:
        raise ValueError(f"Unsupported segmentation for annotation {annotation.get('id')}")
    polygons = []
    for polygon in segmentation:
        values = np.asarray(polygon, dtype=np.float32)
        if values.size < 6 or values.size % 2:
            raise ValueError(f"Invalid polygon for annotation {annotation.get('id')}")
        polygons.append(values.reshape(-1, 2))
    return np.concatenate(polygons)


def order_clockwise(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    cx = sum(point[0] for point in points) / len(points)
    cy = sum(point[1] for point in points) / len(points)
    return sorted(points, key=lambda point: math.atan2(point[1] - cy, point[0] - cx))


def min_area_box(annotation: dict) -> list[tuple[float, float]]:
    points = segmentation_points(annotation)
    rectangle = cv2.minAreaRect(points)
    return order_clockwise([(float(x), float(y)) for x, y in cv2.boxPoints(rectangle)])


def polygon_area(points: list[tuple[float, float]]) -> float:
    return abs(
        sum(
            points[index][0] * points[(index + 1) % len(points)][1]
            - points[(index + 1) % len(points)][0] * points[index][1]
            for index in range(len(points))
        )
    ) / 2


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


def draw_preview(output: Path, candidate: tuple[int, str, str, list[list[tuple[float, float]]]]) -> None:
    _, split, filename, boxes = candidate
    with Image.open(output / "images" / split / filename).convert("RGB") as image:
        draw = ImageDraw.Draw(image)
        for points in boxes:
            draw.line(points + [points[0]], fill=(255, 40, 40), width=3)
        image.save(output / "conversion_preview.jpg", quality=92)


def convert(args: argparse.Namespace) -> dict:
    source = args.source.resolve()
    output = args.output.resolve()
    image_dir = source / "JPEGImages"
    required = [image_dir, source / "annotations" / "train2017.json", source / "annotations" / "test2017.json"]
    if any(not path.exists() for path in required):
        raise FileNotFoundError(f"Incomplete official HRSID source under {source}")

    prepare_output(source, output, args.overwrite)
    split_images, scene_by_name, annotations = build_splits(source, args.val_fraction, args.seed)
    report = {
        "source": str(source),
        "output": str(output),
        "variant": "official HRSID JPG, COCO masks converted with minimum-area rectangles",
        "class_names": [CLASS_NAME],
        "split_protocol": f"official test; {args.val_fraction:.0%} scene-stratified holdout from official train, seed={args.seed}",
        "small_object_protocol": f"letterboxed model input area < 1024 at imgsz={args.imgsz}",
        "splits": {},
        "clipped_boxes": 0,
        "discarded_boxes": 0,
        "image_transfer": Counter(),
    }
    preview_candidates = []

    for split, images in split_images.items():
        stats = Counter(images=len(images))
        scene_counts = Counter()
        manifest_lines = []
        for image_info in images:
            filename = image_info["file_name"]
            width, height = int(image_info["width"]), int(image_info["height"])
            source_image = image_dir / filename
            if not source_image.exists():
                raise FileNotFoundError(source_image)
            with Image.open(source_image) as image:
                if image.size != (width, height):
                    raise ValueError(f"Image size mismatch for {filename}: {image.size} vs {(width, height)}")
            transfer = place_image(source_image, output / "images" / split / filename, args.copy_mode)
            report["image_transfer"][transfer] += 1
            scene_counts[scene_by_name[filename]] += 1

            lines = []
            converted = []
            scale = min(args.imgsz / width, args.imgsz / height)
            for annotation in annotations.get(filename, []):
                if annotation.get("category_id") != 1 or annotation.get("iscrowd", 0):
                    raise ValueError(f"Unexpected annotation {annotation.get('id')}")
                points, changed = clip_polygon(min_area_box(annotation), width, height)
                if changed:
                    report["clipped_boxes"] += 1
                area = polygon_area(points)
                if area <= 1.0:
                    report["discarded_boxes"] += 1
                    continue
                normalized = [(x / width, y / height) for x, y in points]
                coords = " ".join(f"{value:.6f}" for point in normalized for value in point)
                lines.append(f"0 {coords}")
                converted.append(points)
                stats["objects"] += 1
                if area * scale * scale < 1024:
                    stats[f"small_objects_at_imgsz{args.imgsz}"] += 1

            label_path = output / "labels" / split / f"{Path(filename).stem}.txt"
            label_path.parent.mkdir(parents=True, exist_ok=True)
            label_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="ascii")
            if not lines:
                stats["empty_images"] += 1
            preview_candidates.append((len(lines), split, filename, converted))
            manifest_lines.append(f"images/{split}/{filename}")

        split_file = output / "splits" / f"{split}.txt"
        split_file.parent.mkdir(parents=True, exist_ok=True)
        split_file.write_text("\n".join(manifest_lines) + "\n", encoding="ascii")
        stats.update({f"scene_{name}": count for name, count in scene_counts.items()})
        report["splits"][split] = dict(stats)

    report["image_transfer"] = dict(report["image_transfer"])
    (output / "conversion_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    draw_preview(output, max(preview_candidates, key=lambda item: item[0]))
    return report


def main() -> None:
    print(json.dumps(convert(parse_args()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
