"""PARITY-054 evidence: simulator vs real-server differential fixtures."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron import Page, html, swap
from hedron_sim import (
    PARITY_FIXTURES,
    PARITY_SCHEMA,
    SimApp,
    compare_parity,
    embed_demo,
    normalize_parity_html,
    render_handler_html,
    sim_utc,
)

ROOT = Path(__file__).resolve().parents[2]

# (fixture, simulated HTML, real-server HTML) — whitespace differs, meaning must not.
PARITY_CASES: tuple[tuple[str, str, str], ...] = (
    (
        "package_workflows",
        '<div id="out">\n  <p>Queued</p>\n</div>',
        '<div id="out"><p>Queued</p></div>',
    ),
    (
        "validation_failures",
        '<p role="alert">   Enter a valid email.   </p>',
        '<p role="alert">Enter a valid email.</p>',
    ),
    (
        "navigation",
        '<nav><a href="/reports">Reports</a>\n<a href="/jobs">Jobs</a></nav>',
        '<nav><a href="/reports">Reports</a><a href="/jobs">Jobs</a></nav>',
    ),
    (
        "asset_lifecycle",
        '<link rel="stylesheet" href="/assets/app.css">\n<script src="/assets/app.js"></script>',
        '<link rel="stylesheet" href="/assets/app.css"><script src="/assets/app.js"></script>',
    ),
)


def test_parity_054_packet_bound() -> None:
    gate = tomllib.loads(
        (ROOT / "docs" / "acceptance" / "release-gate-0.54.toml").read_text(encoding="utf-8")
    )
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["PARITY-054"]["command"] == "python scripts/check_parity_054.py"
    locks = tomllib.loads(
        (ROOT / "docs" / "acceptance" / "authoring-sim-notebook-054.toml").read_text(
            encoding="utf-8"
        )
    )
    assert sorted(locks["parity"]["fixtures"]) == sorted(PARITY_FIXTURES)


def test_parity_ok_on_equal_html() -> None:
    html = '<div id="out"><p>Ready</p></div>'
    result = compare_parity(html, html)
    assert result["ok"] is True
    assert result["differences"] == []
    assert result["schema_version"] == PARITY_SCHEMA


def test_parity_ignores_trivial_whitespace_across_fixtures() -> None:
    for fixture, sim_html, server_html in PARITY_CASES:
        result = compare_parity(sim_html, server_html, fixture=fixture)
        assert result["fixture"] == fixture
        assert result["ok"] is True, result["differences"]
        assert result["differences"] == []


def test_parity_reports_real_divergence() -> None:
    result = compare_parity(
        '<div id="out"><p>Queued</p></div>',
        '<div id="out"><p>Running</p></div>',
    )
    assert result["ok"] is False
    difference = result["differences"][0]
    assert difference["op"] == "replace"
    assert difference["sim"] == "Queued"
    assert difference["server"] == "Running"


def test_parity_reports_missing_and_extra_markup() -> None:
    missing = compare_parity("<ul><li>a</li></ul>", "<ul><li>a</li><li>b</li></ul>")
    assert missing["ok"] is False
    assert [row["op"] for row in missing["differences"]] == ["insert"]

    extra = compare_parity("<ul><li>a</li><li>b</li></ul>", "<ul><li>a</li></ul>")
    assert extra["ok"] is False
    assert [row["op"] for row in extra["differences"]] == ["delete"]


def test_sim_placeholders_normalize_but_content_still_compares() -> None:
    sim_html = f"<p>{sim_utc()}</p>"
    assert "{sim-placeholder}" in normalize_parity_html(sim_html)
    # Opting out keeps the raw token, which is a real divergence from a server render.
    strict = compare_parity(sim_html, "<p>12:00:00 UTC</p>", placeholders=False)
    assert strict["ok"] is False


def test_rendered_fragment_matches_its_server_side_render() -> None:
    app = SimApp(title="parity demo")
    region = app.region("out", description="Result panel")

    def panel(label: str) -> object:
        return html.div(html.p(label), id=region.id, role="status")

    @app.page("/")
    def home() -> Page:
        return Page(panel("Ready"), title="Home")

    @app.fragment("/run", region=region)
    def run() -> object:
        return swap(panel("Ready"))

    # The simulated fragment and the same handler rendered "server side" agree.
    sim_html = render_handler_html(run())
    server_html = render_handler_html(panel("Ready"))
    result = compare_parity(sim_html, server_html, fixture="package_workflows")
    assert result["ok"] is True, result["differences"]
    assert "Ready" in embed_demo(app)
