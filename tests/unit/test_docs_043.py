"""Evidence-only: DOCS-043 inventory / substring presence — not product behavior.

DOCS-043: three layers, error codes, what's new, scaffold, beta table.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_docs_043_three_layers_and_whats_new() -> None:
    whats = (ROOT / "docs" / "guides" / "whats-new-0.43.md").read_text(encoding="utf-8")
    contract = (ROOT / "docs" / "api" / "REFRESHABLE_VIEWS.md").read_text(encoding="utf-8")
    impl = (ROOT / "docs" / "implementation" / "INTERACTION_HANDLES_043.md").read_text(
        encoding="utf-8"
    )
    rfc = (ROOT / "docs" / "rfcs" / "RFC-0070-REFRESHABLE-VIEWS.md").read_text(encoding="utf-8")
    codes = (ROOT / "docs" / "guides" / "error-codes.md").read_text(encoding="utf-8")
    stability = (ROOT / "docs" / "api" / "STABILITY.md").read_text(encoding="utf-8")
    scaffold = (
        ROOT / "packages" / "hedron" / "src" / "hedron" / "cli" / "scaffold" / "fastapi.py"
    ).read_text(encoding="utf-8")
    archive = (ROOT / "docs" / "guides" / "whats-new-archive.md").read_text(encoding="utf-8")
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    ready = (ROOT / "docs" / "guides" / "whats-ready.md").read_text(encoding="utf-8")
    assert "Published `v0.43.0`" in whats or "0.43" in whats
    assert "@app.refreshable" in ready
    assert "FragmentHandle" in contract
    assert "PatchSet" in contract
    assert "compile_to_interaction" in impl or "protocol" in rfc.lower()
    assert "HED-VIEW-0001" in codes
    assert "HED-CMD-0001" in codes
    assert "HED-UPDATE-0001" in codes
    assert "HED-HOST-0001" in codes
    assert "FragmentHandle" in stability
    assert '@app.refreshable("/status")' in scaffold
    assert "swap(" not in scaffold
    assert "whats-new-0.43" in archive
    assert "whats-new-archive" in mkdocs
    assert "SR-021" not in whats or "#86" not in whats.split("Highlights")[0]


def test_low_level_apis_remain_documented() -> None:
    interaction = (ROOT / "docs" / "api" / "INTERACTION.md").read_text(encoding="utf-8")
    assert "InteractionResult" in interaction
    assert "FragmentRegion" in interaction
