"""Rebuild DIOR-R with the official DIOR train/val/test split.

The official split is sequential by image ID:
    train: 00001-05862
    val:   05863-11725
    test:  11726-23463

The split contents are verified below against the Git blob hashes of the
published ImageSets/Main lists before any dataset files are created.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path


SPLITS = {
    "train": (1, 5862, "4a208c19afcb06bf23dd08013fef705d6fbf19b1"),
    "val": (5863, 11725, "506b53ea4452fa0697937432630f60836d598ce8"),
    "test": (11726, 23463, "b4cc3638ee29f4d224d01def45d5c0af3958ac1c"),
}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Existing YOLO DIOR-R root containing train/val/test.")
    parser.add_argument("--output", type=Path, required=True, help="New official-split dataset root; must not exist.")
    parser.add_argument(
        "--mode",
        choices=("hardlink", "copy"),
        default="hardlink",
        help="Use hard links to save local disk space, or make independent copies.",
    )
    return parser.parse_args()


def git_blob_sha1(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode()
    return hashlib.sha1(header + content).hexdigest()  # noqa: S324 - Git object identity, not security.


def official_ids(split: str) -> list[str]:
    start, end, expected_hash = SPLITS[split]
    ids = [f"{index:05d}" for index in range(start, end + 1)]
    published_content = "".join(f"{image_id}\r\n" for image_id in ids).encode()
    actual_hash = git_blob_sha1(published_content)
    if actual_hash != expected_hash:
        raise RuntimeError(f"Official {split} list hash mismatch: {actual_hash} != {expected_hash}")
    return ids


def index_source(source: Path) -> tuple[dict[str, Path], dict[str, Path]]:
    images: dict[str, Path] = {}
    labels: dict[str, Path] = {}
    for split in ("train", "val", "test"):
        image_dir = source / split / "images"
        label_dir = source / split / "labels"
        if not image_dir.is_dir() or not label_dir.is_dir():
            raise FileNotFoundError(f"Missing source directory: {image_dir} or {label_dir}")

        for path in image_dir.iterdir():
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
                if path.stem in images:
                    raise RuntimeError(f"Duplicate source image ID: {path.stem}")
                images[path.stem] = path
        for path in label_dir.glob("*.txt"):
            if path.stem in labels:
                raise RuntimeError(f"Duplicate source label ID: {path.stem}")
            labels[path.stem] = path

    expected = set().union(*(set(official_ids(split)) for split in SPLITS))
    if set(images) != expected:
        missing = sorted(expected - set(images))[:10]
        extra = sorted(set(images) - expected)[:10]
        raise RuntimeError(f"Source image IDs do not match DIOR: missing={missing}, extra={extra}")
    if set(labels) != expected:
        missing = sorted(expected - set(labels))[:10]
        extra = sorted(set(labels) - expected)[:10]
        raise RuntimeError(f"Source label IDs do not match DIOR: missing={missing}, extra={extra}")
    return images, labels


def place_file(source: Path, destination: Path, mode: str) -> str:
    if mode == "copy":
        shutil.copy2(source, destination)
        return "copy"
    try:
        os.link(source, destination)
        return "hardlink"
    except OSError:
        shutil.copy2(source, destination)
        return "copy-fallback"


def main() -> None:
    args = parse_args()
    source = args.source.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if output.exists():
        raise FileExistsError(f"Output already exists; refusing to overwrite it: {output}")

    images, labels = index_source(source)
    temp = output.with_name(f"{output.name}.building")
    if temp.exists():
        raise FileExistsError(f"Temporary output already exists: {temp}")

    counts: dict[str, int] = {}
    modes: dict[str, int] = {}
    try:
        for split in SPLITS:
            image_dir = temp / split / "images"
            label_dir = temp / split / "labels"
            image_dir.mkdir(parents=True)
            label_dir.mkdir(parents=True)
            ids = official_ids(split)
            for image_id in ids:
                used_mode = place_file(images[image_id], image_dir / images[image_id].name, args.mode)
                modes[used_mode] = modes.get(used_mode, 0) + 1
                used_mode = place_file(labels[image_id], label_dir / labels[image_id].name, args.mode)
                modes[used_mode] = modes.get(used_mode, 0) + 1
            counts[split] = len(ids)

        manifest = {
            "source": str(source),
            "split_protocol": "official DIOR train/val/test",
            "counts": counts,
            "ranges": {name: [values[0], values[1]] for name, values in SPLITS.items()},
            "published_git_blob_sha1": {name: values[2] for name, values in SPLITS.items()},
            "file_placement": modes,
        }
        (temp / "split_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        temp.rename(output)
    except Exception:
        shutil.rmtree(temp, ignore_errors=True)
        raise

    print(f"Created official DIOR-R split at: {output}")
    print(f"Counts: train={counts['train']}, val={counts['val']}, test={counts['test']}")
    print(f"File placement: {modes}")


if __name__ == "__main__":
    main()
