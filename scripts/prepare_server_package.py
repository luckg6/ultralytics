"""Create a zip package for deploying or updating code on a Linux GPU server.

Example:
    python scripts/prepare_server_package.py --output server_packages/code_update.zip
    python scripts/prepare_server_package.py --include-run runs/obb/runs/obb/dior_A_p2
"""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OUTPUT = ROOT / "server_packages" / "ultralytics_remote_obb_server.zip"

EXCLUDE_DIRS = {
    ".git",
    ".github",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "runs",
    "server_packages",
    "docs",
    "examples",
    "tests",
}

EXCLUDE_SUFFIXES = {
    ".npy",
    ".cache",
    ".onnx",
    ".engine",
    ".torchscript",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package project files for server deployment or code updates.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output zip path.")
    parser.add_argument(
        "--include-run",
        action="append",
        default=[],
        help="Run directory to include for resume, e.g. runs/obb/runs/obb/dior_A_p2.",
    )
    return parser.parse_args()


def should_skip(path: Path, include_runs: set[Path]) -> bool:
    rel = path.relative_to(ROOT)
    parts = set(rel.parts)

    if any(path == run or run in path.parents for run in include_runs):
        return False

    if parts & EXCLUDE_DIRS:
        return True

    if path.suffix.lower() in EXCLUDE_SUFFIXES:
        return True

    if path.suffix.lower() == ".pt" and "weights" not in rel.parts:
        return True

    return False


def main() -> None:
    args = parse_args()
    output = Path(args.output)
    output = output if output.is_absolute() else ROOT / output
    include_runs = {(ROOT / p).resolve() for p in args.include_run}

    for run in sorted(include_runs):
        if not run.exists():
            raise FileNotFoundError(f"Included run directory does not exist: {run}")
        if not run.is_dir():
            raise NotADirectoryError(f"Included run path is not a directory: {run}")

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    with ZipFile(output, "w", ZIP_DEFLATED) as zf:
        for path in ROOT.rglob("*"):
            if path == output or path.is_dir() or should_skip(path.resolve(), include_runs):
                continue
            zf.write(path, path.relative_to(ROOT))

    print(f"Package written to: {output}")
    print("Included resume runs:")
    for run in sorted(include_runs):
        print(f"  {run}")


if __name__ == "__main__":
    main()
