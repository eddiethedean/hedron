"""hedron / hedron_core must not import hedron_workbench."""

from __future__ import annotations

import sys

import pytest

import hedron
import hedron_core


def test_flagship_does_not_import_workbench() -> None:
    assert "hedron_workbench" not in sys.modules or "hedron_workbench" not in getattr(
        hedron, "__dict__", {}
    )
    assert "hedron_workbench" not in getattr(hedron_core, "__dict__", {})


def test_import_does_not_wrap(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RS_SERVER_URL", "https://wb.example/s/x/")
    monkeypatch.delenv("HEDRON_ROOT_PATH", raising=False)
    import importlib

    import hedron_workbench

    importlib.reload(hedron_workbench)
    assert "HEDRON_ROOT_PATH" not in __import__("os").environ
    assert callable(hedron_workbench.workbenchify)
