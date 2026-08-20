"""AUTHOR-052 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_conformance import (
    AUTHOR_KIT_VERSION,
    Capability,
    author_kit_dir,
    author_kit_summary,
    declared_capabilities,
    intentional_failure_examples,
    validate_author_manifest,
)
from hedron_conformance.author import author_kit_readme


def test_author_052_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.52.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["AUTHOR-052"]["state"] in {"Planned", "Implemented", "Verified"}
    assert Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md").is_file()


def test_author_kit_version_and_capability_declaration() -> None:
    assert AUTHOR_KIT_VERSION == "0.52.0"
    readme = author_kit_readme()
    assert "Capability" in readme
    assert "monorepo" in readme.lower()
    assert "0.52" in readme
    caps = declared_capabilities()
    assert set(caps) == {c.value for c in Capability}
    summary = author_kit_summary()
    assert summary["author_kit_version"] == "0.52.0"
    assert summary["declares_capability_without_monorepo"] is True
    assert summary["readme_present"] is True
    assert (author_kit_dir() / "README.md").is_file()
    assert all(item.ok for item in validate_author_manifest("hedron-portable-1", "1.0.0"))
    assert any(not item.ok for item in intentional_failure_examples())
