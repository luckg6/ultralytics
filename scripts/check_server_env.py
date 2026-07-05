"""Check whether a Linux GPU server is ready for this OBB training project.

Example:
    python scripts/check_server_env.py --data ultralytics/cfg/datasets/DIOR-autodl.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check server environment for OBB training.")
    parser.add_argument("--env", help="Runtime environment profile, e.g. local or autodl.")
    parser.add_argument("--data", help="Dataset YAML path.")
    parser.add_argument("--pretrained", default="weights/pretrained/yolo11n-obb.pt", help="Pretrained weight path.")
    parser.add_argument("--resume", help="Optional last.pt checkpoint path for resume training.")
    parser.add_argument("--require-cuda", action="store_true", help="Exit with error if CUDA is unavailable.")
    return parser.parse_args()


def resolve(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def resolve_dataset_yaml(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate

    root_path = ROOT / candidate
    if root_path.exists():
        return root_path

    cfg_path = ROOT / "ultralytics" / "cfg" / "datasets" / candidate
    if cfg_path.exists():
        return cfg_path

    return root_path


def load_env_config(env_name: str | None) -> dict:
    if not env_name:
        return {}

    candidate = Path(env_name)
    env_path = resolve(candidate) if candidate.suffix else ROOT / "environments" / f"{env_name}.yaml"
    if not env_path.exists():
        raise FileNotFoundError(f"environment config does not exist: {env_path}")

    import yaml

    with env_path.open("r", encoding="utf-8") as f:
        env_cfg = yaml.safe_load(f) or {}
    env_cfg["_env_path"] = str(env_path)
    return env_cfg


def check_path(path: str | Path, label: str, must_exist: bool = True) -> bool:
    resolved = resolve(path)
    exists = resolved.exists()
    status = "OK" if exists else "MISSING"
    print(f"[{status}] {label}: {resolved}")
    if must_exist and not exists:
        return False
    return True


def count_images(path: Path) -> int:
    if not path.exists():
        return 0
    suffixes = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
    return sum(1 for p in path.iterdir() if p.is_file() and p.suffix.lower() in suffixes)


def check_dataset(data_yaml: Path) -> bool:
    import yaml

    if not data_yaml.exists():
        print(f"[MISSING] dataset yaml: {data_yaml}")
        return False

    with data_yaml.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    root = Path(data.get("path", ""))
    if not root.is_absolute():
        root = data_yaml.parent / root

    ok = True
    print(f"[OK] dataset yaml: {data_yaml}")
    print(f"[INFO] dataset root: {root}")
    for split in ("train", "val", "test"):
        rel = data.get(split)
        if not rel:
            continue
        image_dir = root / rel
        exists = image_dir.exists()
        count = count_images(image_dir) if exists else 0
        status = "OK" if exists else "MISSING"
        print(f"[{status}] {split} images: {image_dir} ({count} images)")
        ok = ok and exists

    nc = data.get("nc")
    names = data.get("names", {})
    print(f"[INFO] nc={nc}, names={len(names) if hasattr(names, '__len__') else 'unknown'}")
    return ok


def check_torch(require_cuda: bool) -> bool:
    try:
        import torch
    except Exception as exc:
        print(f"[ERROR] torch import failed: {exc}")
        return False

    print(f"[OK] torch: {torch.__version__}")
    cuda_ok = torch.cuda.is_available()
    print(f"[{'OK' if cuda_ok else 'ERROR'}] cuda available: {cuda_ok}")
    if cuda_ok:
        print(f"[INFO] cuda version used by torch: {torch.version.cuda}")
        print(f"[INFO] gpu: {torch.cuda.get_device_name(0)}")
        props = torch.cuda.get_device_properties(0)
        print(f"[INFO] gpu memory: {props.total_memory / 1024**3:.1f} GiB")
    return cuda_ok or not require_cuda


def main() -> None:
    args = parse_args()
    env_cfg = load_env_config(args.env)
    data = args.data or env_cfg.get("data") or "ultralytics/cfg/datasets/DIOR-autodl.yaml"
    ok = True

    if env_cfg:
        print(f"[OK] environment config: {env_cfg['_env_path']}")
    ok = check_torch(args.require_cuda) and ok
    ok = check_path(args.pretrained, "pretrained weight") and ok
    if args.resume:
        ok = check_path(args.resume, "resume checkpoint") and ok
    ok = check_dataset(resolve_dataset_yaml(data)) and ok

    print("[RESULT] server environment looks ready." if ok else "[RESULT] server environment needs attention.")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
