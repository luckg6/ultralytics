"""Convert the official HRSC2016 release to Ultralytics YOLO-OBB format."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw


CLASS_NAME = "ship"
EXPECTED_SPLITS = {"train": 436, "val": 181, "test": 453}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("C:/E/datasets/HRSC2016/HRSC2016"))
    parser.add_argument("--output", type=Path, default=Path("C:/E/datasets/HRSC2016-YOLO"))
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


def load_splits(source: Path) -> dict[str, list[str]]:
    splits = {name: read_ids(source / "ImageSets" / f"{name}.txt") for name in EXPECTED_SPLITS}
    for name, expected in EXPECTED_SPLITS.items():
        if len(splits[name]) != expected:
            raise ValueError(f"Expected {expected} {name} images, found {len(splits[name])}")
    names = tuple(splits)
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            overlap = set(splits[left]) & set(splits[right])
            if overlap:
                raise ValueError(f"{left}/{right} overlap: {sorted(overlap)[:5]}")
    return splits


def rotated_box(cx: float, cy: float, width: float, height: float, angle: float) -> list[tuple[float, float]]:
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    half_w, half_h = width / 2, height / 2
    corners = [(-half_w, -half_h), (half_w, -half_h), (half_w, half_h), (-half_w, half_h)]
    return [(cx + x * cos_a - y * sin_a, cy + x * sin_a + y * cos_a) for x, y in corners]


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
    return clipped, changed


def parse_annotation(path: Path) -> tuple[int, int, list[list[tuple[float, float]]], Counter]:
    root = ET.parse(path).getroot()
    width = int(root.findtext("Img_SizeWidth", default="0"))
    height = int(root.findtext("Img_SizeHeight", default="0"))
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid image size in {path}")

    boxes: list[list[tuple[float, float]]] = []
    flags: Counter = Counter()
    for obj in root.findall("./HRSC_Objects/HRSC_Object"):
        values = {
            key: float(obj.findtext(key, default="nan"))
            for key in ("mbox_cx", "mbox_cy", "mbox_w", "mbox_h", "mbox_ang")
        }
        if not all(math.isfinite(value) for value in values.values()):
            raise ValueError(f"Invalid rotated box in {path}")
        if values["mbox_w"] <= 0 or values["mbox_h"] <= 0:
            raise ValueError(f"Non-positive rotated box in {path}")
        boxes.append(
            rotated_box(
                values["mbox_cx"],
                values["mbox_cy"],
                values["mbox_w"],
                values["mbox_h"],
                values["mbox_ang"],
            )
        )
        flags[f"difficult_{obj.findtext('difficult', default='0')}"] += 1
        flags[f"truncated_{obj.findtext('truncated', default='0')}"] += 1
    return width, height, boxes, flags


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
    _, split, image_name, boxes = candidate
    with Image.open(output / "images" / split / image_name).convert("RGB") as image:
        draw = ImageDraw.Draw(image)
        for points in boxes:
            draw.line(points + [points[0]], fill=(255, 40, 40), width=3)
        image.save(output / "conversion_preview.jpg", quality=92)


def convert(args: argparse.Namespace) -> dict:
    source = args.source.resolve()
    output = args.output.resolve()
    image_dir = source / "FullDataSet" / "AllImages"
    annotation_dir = source / "FullDataSet" / "Annotations"
    required = [image_dir, annotation_dir, source / "ImageSets" / "train.txt", source / "ImageSets" / "val.txt", source / "ImageSets" / "test.txt"]
    if any(not path.exists() for path in required):
        raise FileNotFoundError(f"Incomplete HRSC2016 source under {source}")

    prepare_output(source, output, args.overwrite)
    splits = load_splits(source)
    report = {
        "source": str(source),
        "output": str(output),
        "variant": "HRSC2016 official archive split",
        "class_names": [CLASS_NAME],
        "split_protocol": "archive ImageSets: 436 train, 181 val, 453 test",
        "small_object_protocol": f"letterboxed model input area < 1024 at imgsz={args.imgsz}",
        "splits": {},
        "annotation_flags": Counter(),
        "clipped_boxes": 0,
        "discarded_boxes": 0,
        "image_transfer": Counter(),
    }
    preview_candidates: list[tuple[int, str, str, list[list[tuple[float, float]]]]] = []

    for split, image_ids in splits.items():
        stats = Counter(images=len(image_ids))
        manifest_lines = []
        for image_id in image_ids:
            source_image = image_dir / f"{image_id}.bmp"
            xml_path = annotation_dir / f"{image_id}.xml"
            if not source_image.exists() or not xml_path.exists():
                raise FileNotFoundError(f"Missing image or annotation for {image_id}")
            width, height, boxes, flags = parse_annotation(xml_path)
            with Image.open(source_image) as image:
                if image.size != (width, height):
                    raise ValueError(f"XML/image size mismatch for {image_id}: {(width, height)} vs {image.size}")

            image_name = source_image.name
            transfer = place_image(source_image, output / "images" / split / image_name, args.copy_mode)
            report["image_transfer"][transfer] += 1
            report["annotation_flags"].update(flags)
            lines = []
            converted = []
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
                stats["objects"] += 1
                if area * scale * scale < 1024:
                    stats[f"small_objects_at_imgsz{args.imgsz}"] += 1

            label_path = output / "labels" / split / f"{image_id}.txt"
            label_path.parent.mkdir(parents=True, exist_ok=True)
            label_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="ascii")
            if not lines:
                stats["empty_images"] += 1
            preview_candidates.append((len(lines), split, image_name, converted))
            manifest_lines.append(f"images/{split}/{image_name}")

        split_file = output / "splits" / f"{split}.txt"
        split_file.parent.mkdir(parents=True, exist_ok=True)
        split_file.write_text("\n".join(manifest_lines) + "\n", encoding="ascii")
        report["splits"][split] = dict(stats)

    report["annotation_flags"] = dict(report["annotation_flags"])
    report["image_transfer"] = dict(report["image_transfer"])
    (output / "conversion_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    preview = max(preview_candidates, key=lambda item: item[0])
    draw_preview(output, preview)
    return report


def main() -> None:
    report = convert(parse_args())
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
