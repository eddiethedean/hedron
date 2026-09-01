"""Evidence-only: DOCS-044 inventory / substring presence — not product behavior.

DOCS-044: contract current, what's new, layers, error codes, no SR-021 claim.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_docs_044_layers_and_whats_new() -> None:
    whats = (ROOT / "docs" / "guides" / "whats-new-0.44.md").read_text(encoding="utf-8")
    contract = (ROOT / "docs" / "api" / "TYPE_DRIVEN_AUTHORING.md").read_text(encoding="utf-8")
    impl = (ROOT / "docs" / "implementation" / "TYPE_DRIVEN_AUTHORING_044.md").read_text(
        encoding="utf-8"
    )
    codes = (ROOT / "docs" / "guides" / "error-codes.md").read_text(encoding="utf-8")
    stability = (ROOT / "docs" / "api" / "STABILITY.md").read_text(encoding="utf-8")
    archive = (ROOT / "docs" / "guides" / "whats-new-archive.md").read_text(encoding="utf-8")
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    header = contract.split("---", 2)[1] if contract.startswith("---") else contract[:200]
    assert "status: historical" in header
    assert "ViewParams" in whats
    assert "FormBody" in whats
    assert "SR-021" not in whats
    assert "HED-TYPE-0001" in codes
    assert "ViewParams" in stability
    assert "whats-new-0.44" in archive
    assert "whats-new-archive" in mkdocs
    assert "functions" in impl.lower() or "function" in contract.lower()
    scaffold = (
        ROOT / "packages" / "hedron" / "src" / "hedron" / "cli" / "scaffold" / "fastapi.py"
    ).read_text(encoding="utf-8")
    assert '@app.view("/status")' in scaffold
    assert "RefreshableView" not in scaffold
