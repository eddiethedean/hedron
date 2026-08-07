"""Guard documented CLI snippets against flag-placement regressions."""

from __future__ import annotations

from pathlib import Path

import pytest

from hedron.cli import main

ROOT = Path(__file__).resolve().parents[2]
QUICKSTART = ROOT / "docs" / "getting-started" / "quickstart.md"


def test_quickstart_documents_global_app_before_check() -> None:
    text = QUICKSTART.read_text(encoding="utf-8")
    assert "python -m hedron --app app:app check" in text
    assert "uv run hedron --app app:app check" in text
    # Wrong placement (subcommand then --app) must not reappear in adopter docs.
    assert "hedron check --app" not in text
    assert "python -m hedron check --app" not in text


def test_cli_rejects_app_flag_after_check_subcommand() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["check", "--app", "app:app"])
    assert excinfo.value.code == 2
