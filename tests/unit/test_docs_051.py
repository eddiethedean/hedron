"""DOCS-051 extras honesty and companion authoring."""

from __future__ import annotations

from pathlib import Path


def test_docs_name_sandbox_opt_in_and_companion() -> None:
    extras = Path("docs/packages/hedron-extras.md").read_text(encoding="utf-8")
    api = Path("docs/api/EXTRAS.md").read_text(encoding="utf-8")
    whats = Path("docs/guides/whats-new-0.51.md").read_text(encoding="utf-8")
    ready = Path("docs/guides/whats-ready.md").read_text(encoding="utf-8")
    evidence = Path("docs/guides/whats-ready-evidence.md").read_text(encoding="utf-8")
    for text in (extras, api, whats, evidence):
        assert "hedron_extras_sandbox" in text or "HEDRON_EXTRAS_SANDBOX" in text
        assert "experimental" in text.lower()
    assert "experimental" in ready.lower()
    assert "#504" in whats or "password" in whats.lower()
    assert "0.51.2" in whats or "0.51.1" in whats or "0.51.0" in whats
