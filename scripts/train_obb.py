"""Train OBB experiments from a YAML experiment config.

Example:
    python scripts/train_obb.py --config experiments/dior/baseline.yaml
"""

from __future__ import annotations

import argparse
import shutil
import sys
from multiprocessing import freeze_support
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a YOLO OBB experiment.")
    parser.add_argument("--config", default="experiments/dior/baseline.yaml", help="Experiment YAML path.")
    parser.add_argument("--env", help="Runtime environment profile, e.g. local or autodl.")
    parser.add_argument("--model", help="Override model YAML path.")
    parser.add_argument("--data", help="Override dataset YAML path.")
    parser.add_argument("--pretrained", help="Override pretrained weights path.")
    parser.add_argument("--name", help="Override run name.")
    parser.add_argument("--device", help="Override device, e.g. 0 or cpu.")
    parser.add_argument("--batch", type=int, help="Override batch size.")
    parser.add_argument("--cache", help="Override cache mode, e.g. ram, disk, False.")
    parser.add_argument("--resume", help="Resume from a last.pt checkpoint.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print the resolved config without training.")
    return parser.parse_args()


def load_config(path: str | Path) -> dict:
    import yaml

    config_path = resolve_config_path(path)
    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    cfg["_config_path"] = str(config_path)
    return cfg


def resolve_config_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def load_env_config(env_name: str | None) -> dict:
    if not env_name:
        return {}

    candidate = Path(env_name)
    if candidate.suffix:
        env_path = resolve_config_path(candidate)
    else:
        env_path = ROOT / "environments" / f"{env_name}.yaml"

    if not env_path.exists():
        raise FileNotFoundError(f"environment config does not exist: {env_path}")

    import yaml

    with env_path.open("r", encoding="utf-8") as f:
        env_cfg = yaml.safe_load(f) or {}
    env_cfg["_env_path"] = str(env_path)
    env_cfg["_env_name"] = env_name
    return env_cfg


def pick_value(cli_value, env_cfg: dict, exp_cfg: dict, key: str, default=None):
    if cli_value is not None:
        return cli_value
    if key in env_cfg:
        return env_cfg[key]
    return exp_cfg.get(key, default)


def as_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "on"}
    return bool(value)


def normalize_cache(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.lower()
        if lowered in {"false", "0", "none", "no", "off"}:
            return False
        if lowered in {"true", "1", "yes", "on"}:
            return True
    return value


def resolve_existing_path(path: str | Path, label: str) -> str:
    candidate = Path(path)
    resolved = candidate if candidate.is_absolute() else ROOT / candidate
    if not resolved.exists():
        raise FileNotFoundError(f"{label} does not exist: {resolved}")
    return str(candidate)


def ensure_amp_check_weight() -> None:
    """Keep Ultralytics AMP checks offline by placing yolo26n.pt in the working directory if available."""
    src = ROOT / "weights" / "pretrained" / "yolo26n.pt"
    dst = ROOT / "yolo26n.pt"
    if src.exists() and not dst.exists():
        shutil.copy2(src, dst)


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    env_cfg = load_env_config(args.env)

    if args.resume:
        resume_path = resolve_existing_path(args.resume, "resume checkpoint")
        data = pick_value(args.data, env_cfg, cfg, "data")
        device = pick_value(args.device, env_cfg, cfg, "device", 0)
        batch = pick_value(args.batch, env_cfg, cfg, "batch", 4)
        cache = normalize_cache(pick_value(args.cache, env_cfg, cfg, "cache", "disk"))
        workers = int(pick_value(None, env_cfg, cfg, "workers", 4))

        if args.dry_run:
            print("Resume config is ready.")
            print(f"config: {cfg['_config_path']}")
            if env_cfg:
                print(f"env:    {env_cfg['_env_path']}")
            print(f"resume: {resume_path}")
            print(f"data:   {data}")
            print(f"device: {device}")
            print(f"batch:  {batch}")
            print(f"cache:  {cache}")
            print(f"workers:{workers}")
            return

        ensure_amp_check_weight()

        from ultralytics import YOLO

        model = YOLO(resume_path)
        model.train(
            resume=resume_path,
            data=data,
            device=device,
            batch=int(batch),
            workers=workers,
            cache=cache,
        )
        return

    status = cfg.get("status", "planned")
    if status != "ready":
        raise RuntimeError(f"Experiment config is not ready: {cfg['_config_path']} (status={status})")

    model_path = args.model or cfg["model"]
    data = pick_value(args.data, env_cfg, cfg, "data")
    pretrained = args.pretrained or cfg.get("pretrained")
    name = args.name or cfg.get("name")
    device = pick_value(args.device, env_cfg, cfg, "device", 0)
    batch = pick_value(args.batch, env_cfg, cfg, "batch", 4)
    cache = normalize_cache(pick_value(args.cache, env_cfg, cfg, "cache", "disk"))
    workers = int(pick_value(None, env_cfg, cfg, "workers", 4))

    resolve_existing_path(model_path, "model")
    if pretrained:
        resolve_existing_path(pretrained, "pretrained")

    if args.dry_run:
        print("Experiment config is ready.")
        print(f"config:     {cfg['_config_path']}")
        if env_cfg:
            print(f"env:        {env_cfg['_env_path']}")
        print(f"model:      {model_path}")
        print(f"pretrained: {pretrained}")
        print(f"data:       {data}")
        print(f"name:       {name}")
        print(f"epochs:     {cfg.get('epochs', 100)}")
        print(f"batch:      {batch}")
        print(f"imgsz:      {cfg.get('imgsz', 640)}")
        print(f"device:     {device}")
        print(f"cache:      {cache}")
        print(f"workers:    {workers}")
        if "set_hbs" in cfg:
            print(f"set_hbs:   {cfg['set_hbs']}")
        return

    ensure_amp_check_weight()

    import torch

    torch.manual_seed(int(cfg.get("seed", 42)))

    from ultralytics import YOLO

    model = YOLO(model_path)
    model.train(
        data=data,
        pretrained=pretrained,
        epochs=int(cfg.get("epochs", 100)),
        batch=int(batch),
        imgsz=int(cfg.get("imgsz", 640)),
        seed=int(cfg.get("seed", 42)),
        device=device,
        amp=as_bool(cfg.get("amp", True)),
        deterministic=as_bool(cfg.get("deterministic", True)),
        workers=workers,
        cache=cache,
        cos_lr=as_bool(cfg.get("cos_lr", True)),
        set_hbs=float(cfg.get("set_hbs", 1.0)),
        project=cfg.get("project"),
        name=name,
    )


if __name__ == "__main__":
    freeze_support()
    main()
