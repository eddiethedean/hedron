"""PKG-051 in-tree 0.51 versions and 0.50 upgrade honesty."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_core import __version__ as core_version


def test_core_version_is_train_tip() -> None:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{core_version}"' in pyproject
    assert core_version == "0.51.0"


def test_packet_and_sandbox_entry() -> None:
    extras_py = Path("packages/hedron-extras/pyproject.toml")
    extras = tomllib.loads(extras_py.read_text(encoding="utf-8"))
    assert extras["project"]["version"] == "0.51.0"
    eps = extras["project"]["entry-points"]["hedron.plugins"]
    assert "hedron_extras_sandbox" in eps
    release = tomllib.loads(Path("docs/release.toml").read_text(encoding="utf-8"))["release"]
    assert release["train"] == "0.51"
    assert release["published_version"] == "0.51.0"
    assert release["pypi_version"] == "0.50.1"
    assert release["registry_status"] == "deferred"
    assert release["pypi_pin_ceiling"] == "0.51"
    assert release["previous_version"] == "0.50.3"
