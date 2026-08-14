"""Locate packaged element static assets."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

__all__ = ["asset_path", "bridge_path", "example_css_path", "example_module_path"]


def asset_path(name: str) -> Path:
    target = resources.files("hedron_elements").joinpath("static").joinpath(name)
    with resources.as_file(target) as path:
        return Path(path)


def bridge_path() -> Path:
    return asset_path("hedron-bridge.mjs")


def example_module_path() -> Path:
    return asset_path("hedron-example.mjs")


def example_css_path() -> Path:
    return asset_path("hedron-example.css")
