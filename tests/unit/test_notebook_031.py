"""NOTEBOOK-031 unit coverage: loopback refusal and compatibility matrix doc."""

from __future__ import annotations

from pathlib import Path

import pytest

from hedron_notebook import start_preview

ROOT = Path(__file__).resolve().parents[2]


class _FakeServer:
    port = 8765

    def start(self) -> None:
        return None

    def shutdown(self) -> None:
        return None


def test_start_preview_refuses_non_loopback() -> None:
    with pytest.raises(ValueError, match="refuses non-loopback"):
        start_preview(object(), host="192.168.1.10", server=_FakeServer())


def test_jupyter_compatibility_matrix_doc_exists() -> None:
    path = ROOT / "docs" / "packages" / "hedron-notebook.md"
    text = path.read_text(encoding="utf-8")
    assert "compatibility" in text.lower() or "Jupyter" in text
    assert "loopback" in text.lower() or "localhost" in text.lower()
