"""Locate packaged first-party chart static assets."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

__all__ = ["chart_css_path", "chart_module_path", "static_path"]


def static_path(name: str) -> Path:
    target = resources.files("hedron_charts").joinpath("static").joinpath(name)
    with resources.as_file(target) as path:
        return Path(path)


def chart_module_path() -> Path:
    return static_path("hedron-chart.mjs")


def chart_css_path() -> Path:
    return static_path("hedron-chart.css")
