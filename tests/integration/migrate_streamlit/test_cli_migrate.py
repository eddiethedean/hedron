"""CLI integration for hedron migrate streamlit."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hedron.cli import main

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "migrate_streamlit"
    / "sales_dashboard"
    / "streamlit_app.py"
)


def test_migrate_generate_sales_dashboard(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "sales_out"
    with pytest.raises(SystemExit) as result:
        main(
            [
                "migrate",
                "streamlit",
                str(FIXTURE),
                "--out",
                str(out),
                "--format",
                "json",
            ]
        )
    assert result.value.code in {0, 2}
    payload = json.loads(capsys.readouterr().out)
    assert payload["page_title"] == "Sales dashboard"
    assert (out / "app.py").is_file()
    app_text = (out / "app.py").read_text(encoding="utf-8")
    assert "from hedron import" in app_text
    assert "import streamlit" not in app_text
    assert "Sales dashboard" in app_text
    assert "DataTable" in app_text


def test_sarif_uses_shared_adapter(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        main(
            [
                "migrate",
                "streamlit",
                str(FIXTURE),
                "--analyze-only",
                "--format",
                "sarif",
            ]
        )
    payload = json.loads(capsys.readouterr().out)
    assert payload["version"] == "2.1.0"
    assert payload["runs"][0]["tool"]["driver"]["name"] == "hedron"
