"""Upgrade fixtures: public fastapi-workbench 0.3.4 → monorepo 1.0.0."""

from __future__ import annotations

from pathlib import Path


def test_provenance_030_documents_monorepo_ownership() -> None:
    path = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "acceptance"
        / "fastapi-workbench-provenance-030.toml"
    )
    text = path.read_text(encoding="utf-8")
    assert "fastapi-workbench" in text
    assert "1.0.0" in text or "monorepo" in text.lower()


def test_fastapi_workbench_cli_entrypoint() -> None:
    pyproject = (
        Path(__file__).resolve().parents[2] / "packages" / "fastapi-workbench" / "pyproject.toml"
    )
    assert "fastapi-workbench = " in pyproject.read_text(encoding="utf-8")
