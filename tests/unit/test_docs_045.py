"""DOCS-045: interaction catalog is current; what's-new; no SR-021 claim."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_docs_045_layers_and_whats_new() -> None:
    contract = (ROOT / "docs" / "api" / "INTERACTION_CATALOG.md").read_text(encoding="utf-8")
    impl = (ROOT / "docs" / "implementation" / "TYPED_INTERACTION_ECOSYSTEM_045.md").read_text(
        encoding="utf-8"
    )
    whats = (ROOT / "docs" / "guides" / "whats-new-0.45.md").read_text(encoding="utf-8")
    codes = (ROOT / "docs" / "guides" / "error-codes.md").read_text(encoding="utf-8")
    stability = (ROOT / "docs" / "api" / "STABILITY.md").read_text(encoding="utf-8")
    archive = (ROOT / "docs" / "guides" / "whats-new-archive.md").read_text(encoding="utf-8")
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    header = contract.split("---", 2)[1] if contract.startswith("---") else contract[:240]
    assert "status: current" in header or "status: current" in contract
    assert "InteractionCatalog" in whats
    assert "interactions.json" in whats
    assert "SR-021" not in whats
    assert "HED-CATALOG-0001" in codes
    assert "HED-PROJECTION-0001" in codes
    assert "InteractionCatalog" in stability
    assert "whats-new-0.45" in archive
    assert "whats-new-archive" in mkdocs
    assert "0.46" in contract.lower() or "RFC-0073" in impl
