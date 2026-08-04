"""Ensure ``python -m hedron`` is a working PATH-independent CLI entry."""

from __future__ import annotations

import runpy
import sys
from typing import Any


def test_python_m_hedron_invokes_cli(monkeypatch: Any) -> None:
    called: list[list[str]] = []

    def fake_main(argv: list[str] | None = None) -> int:
        called.append(list(argv) if argv is not None else list(sys.argv[1:]))
        return 0

    monkeypatch.setattr("hedron.cli.main", fake_main)
    monkeypatch.setattr(sys, "argv", ["hedron", "--help"])
    try:
        runpy.run_module("hedron", run_name="__main__")
    except SystemExit as exc:
        assert exc.code == 0
    assert called == [["--help"]]
