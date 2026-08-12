"""Analyze-only path and Streamlit-free packaging guarantees."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hedron.cli import main
from hedron.migrate.analyze import analyze_source

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "migrate_streamlit"
    / "sales_dashboard"
    / "streamlit_app.py"
)


def test_analyze_sales_dashboard_no_drop() -> None:
    plan = analyze_source(FIXTURE)
    assert not plan.tool_errors
    assert plan.calls
    assert all(c.disposition for c in plan.calls)
    symbols = {c.symbol for c in plan.calls}
    assert "st.title" in symbols
    assert "st.selectbox" in symbols
    assert "st.slider" in symbols
    assert "st.metric" in symbols
    assert "st.line_chart" in symbols
    assert "st.dataframe" in symbols
    assert "st.cache_data" in symbols


def test_analyze_only_cli_json(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as result:
        main(
            [
                "migrate",
                "streamlit",
                str(FIXTURE),
                "--analyze-only",
                "--format",
                "json",
            ]
        )
    # Default fail-on=error: warnings from scaffolded APIs do not force exit 2
    assert result.value.code in {0, 2}
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"]
    assert payload["calls"]
    assert "findings" in payload


def test_works_without_streamlit_installed() -> None:
    """Migrator modules must not import Streamlit (packaging / optional dep)."""
    import ast
    from pathlib import Path

    migrate_root = Path(__file__).resolve().parents[3] / "packages" / "hedron" / "src" / "hedron" / "migrate"
    for path in migrate_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "streamlit" and not alias.name.startswith(
                        "streamlit."
                    ), path
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module != "streamlit" and not node.module.startswith(
                    "streamlit."
                ), path
    plan = analyze_source(FIXTURE)
    assert not plan.tool_errors
    assert plan.calls
