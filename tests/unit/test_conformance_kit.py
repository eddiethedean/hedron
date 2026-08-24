"""CONFORM-014: published kit runner and normalization."""

from __future__ import annotations

from hedron_conformance import normalize_html, run_kit
from hedron_conformance.cli import main
from hedron_conformance.schema import load_bundled_fixtures


def test_bundled_fixtures_pass_reference_runner() -> None:
    report = run_kit()
    assert report.ok, [f.detail for f in report.failures()]
    assert len(report.results) >= 10
    assert all(cap.ok for cap in report.by_capability.values())


def test_normalize_html_v1() -> None:
    assert normalize_html("  <p>x</p>  ") == "<p>x</p>"
    assert normalize_html("<div>\n  <span>a</span>\n</div>") == "<div><span>a</span></div>"


def test_cli_run_exits_zero() -> None:
    assert main(["run"]) == 0


def test_cli_theme_contract_exits_zero(capsys) -> None:
    assert main(["theme", "--name", "default"]) == 0
    assert '"schema": "hedron.theme-contract/1"' in capsys.readouterr().out


def test_load_fixtures_have_contract_version() -> None:
    fixtures = load_bundled_fixtures()
    assert fixtures
    assert all(f.contract_version == "hedron-portable-1" for f in fixtures)
