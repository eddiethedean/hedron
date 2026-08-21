"""Evidence-only: package/release inventory — not product behavior.

PKG-051 packet files and train floor after 0.52 cut.
"""

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
    # Historical 0.51 packet remains valid after a later train is published.
    assert release["registry_status"] in {"deferred", "uploaded"}
    pypi = str(release["pypi_version"])
    assert tuple(int(p) for p in pypi.split(".")[:2]) >= (0, 51)
    # The pin ceiling remains a valid upper bound in either registry state.
    assert release["pypi_pin_ceiling"] == str(release["pypi_pin_ceiling"])
    published = str(release["published_version"])
    assert tuple(int(p) for p in published.split(".")[:2]) >= (0, 51)
    train_mm = tuple(int(p) for p in str(release["train"]).split(".")[:2])
    ceil_mm = tuple(int(p) for p in str(release["pypi_pin_ceiling"]).split(".")[:2])
    pypi_mm = tuple(int(p) for p in str(release["pypi_version"]).split(".")[:2])
    if release["registry_status"] == "uploaded":
        # Once published, consumers may pin through the next minor train.
        assert ceil_mm > train_mm
    elif pypi_mm >= train_mm:
        # Same-train deferred patch: first-run pin stays >=pypi,<next-minor.
        assert ceil_mm == (train_mm[0], train_mm[1] + 1)
    else:
        # Deferred while PyPI still serves a prior train.
        assert ceil_mm <= train_mm
