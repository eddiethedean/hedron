"""DOCS-048 packet, public contract, codes, tracking."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_tracking_issue_bound() -> None:
    for rel in (
        "docs/acceptance/RELEASE_0_48.md",
        "STATUS.md",
        "docs/ROADMAP.md",
        "docs/TRACEABILITY.md",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "#373" in text


def test_public_contract_and_guides() -> None:
    api = (ROOT / "docs/api/HTMX_EXTENSIONS.md").read_text(encoding="utf-8")
    assert "HtmxExtension" in api or "htmx_extensions" in api
    assert "SseRegion" in api
    codes = (ROOT / "docs/guides/error-codes.md").read_text(encoding="utf-8")
    for code in (
        "HED-EXT-0001",
        "HED-EXT-0002",
        "HED-EXT-0003",
        "HED-HTMX-0001",
        "HED-HTMX-0002",
        "HED-JINJA-0030",
    ):
        assert code in codes
    for rel in (
        "docs/guides/whats-new-0.48.md",
        "docs/guides/htmx-extensions.md",
        "examples/htmx-extensions/README.md",
    ):
        assert (ROOT / rel).is_file(), rel
