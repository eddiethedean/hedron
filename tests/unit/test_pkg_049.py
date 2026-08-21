"""PKG-049 train versions and 0.49 packet files."""

from __future__ import annotations

from pathlib import Path

from hedron_core import __version__ as core_version


def test_core_version_is_at_least_049() -> None:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{core_version}"' in pyproject
    parts = tuple(int(p) for p in core_version.split(".")[:2])
    assert parts >= (0, 49)


def test_packet_files_exist() -> None:
    root = Path()
    for rel in (
        "docs/acceptance/release-gate-0.49.toml",
        "docs/acceptance/fastapi-lifetime-049.toml",
        "scripts/verify_pkg_49.py",
    ):
        assert (root / rel).is_file()
