"""Refuse overwrite and generation smoke."""

from __future__ import annotations

from pathlib import Path

import pytest

from hedron.cli import main
from hedron.migrate.analyze import analyze_source
from hedron.migrate.generate import generate_project

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "migrate_streamlit"
    / "sales_dashboard"
    / "streamlit_app.py"
)


def test_refuse_nonempty_out(tmp_path: Path) -> None:
    out = tmp_path / "dest"
    out.mkdir()
    (out / "existing.txt").write_text("nope", encoding="utf-8")
    with pytest.raises(SystemExit) as result:
        main(
            [
                "migrate",
                "streamlit",
                str(FIXTURE),
                "--out",
                str(out),
            ]
        )
    assert result.value.code == 1
    assert (out / "existing.txt").read_text(encoding="utf-8") == "nope"
    assert FIXTURE.read_bytes()  # source untouched


def test_source_byte_identical_after_generate(tmp_path: Path) -> None:
    before = FIXTURE.read_bytes()
    out = tmp_path / "hedron_app"
    plan = analyze_source(FIXTURE)
    generate_project(plan, out)
    assert FIXTURE.read_bytes() == before
    assert (out / "app.py").is_file()
    assert (out / "pyproject.toml").is_file()
    assert (out / "migration" / "report.json").is_file()
    assert (out / "migration" / "source-map.json").is_file()
    assert (out / "migration" / "REVIEW.md").is_file()
    assert (out / "tests" / "test_migration_smoke.py").is_file()
    pyproject = (out / "pyproject.toml").read_text(encoding="utf-8")
    assert "hedron" in pyproject
    assert "streamlit" not in pyproject
