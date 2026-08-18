"""DOCS-050 provider guide, migration, codes, architecture contract."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_architecture_contract_and_provider_guide() -> None:
    api = (ROOT / "docs/api/EXPLORER_ARCHITECTURE.md").read_text(encoding="utf-8")
    assert "ExplorerProvider" in api
    assert "diagnostics_to_sarif" in api
    assert "/hedron-explorer/" in api
    interaction = (ROOT / "docs/api/INTERACTION.md").read_text(encoding="utf-8")
    assert "ActionHandle.effect" in interaction
    assert "history_restore" in interaction
    assert "ToastHost" in interaction
    codes = (ROOT / "docs/guides/error-codes.md").read_text(encoding="utf-8")
    for code in ("HED-EXPLORER-0001", "HED-EXPLORER-0002", "HED-EXPLORER-0003"):
        assert code in codes


def test_upgrade_and_whats_new() -> None:
    assert (ROOT / "docs/acceptance/upgrade-fixtures-050.md").is_file()
    assert (ROOT / "docs/guides/whats-new-0.50.md").is_file()
    whats = (ROOT / "docs/guides/whats-new-0.50.md").read_text(encoding="utf-8")
    assert "does not tag Git" in whats
