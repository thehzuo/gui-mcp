from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def example_paths() -> list[Path]:
    return sorted((ROOT / "examples").rglob("*.json"))


def v01_example_paths() -> list[Path]:
    return sorted((ROOT / "examples").glob("*.json"))


def v02_example_paths() -> list[Path]:
    return sorted((ROOT / "examples" / "v0_2").glob("*.json"))
