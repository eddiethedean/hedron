"""Evidence-only: DOCS-046 inventory / substring presence — not product behavior.

DOCS-046: package workflow contract is current; what's-new; no SR-021 claim.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_docs_046_layers_and_whats_new() -> None:
    contract = (ROOT / "docs" / "api" / "PACKAGE_WORKFLOWS.md").read_text(encoding="utf-8")
    impl = (ROOT / "docs" / "implementation" / "PACKAGE_NATIVE_WORKFLOWS_046.md").read_text(
        encoding="utf-8"
    )
    whats = (ROOT / "docs" / "guides" / "whats-new-0.46.md").read_text(encoding="utf-8")
    codes = (ROOT / "docs" / "guides" / "error-codes.md").read_text(encoding="utf-8")
    stability = (ROOT / "docs" / "api" / "STABILITY.md").read_text(encoding="utf-8")
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    header = contract.split("---", 2)[1] if contract.startswith("---") else contract[:240]
    assert "status: current" in header or "FeatureBundle" in contract
    assert "FeatureBundle" in whats
    assert "DataWorkspace" in whats
    assert "SR-021" not in whats
    assert "HED-BUNDLE-0001" in codes
    assert "FeatureBundle" in stability or "PACKAGE_WORKFLOWS" in stability or "0.46" in stability
    assert "whats-new-archive" in mkdocs
    assert "whats-new-0.46" in (ROOT / "docs" / "guides" / "whats-new-archive.md").read_text(
        encoding="utf-8"
    )
    assert "include_feature" in impl
    assert "#334" in (ROOT / "docs" / "acceptance" / "RELEASE_0_46.md").read_text(encoding="utf-8")
