"""DX-029 CLI check / dry-run (no listener)."""

from __future__ import annotations

import json

import pytest

from hedron_workbench.cli import main


def test_check_text() -> None:
    assert main(["check", "--format", "text", "--mode", "off"]) == 0


def test_check_json(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["check", "--format", "json", "--mount", "/s/demo/p/9"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["browser_mount"] == "/s/demo/p/9"
    assert payload["cookie_mount"] == "/s/demo/p/9"


def test_dry_run_alias() -> None:
    assert main(["dry-run", "--mode", "off"]) == 0


def test_external_bind_requires_flag(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["check", "--host", "0.0.0.0"]) == 1
    assert "HED-WB-0001" in capsys.readouterr().err
    assert main(["check", "--host", "0.0.0.0", "--allow-external-bind"]) == 0


def test_bad_worker_count_is_diagnostic(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["check", "--workers", "0"]) == 1
    assert "HED-WB-0001" in capsys.readouterr().err
