"""PKG-050 train versions and 0.50 packet files."""

from __future__ import annotations

from pathlib import Path

from hedron_core import __version__ as core_version


def test_core_version_is_at_least_050() -> None:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{core_version}"' in pyproject
    parts = tuple(int(p) for p in core_version.split(".")[:2])
    assert parts >= (0, 50)


def test_packet_files_exist() -> None:
    root = Path(".")
    for rel in (
        "docs/acceptance/release-gate-0.50.toml",
        "docs/acceptance/explorer-architecture-050.toml",
        "scripts/verify_pkg_50.py",
        "scripts/check_pkg_050.py",
    ):
        assert (root / rel).is_file()
