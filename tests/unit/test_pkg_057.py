"""PKG-057 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

import hedron
import hedron_core


def test_pkg_057_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.57.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["PKG-057"]["state"] == "Verified"
    assert Path("docs/api/PRESENTATION.md").is_file()
    assert Path("docs/implementation/PRESENTATION_057.md").is_file()
    assert Path("docs/acceptance/RELEASE_0_57.md").is_file()


def test_public_exports_include_presentation_symbols() -> None:
    for name in (
        "GridItem",
        "Surface",
        "Avatar",
        "Identity",
        "ResourceList",
        "ResourceRow",
        "Brand",
        "AccountSummary",
        "EnvironmentBanner",
        "NavStatus",
        "AppFooter",
    ):
        assert hasattr(hedron_core, name), name
        assert hasattr(hedron, name), name
    assert hasattr(hedron, "FileUpload")
