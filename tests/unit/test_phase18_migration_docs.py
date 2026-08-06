"""Phase 0.18 migration inventory docs (MIGRATE-018)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_gradio_migration_guide_exists() -> None:
    path = ROOT / "docs" / "guides" / "gradio-migration.md"
    text = path.read_text(encoding="utf-8")
    assert "MIGRATE-018" in text
    assert "InferenceInterface" in text
    assert "PredictionFeedback" in text
    assert "deliberate non-parity" in text.lower() or "Deliberate non-parity" in text
    assert "share" in text.lower()
    assert "automatic" in text.lower()


def test_whats_new_0_18_exists() -> None:
    path = ROOT / "docs" / "guides" / "whats-new-0.18.md"
    text = path.read_text(encoding="utf-8")
    assert "0.18" in text
    assert "InferencePolicy" in text or "ModelDemo" in text
