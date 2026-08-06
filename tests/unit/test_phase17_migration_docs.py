"""Phase 0.17 migration inventory docs (MIGRATE-017)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_dash_migration_guide_exists() -> None:
    path = ROOT / "docs" / "guides" / "dash-migration.md"
    text = path.read_text(encoding="utf-8")
    assert "DashboardBinding" in text
    assert "automatic" in text.lower()
    assert "MIGRATE-017" in text


def test_nicegui_migration_guide_exists() -> None:
    path = ROOT / "docs" / "guides" / "nicegui-migration.md"
    text = path.read_text(encoding="utf-8")
    assert "DashboardBinding" in text or "InteractionGraph" in text
    assert "run_javascript" in text
    assert "MIGRATE-017" in text or "0.17" in text
