"""Locate vendored map host assets."""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parent

__all__ = ["map_module_path", "map_css_path"]


def map_module_path() -> Path:
    return _ROOT / "static" / "hedron-map.mjs"


def map_css_path() -> Path:
    return _ROOT / "static" / "hedron-map.css"
