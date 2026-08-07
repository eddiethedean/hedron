"""Unit tests for hedron-sim offline HTMX embeds."""

from __future__ import annotations

import json
import re

from hedron import Page, RefreshButton, Text, html, swap
from hedron_sim import SIM_UTC, SimApp, embed_demo, sim_utc
from hedron_sim.embed import route_table


def _hello_app() -> SimApp:
    app = SimApp(title="Sim test", demo_id="unit-hello")
    status = app.region("service-status")

    def panel():
        return html.div(
            Text(f"up {sim_utc()}"),
            id=status.id,
            role="status",
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            Text("Hello"),
            panel(),
            RefreshButton.for_region(status, href="/status", label="Refresh"),
            title="Home",
        )

    @app.fragment("/status", region=status)
    def refresh():
        return swap(panel())

    return app


def test_embed_demo_includes_real_hx_attrs_and_route_table() -> None:
    html_out = embed_demo(_hello_app())
    assert 'data-hedron-sim="unit-hello"' in html_out
    assert 'hx-get="/status"' in html_out or "hx-get='/status'" in html_out
    assert 'hx-target="#service-status"' in html_out
    assert "hx-swap" in html_out
    assert "data-hedron-sim-routes" in html_out
    assert SIM_UTC in html_out

    match = re.search(
        r'<script type="application/json" data-hedron-sim-routes>(.*?)</script>',
        html_out,
        flags=re.DOTALL,
    )
    assert match is not None
    payload = json.loads(match.group(1))
    assert "GET /status" in payload["routes"]
    route = payload["routes"]["GET /status"]
    assert route["status"] == 200
    assert route["regions"][0]["selector"] == "#service-status"
    assert SIM_UTC in route["html"]
    assert 'id="service-status"' in route["html"]


def test_route_table_allowlist_payload() -> None:
    table = route_table(_hello_app())
    assert table["demoId"] == "unit-hello"
    assert table["routes"]["GET /status"]["regions"][0]["id"] == "service-status"


def test_embed_requires_page() -> None:
    app = SimApp(demo_id="empty")
    try:
        embed_demo(app)
    except ValueError as exc:
        assert "page" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError")
