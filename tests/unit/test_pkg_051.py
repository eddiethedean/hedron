"""PKG-051 packet files and train floor after 0.52 cut."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_core import __version__ as core_version


def test_core_version_is_at_least_051() -> None:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{core_version}"' in pyproject
    parts = tuple(int(p) for p in core_version.split(".")[:2])
    assert parts >= (0, 51)


def test_packet_and_sandbox_entry() -> None:
    extras_py = Path("packages/hedron-extras/pyproject.toml")
    extras = tomllib.loads(extras_py.read_text(encoding="utf-8"))
    parts = tuple(int(p) for p in str(extras["project"]["version"]).split(".")[:2])
    assert parts >= (0, 51)
    eps = extras["project"]["entry-points"]["hedron.plugins"]
    assert "hedron_extras_sandbox" in eps
    release = tomllib.loads(Path("docs/release.toml").read_text(encoding="utf-8"))["release"]
    assert release["previous_version"] == "0.51.2" or tuple(
        int(p) for p in str(release["published_version"]).split(".")[:2]
    ) >= (0, 51)
    assert release["pypi_version"] == "0.51.0"
    assert release["registry_status"] == "deferred"
    assert release["pypi_pin_ceiling"] == "0.52"
