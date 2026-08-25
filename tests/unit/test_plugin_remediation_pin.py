"""Plugin remediation example pin tracks docs/release.toml train bounds."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_core import plugin_loader

ROOT = Path(__file__).resolve().parents[2]


def test_missing_meta_remediation_matches_release_train_pin() -> None:
    release = tomllib.loads((ROOT / "docs" / "release.toml").read_text(encoding="utf-8"))["release"]
    development = str(release["development_version"]).split(".")
    expected = f">={development[0]}.{development[1]},<{development[0]}.{int(development[1]) + 1}"
    source = Path(plugin_loader.__file__).read_text(encoding="utf-8")
    assert expected in source
