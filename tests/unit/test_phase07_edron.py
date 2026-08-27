from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from edron.cli import main
from edron.migrate import analyze_source, generate_project
from edron.migrate.codemod import apply_safe_codemod, codemod_file

FIXTURE = Path("tests/fixtures/migrate_streamlit/sales_dashboard/streamlit_app.py")


def test_streamlit_analysis_is_edron_targeted_and_bounded() -> None:
    plan = analyze_source(FIXTURE)
    assert plan.schema_version == "0.7.0-beta"
    assert plan.mapping_catalog_version == "1.60.0-edron-0.7"
    assert plan.streamlit_audit_baseline == "1.60.x"
    assert not plan.tool_errors
    assert any(call.hedron_hint and "self." in call.hedron_hint for call in plan.calls)


def test_cli_analyze_json_has_stable_edron_metadata(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["migrate", "streamlit", str(FIXTURE), "--analyze-only", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["tool"] == "edron migrate streamlit"
    assert payload["target_framework"] == "edron"
    assert payload["schema_version"] == "0.7.0-beta"


def test_generator_is_fresh_edron_project(tmp_path: Path) -> None:
    source_before = FIXTURE.read_bytes()
    plan = analyze_source(FIXTURE)
    out = tmp_path / "migrated"
    hashes = generate_project(plan, out)
    app = (out / "app.py").read_text()
    assert "import edron as ed" in app
    assert "import streamlit" not in app
    assert "from hedron import" not in app
    ast.parse(app)
    assert "edron>=0.9,<0.10" in (out / "pyproject.toml").read_text()
    assert (out / "migration/report.json").is_file()
    assert (out / "migration/source-map.json").is_file()
    assert (out / "migration/REVIEW.md").is_file()
    assert (out / "tests/test_migration_smoke.py").is_file()
    assert hashes["app.py"]
    assert FIXTURE.read_bytes() == source_before


def test_generator_refuses_non_empty_output(tmp_path: Path) -> None:
    out = tmp_path / "existing"
    out.mkdir()
    (out / "keep.txt").write_text("keep")
    with pytest.raises(FileExistsError):
        generate_project(analyze_source(FIXTURE), out)


def test_safe_codemod_preview_and_write(tmp_path: Path) -> None:
    result = apply_safe_codemod('@app.page_function("/")\ndef home():\n    pass\n')
    assert result.changed
    assert "function_page" in result.source
    assert "page_function" not in result.source
    assert not apply_safe_codemod("other.page_function()\n").changed
    source = tmp_path / "source.py"
    destination = tmp_path / "out.py"
    source.write_text("ed.expose(handler)\n")
    written = codemod_file(source, destination)
    assert written.changed
    assert destination.read_text() == "ed.inherit(handler)\n"
    assert source.read_text() == "ed.expose(handler)\n"
