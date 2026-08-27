"""Scope hedron check compatibility notices to active surfaces (#54)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hedron.cli import (
    _compat_info_diagnostics,
    _compat_surface_active,
    _registry_has_chart_surface,
)
from hedron_core.registry import register_component, reset_registry_for_tests


@pytest.fixture(autouse=True)
def _fresh_registry() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield
    reset_registry_for_tests()


def _codes(diags: list[object]) -> set[str]:
    return {d.code for d in diags}  # type: ignore[attr-defined]


def test_fastapi_project_skips_django_and_chart_compat(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text(
        "from hedron import Hedron, Page, Text\n"
        "app = Hedron(title='demo', security='standard', explorer='off', session_secret='x')\n"
        "@app.page('/')\n"
        "def home():\n"
        "    return Page(Text('hi'), title='Hi')\n",
        encoding="utf-8",
    )
    assert not _compat_surface_active(
        tmp_path,
        app=None,
        module_roots=frozenset({"django", "hedron_django"}),
        package_tokens=frozenset({"hedron-django"}),
    )
    assert not _compat_surface_active(
        tmp_path,
        app=None,
        module_roots=frozenset({"hedron_charts", "plotly", "altair"}),
        package_tokens=frozenset({"hedron-charts"}),
    )
    codes = _codes(_compat_info_diagnostics(base=tmp_path, app=None, all_compat=False))
    assert "HED-COMPAT-0001" in codes
    assert "HED-COMPAT-0002" not in codes
    assert "HED-COMPAT-0003" not in codes


def test_django_project_emits_django_floor(tmp_path: Path) -> None:
    (tmp_path / "views.py").write_text(
        "from hedron_django import hedron_view\n"
        "from hedron import Page, Text\n"
        "@hedron_view\n"
        "def home(request):\n"
        "    return Page(Text('django'), title='D')\n",
        encoding="utf-8",
    )
    codes = _codes(_compat_info_diagnostics(base=tmp_path, app=None, all_compat=False))
    assert "HED-COMPAT-0001" in codes
    assert "HED-COMPAT-0002" in codes
    assert "HED-COMPAT-0003" not in codes


def test_chart_manifest_and_registry_emit_plotly_notice(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\ndependencies = ["hedron[charts]>=0.27.0,<0.28"]\n',
        encoding="utf-8",
    )
    codes = _codes(_compat_info_diagnostics(base=tmp_path, app=None, all_compat=False))
    assert "HED-COMPAT-0003" in codes
    assert "HED-COMPAT-0002" not in codes

    reset_registry_for_tests()
    register_component(
        logical_id="hedron-charts:demo.BarChart",
        name="BarChart",
        module="demo",
        distribution="hedron-charts",
    )
    assert _registry_has_chart_surface()
    empty = tmp_path / "empty"
    empty.mkdir()
    codes_reg = _codes(_compat_info_diagnostics(base=empty, app=None, all_compat=False))
    assert "HED-COMPAT-0003" in codes_reg


def test_all_compat_emits_global_notices(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('noop')\n", encoding="utf-8")
    codes = _codes(_compat_info_diagnostics(base=tmp_path, app=None, all_compat=True))
    assert {"HED-COMPAT-0001", "HED-COMPAT-0002", "HED-COMPAT-0003"} <= codes


def test_check_json_output_filters_compat(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from hedron.cli import main

    (tmp_path / "pyproject.toml").write_text("[tool.hedron]\n", encoding="utf-8")
    (tmp_path / "app.py").write_text(
        "from hedron import Hedron\n"
        "app = Hedron(title='demo', security='standard', explorer='off', session_secret='x')\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit) as filtered:
        main(["check", "--project", str(tmp_path), "--format", "json"])
    assert filtered.value.code == 0
    payload, _ = json.JSONDecoder().raw_decode(capsys.readouterr().out)
    codes = {item["code"] for item in payload}
    assert "HED-COMPAT-0001" in codes
    assert "HED-COMPAT-0002" not in codes
    assert "HED-COMPAT-0003" not in codes

    with pytest.raises(SystemExit) as all_compat:
        main(["check", "--project", str(tmp_path), "--format", "json", "--all-compat"])
    assert all_compat.value.code == 0
    payload_all, _ = json.JSONDecoder().raw_decode(capsys.readouterr().out)
    codes_all = {item["code"] for item in payload_all}
    assert {"HED-COMPAT-0001", "HED-COMPAT-0002", "HED-COMPAT-0003"} <= codes_all


def test_target_100_json_is_one_document_with_hdj_inventory(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The migration target output must be parseable when HDJ is installed."""
    from hedron.cli import main

    (tmp_path / "pyproject.toml").write_text("[tool.hedron]\n", encoding="utf-8")
    (tmp_path / "status.hdj").write_text(
        '---hdj\nversion = 1\nkind = "fragment"\n---\n<section>ok</section>\n',
        encoding="utf-8",
    )
    (tmp_path / "app.py").write_text(
        "@app.component('/legacy')\ndef legacy(): pass\n", encoding="utf-8"
    )

    with pytest.raises(SystemExit) as result:
        main(
            [
                "check",
                "--target",
                "1.0",
                "--project",
                str(tmp_path),
                "--format",
                "json",
                "--severity",
                "information",
            ]
        )
    assert result.value.code == 1
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, dict)
    assert payload["diagnostics"]
    assert payload["hdj_inventory"]["templates"] == 1
