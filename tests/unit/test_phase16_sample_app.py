"""Smoke import for the 0.16 sample app."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def test_data_app_016_imports() -> None:
    path = Path(__file__).resolve().parents[2] / "examples" / "data-app-0.16" / "app.py"
    spec = importlib.util.spec_from_file_location("data_app_016_sample", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert hasattr(module, "app")
    assert module.app.title == "Hedron 0.16 workbench sample"
