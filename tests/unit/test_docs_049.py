"""DOCS-049 packet, public contract, codes, tracking."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_tracking_issue_bound() -> None:
    for rel in (
        "docs/acceptance/RELEASE_0_49.md",
        "STATUS.md",
        "docs/ROADMAP.md",
        "docs/TRACEABILITY.md",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "#380" in text


def test_public_contract_and_guides() -> None:
    api = (ROOT / "docs/api/FASTAPI_PYDANTIC_CONVERGENCE.md").read_text(encoding="utf-8")
    assert "DependsOn" in api
    assert "BoundaryBindingPlan" in api
    assert "RequiresScopes" in api
    codes = (ROOT / "docs/guides/error-codes.md").read_text(encoding="utf-8")
    for code in (
        "HED-FP-0001",
        "HED-FP-0002",
        "HED-FP-0003",
        "HED-FP-0004",
        "HED-FP-0005",
        "HED-FP-0006",
        "HED-FP-0007",
        "HED-FP-0008",
        "HED-TYPE-0001",
    ):
        assert code in codes
    for rel in (
        "docs/guides/whats-new-0.49.md",
        "docs/api/FASTAPI_PYDANTIC_CONVERGENCE.md",
        "examples/fastapi-pydantic/README.md",
    ):
        assert (ROOT / rel).is_file(), rel
