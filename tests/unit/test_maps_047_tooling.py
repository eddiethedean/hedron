"""TOOLING-047 Explorer maps panel and plan facts."""

from __future__ import annotations

from tests.unit._helpers_046 import make_app, with_client

from hedron_explorer.router import explorer_router
from hedron_maps import Map
from hedron_maps.facts import plan_facts


def test_plan_facts_do_not_execute() -> None:
    plan = Map(title="Inspect", description="Facts").compile_plan()
    facts = plan_facts(plan)
    assert facts["executes_untrusted_data"] is False
    assert facts["preset_id"] == "openstreetmap-standard"
    assert facts["fallback_class"] == "hedron-map-alternative"


def test_explorer_maps_route() -> None:
    paths = [getattr(route, "path", "") for route in explorer_router().routes]
    assert "/maps" in paths

    def _check(client) -> None:
        response = client.get("/hedron-explorer/maps")
        assert response.status_code == 200
        assert b"without executing untrusted map data" in response.content
        assert b"viewport-changed" in response.content

    from hedron import Page, Text

    app = make_app(explorer="development")

    @app.page("/")
    def home():
        return Page(Text("ok"), title="Home")

    with_client(app, _check)
