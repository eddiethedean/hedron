"""DOCS-054 evidence for authoring-loop / chrome documentation."""

from __future__ import annotations

import tomllib
from pathlib import Path

PACKET_FILES = (
    Path("docs/acceptance/release-gate-0.54.toml"),
    Path("docs/acceptance/authoring-loop-inventory-054.toml"),
    Path("docs/acceptance/authoring-shared-054.toml"),
    Path("docs/acceptance/authoring-sim-notebook-054.toml"),
    Path("docs/acceptance/authoring-chrome-054.toml"),
    Path("docs/acceptance/RELEASE_0_54.md"),
    Path("docs/acceptance/upgrade-fixtures-054.md"),
    Path("docs/implementation/AUTHORING_LOOP_054.md"),
    Path("docs/api/AUTHORING_LOOP.md"),
    Path("docs/rfcs/RFC-0081-AUTHORING-LOOP-AND-CHROME.md"),
    Path("docs/guides/package-author-handbook.md"),
    Path("docs/guides/simulator-semantics.md"),
    Path("docs/guides/notebook-preview.md"),
    Path("docs/guides/whats-new-0.54.md"),
)


def test_docs_054_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.54.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["DOCS-054"]["state"] == "Verified"
    assert Path("docs/rfcs/RFC-0081-AUTHORING-LOOP-AND-CHROME.md").is_file()


def test_packet_files_and_handbook_markers() -> None:
    for path in PACKET_FILES:
        assert path.is_file(), path
    rfc = Path("docs/rfcs/RFC-0081-AUTHORING-LOOP-AND-CHROME.md").read_text(encoding="utf-8")
    assert "**Status:** Accepted" in rfc
    handbook = Path("docs/guides/package-author-handbook.md").read_text(encoding="utf-8")
    for marker in (
        "hedron package doctor",
        "hedron-sample-kit",
        "hedron-sim",
        "hedron-notebook",
        "authoring_loop",
    ):
        assert marker in handbook, marker
    whats = Path("docs/guides/whats-new-0.54.md").read_text(encoding="utf-8")
    assert "0.54" in whats
    assert "package doctor" in whats.lower() or "DOCTOR-054" in whats


def test_zero_css_example_documented() -> None:
    readme = Path("examples/chrome-zero-css/README.md").read_text(encoding="utf-8")
    assert "zero" in readme.lower()
    assert Path("examples/chrome-zero-css/app.py").is_file()
