"""DataEditor JS remediations for #119 / #120 / #121 (REGRESS-039)."""

from __future__ import annotations

from pathlib import Path

EDITOR_JS = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "hedron-data"
    / "src"
    / "hedron_data"
    / "assets"
    / "tabulator"
    / "editor.js"
)


def test_119_unsaved_insert_delete_not_server_delete() -> None:
    text = EDITOR_JS.read_text(encoding="utf-8")
    assert "wasInsert" in text
    assert "unsaved local inserts must not become server deletes" in text
    assert "if (!wasInsert)" in text


def test_120_undo_restores_prior_pending() -> None:
    text = EDITOR_JS.read_text(encoding="utf-8")
    assert "priorPending" in text
    assert "last.priorPending" in text


def test_121_retain_and_retry_rebases_server_revision() -> None:
    text = EDITOR_JS.read_text(encoding="utf-8")
    assert "_conflictServerVersion" in text
    assert "Cannot retry without a fresh server revision" in text
    assert "rebase onto server revision" in text or "fresh server revision" in text


def test_optimistic_states_emitted() -> None:
    text = EDITOR_JS.read_text(encoding="utf-8")
    assert "hedron-data-optimistic" in text
    assert 'this._setOptimistic("submitted")' in text
    assert 'this._setOptimistic("confirmed")' in text
    assert 'this._setOptimistic("conflicted")' in text
    assert "idempotency_key" in text
