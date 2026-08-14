"""ELEMENTS-036: package install surface."""

from __future__ import annotations

from importlib.metadata import version
from pathlib import Path

import hedron_elements
from hedron_elements.assets import bridge_path, example_module_path
from hedron_elements.example import Example
from hedron_elements.plugin import PLUGIN_META, register


def test_version_and_exports() -> None:
    assert hedron_elements.__version__ == "0.36.0"
    assert version("hedron-elements").startswith("0.36.")
    assert Example is not None


def test_static_assets_present() -> None:
    assert bridge_path().is_file()
    assert example_module_path().is_file()
    bridge = bridge_path().read_bytes()
    # Uncompressed budget check: gzip target is 12 KiB; raw source should stay lean.
    assert len(bridge) < 12_288


def test_plugin_meta() -> None:
    assert PLUGIN_META.distribution == "hedron-elements"
    assert callable(register)


def test_package_layout() -> None:
    root = Path(__file__).resolve().parents[2] / "packages" / "hedron-elements"
    assert (root / "pyproject.toml").is_file()
    assert (root / "src" / "hedron_elements" / "plugin.py").is_file()
