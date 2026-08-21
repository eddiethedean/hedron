"""ZERO-CSS-057 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path


def test_zero_css_057_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.57.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["ZERO-CSS-057"]["state"] == "Verified"
    fixture = tomllib.loads(
        Path("docs/acceptance/zero-css-fixture-057.toml").read_text(encoding="utf-8")
    )
    assert fixture["application_component_css_files"] == 0
    required = set(fixture["required_surfaces"])
    assert {
        "environment-banner",
        "brand",
        "account-summary",
        "resource-list",
        "file-upload",
        "identity",
        "compact-status",
        "process-flow",
        "footer",
    } <= required


def test_zero_css_example_has_no_application_stylesheet() -> None:
    root = Path("examples/chrome-zero-css")
    assert root.is_dir()
    css_files = list(root.rglob("*.css"))
    assert css_files == []
    app = (root / "app.py").read_text(encoding="utf-8")
    # Ignore the module docstring (which documents the zero-style= claim).
    code = app.split('"""', 2)[-1]
    assert "style=" not in code
    assert "<style" not in code.lower()
    for needle in (
        "EnvironmentBanner",
        "Brand",
        "AccountSummary",
        "ResourceList",
        "FileUpload",
        "Identity",
        "AppFooter",
        "Status",
        "ProcessFlow",
    ):
        assert needle in app
