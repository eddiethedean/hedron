"""Plugin remediation example pin tracks docs/release.toml train bounds."""

from __future__ import annotations

import inspect
import tomllib
from pathlib import Path

from hedron_core import plugin_loader

ROOT = Path(__file__).resolve().parents[2]


def test_missing_meta_remediation_matches_release_train_pin() -> None:
    release = tomllib.loads((ROOT / "docs" / "release.toml").read_text(encoding="utf-8"))["release"]
    expected = f">={release['pin_floor'].rsplit('.', 1)[0]},<{release['pin_ceiling']}"
    source = inspect.getsource(plugin_loader.load_plugins)
    assert f"hedron_version='{expected}'" in source
