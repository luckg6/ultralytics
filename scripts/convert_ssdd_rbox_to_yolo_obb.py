"""Convert the official RBox-SSDD release to Ultralytics YOLO-OBB format."""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import shutil
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw


CLASS_NAME = "ship"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("C:/E/datasets/Official-SSDD-OPEN"))
    parser.add_argument("--output", type=Path, default=Path("C:/E/datasets/SSDD-RBox-YOLO"))
    parser.add_argument("--val-fraction", type=float, default=0.1, help="Fraction of official train held out for val.")
    parser.add_argument("--seed", type=int, default=42, help="Seed for the scene-stratified val split.")
    parser.add_argument("--imgsz", type=int, default=640, help="Input size used for small-object statistics.")
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
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate image id in {path}")
    if any(not image_id.isdigit() for image_id in ids):
        raise ValueError(f"Invalid image id in {path}")
    return ids


def directory_ids(path: Path) -> set[str]:
    return {item.stem for item in path.glob("*.jpg")}


def build_splits(root: Path, val_fraction: float, seed: int) -> tuple[dict[str, list[str]], dict[str, str]]:
    if not 0 < val_fraction < 0.5:
        raise ValueError("val-fraction must be between 0 and 0.5")

    split_dir = root / "ImageSets" / "Main"
    official_train = set(read_ids(split_dir / "train.txt"))
    official_test = set(read_ids(split_dir / "test.txt"))
    if official_train & official_test:
        raise ValueError("Official train and test splits overlap")

    train_scenes = {
        "inshore": directory_ids(root / "JPEGImages_train_inshore"),
        "offshore": directory_ids(root / "JPEGImages_train_offshore"),
    }
    test_scenes = {
        "inshore": directory_ids(root / "JPEGImages_test_inshore"),
        "offshore": directory_ids(root / "JPEGImages_test_offshore"),
    }
    if set().union(*train_scenes.values()) != official_train or set().union(*test_scenes.values()) != official_test:
        raise ValueError("Scene directories do not match official train/test manifests")
    if train_scenes["inshore"] & train_scenes["offshore"] or test_scenes["inshore"] & test_scenes["offshore"]:
        raise ValueError("Inshore and offshore scene directories overlap")

    rng = random.Random(seed)
    val_ids: set[str] = set()
    for scene in ("inshore", "offshore"):
        candidates = sorted(train_scenes[scene])
        rng.shuffle(candidates)
        val_count = round(len(candidates) * val_fraction)
        val_ids.update(candidates[:val_count])

    train_ids = official_train - val_ids
    splits = {"train": sorted(train_ids), "val": sorted(val_ids), "test": sorted(official_test)}
    if set(splits["train"]) & set(splits["val"]):
        raise ValueError("Generated train and val splits overlap")

    scene_by_id = {
        image_id: scene
        for scene_sets in (train_scenes, test_scenes)
        for scene, image_ids in scene_sets.items()
        for image_id in image_ids
    }
    return splits, scene_by_id


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


def parse_annotation(path: Path) -> tuple[str, int, int, list[list[tuple[float, float]]], Counter]:
    root = ET.parse(path).getroot()
    filename = root.findtext("filename")
    width_text = root.findtext("size/width")
    height_text = root.findtext("size/height")
    if not filename or not width_text or not height_text:
        raise ValueError(f"Missing filename or image size in {path}")

    flags: Counter = Counter()
    boxes: list[list[tuple[float, float]]] = []
    for obj in root.findall("object"):
        class_name = obj.findtext("name")
        if class_name != CLASS_NAME:
            raise ValueError(f"Unexpected class {class_name!r} in {path}")
        flags[f"difficult_{obj.findtext('difficult', default='0')}"] += 1
        flags[f"truncated_{obj.findtext('truncated', default='0')}"] += 1
        rotated = obj.find("rotated_bndbox")
        if rotated is None:
            raise ValueError(f"Missing rotated_bndbox in {path}")
        points = []
        for index in range(1, 5):
            x = rotated.findtext(f"x{index}")
            y = rotated.findtext(f"y{index}")
            if x is None or y is None:
                raise ValueError(f"Missing RBox vertex {index} in {path}")
            points.append((float(x), float(y)))
        boxes.append(points)
    return filename, int(width_text), int(height_text), boxes, flags


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
    image_path = output / "images" / split / filename
    with Image.open(image_path).convert("RGB") as image:
        draw = ImageDraw.Draw(image)
        for points in boxes:
            draw.line(points + [points[0]], fill=(255, 40, 40), width=2)
        image.save(output / "conversion_preview.jpg", quality=92)


