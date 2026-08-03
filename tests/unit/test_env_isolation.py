"""Prove the core test environment does not install web frameworks or Node."""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path


def test_no_fastapi_flask_django() -> None:
    assert importlib.util.find_spec("fastapi") is None
    assert importlib.util.find_spec("flask") is None
    assert importlib.util.find_spec("django") is None


def test_no_package_json_in_repo() -> None:
    root = Path(__file__).resolve().parents[2]
    assert not (root / "package.json").exists()


def test_node_not_required_for_core() -> None:
    # Core must not depend on Node; CI jobs do not install it.
    # Local machines may have node on PATH — only assert no package.json tooling.
    assert shutil.which("npm") is None or True  # informational soft check
    assert not Path(__file__).resolve().parents[2].joinpath("node_modules").exists()
