"""Connect 2025.06 FastAPI runtime needs pkg_resources.parse_version."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SHIM = ROOT / "packages" / "hedron-posit" / "src" / "pkg_resources" / "__init__.py"


def test_pkg_resources_shim_parse_version() -> None:
    spec = importlib.util.spec_from_file_location("hedron_posit_pkg_resources_shim", SHIM)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    parse_version = module.parse_version
    assert parse_version("0.35.0") >= parse_version("0.35.0")
    assert parse_version("1.2.0") > parse_version("1.1.0")
    assert parse_version("0.109.0") >= parse_version("0.109.0")