def convert(args: argparse.Namespace) -> dict:
    source = args.source.resolve()
    output = args.output.resolve()
    root = source / "RBox_SSDD" / "voc_style"
    annotation_dir = root / "Annotations"
    image_dir = root / "JPEGImages"
    required = [annotation_dir, image_dir, root / "ImageSets" / "Main" / "train.txt", root / "ImageSets" / "Main" / "test.txt"]
    if any(not path.exists() for path in required):
        raise FileNotFoundError(f"Incomplete Official RBox-SSDD source under {source}")

    prepare_output(source, output, args.overwrite)
    splits, scene_by_id = build_splits(root, args.val_fraction, args.seed)
    report = {
        "source": str(source),
        "output": str(output),
        "variant": "Official RBox-SSDD",
        "class_names": [CLASS_NAME],
        "split_protocol": (
            f"official suffix-based test; scene-stratified {args.val_fraction:.0%} holdout from official train "
            f"with seed={args.seed}"
        ),
        "small_object_protocol": f"letterboxed model input area < 1024 at imgsz={args.imgsz}",
        "splits": {},
        "annotation_flags": Counter(),
        "clipped_boxes": 0,
        "discarded_boxes": 0,
        "image_transfer": Counter(),
    }
    preview_candidates: list[tuple[int, str, str, list[list[tuple[float, float]]]]] = []

    for split, image_ids in splits.items():
        split_stats = Counter()
        split_stats.update({"images": len(image_ids)})
        scene_counts: Counter = Counter()
        for image_id in image_ids:
            xml_path = annotation_dir / f"{image_id}.xml"
            if not xml_path.exists():
                raise FileNotFoundError(xml_path)
            filename, width, height, boxes, flags = parse_annotation(xml_path)
            if Path(filename).stem != image_id:
                raise ValueError(f"Image id mismatch in {xml_path}: {filename}")
            source_image = image_dir / filename
            if not source_image.exists():
                raise FileNotFoundError(source_image)
            with Image.open(source_image) as image:
                if image.size != (width, height):
                    raise ValueError(f"XML/image size mismatch for {source_image}: {(width, height)} vs {image.size}")

            transfer = place_image(source_image, output / "images" / split / filename, args.copy_mode)
            report["image_transfer"][transfer] += 1
            report["annotation_flags"].update(flags)
            scene_counts[scene_by_id[image_id]] += 1
            converted: list[list[tuple[float, float]]] = []
            lines: list[str] = []
            scale = min(args.imgsz / width, args.imgsz / height)
            for points in boxes:
                clipped, changed = clip_polygon(points, width, height)
                if changed:
                    report["clipped_boxes"] += 1
                area = polygon_area(clipped)
                if area <= 1.0:
                    report["discarded_boxes"] += 1
                    continue
                normalized = [(x / width, y / height) for x, y in clipped]
                coords = " ".join(f"{value:.6f}" for point in normalized for value in point)
                lines.append(f"0 {coords}")
                converted.append(clipped)
                split_stats["objects"] += 1
                if area * scale * scale < 1024:
                    split_stats[f"small_objects_at_imgsz{args.imgsz}"] += 1

            label_path = output / "labels" / split / f"{image_id}.txt"
            label_path.parent.mkdir(parents=True, exist_ok=True)
            label_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="ascii")
            if not lines:
                split_stats["empty_images"] += 1
            preview_candidates.append((len(lines), split, filename, converted))

        manifest = output / "splits" / f"{split}.txt"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text("\n".join(image_ids) + "\n", encoding="ascii")
        report["splits"][split] = {**dict(split_stats), "scenes": dict(sorted(scene_counts.items()))}

    report["annotation_flags"] = dict(sorted(report["annotation_flags"].items()))
    report["image_transfer"] = dict(report["image_transfer"])
    (output / "conversion_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="ascii")
    draw_preview(output, max(preview_candidates, key=lambda item: item[0]))
    return report


def main() -> None:
    args = parse_args()
    report = convert(args)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
