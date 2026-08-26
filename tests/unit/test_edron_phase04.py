"""PHASE-EDRON-04: visualizations, typed links, fallbacks, and media."""

from __future__ import annotations

from pydantic import BaseModel
from starlette.testclient import TestClient

import edron as ed
from hedron_charts import Chart, beginner_to_spec
from hedron_maps import FeatureSelected, Map


class ChartSelection(BaseModel):
    ids: list[str]


def _chart() -> Chart:
    spec = beginner_to_spec(
        kind="bar",
        data=[{"month": "Jan", "revenue": 10}],
        x="month",
        y="revenue",
        title="Revenue",
        description="Revenue by month",
    )
    return Chart(spec=spec)


def test_page_visualization_and_media_helpers_keep_native_fallbacks() -> None:
    app = ed.App(title="Visuals", session_secret="test")

    @app.page("/", title="Visuals")
    class Visuals(ed.Page):
        def render(self) -> None:
            self.chart(_chart(), alternative="Use the table below for exact values.")
            self.map(title="Locations", description="Locations by region", alternative="Map list")
            self.image("/assets/hero.png", alt="A sales trend illustration")
            self.audio(
                "/media/summary.mp3",
                tracks=(
                    {
                        "kind": "transcript",
                        "language": "en",
                        "reviewed": True,
                    },
                ),
            )
            self.video(
                "/media/brief.mp4",
                poster="/assets/poster.png",
                tracks=(
                    {
                        "kind": "captions",
                        "language": "en",
                        "src": "/media/brief.vtt",
                        "reviewed": True,
                    },
                ),
            )

    response = TestClient(app.native, raise_server_exceptions=False).get("/")
    assert response.status_code == 200
    assert "hedron-chart-fallback" in response.text
    assert "hedron-map-alternative" in response.text
    assert "Use the table below" in response.text
    assert 'alt="A sales trend illustration"' in response.text
    assert "summary.mp3" in response.text
    assert "brief.vtt" in response.text


def test_image_requires_meaningful_alt_text() -> None:
    app = ed.App(title="Visuals", session_secret="test")

    @app.page("/", title="Visuals")
    class Visuals(ed.Page):
        def render(self) -> None:
            self.image("/assets/hero.png", alt="")

    response = TestClient(app.native, raise_server_exceptions=False).get("/")
    assert response.status_code == 500


def test_chart_interaction_resolves_edron_action_and_is_explained() -> None:
    app = ed.App(title="Linked chart", session_secret="test")
    seen: list[list[str]] = []

    @app.page("/", title="Linked chart")
    class Dashboard(ed.Page):
        @ed.action
        def select(self, payload: ChartSelection) -> ed.Outcome:
            seen.append(payload.ids)
            return ed.success("selected")

        def render(self) -> None:
            self.chart(_chart())

    chart = _chart()
    bundle = app.chart_interaction(
        chart,
        event="select",
        payload=ChartSelection,
        command=Dashboard.select,
        max_items=2,
        name="dashboard-selection",
    )
    facts = app.explain()
    assert facts["visual_interactions"][0]["logical_id"] == bundle.logical_id
    assert facts["visual_interactions"][0]["provider"] == "hedron-charts"

    client = TestClient(app.native)
    page = client.get("/")
    assert page.status_code == 200
    token = page.cookies.get("hedron_csrf")
    assert token
    event = bundle.commands[0]
    response = client.post(
        event.path,
        json={"ids": ["north", "south"]},
        headers={"X-CSRF-Token": token},
    )
    assert response.status_code == 200
    assert seen == [["north", "south"]]


def test_map_interaction_promotes_native_map_event_contract() -> None:
    app = ed.App(title="Linked map", session_secret="test")

    @app.page("/", title="Linked map")
    class Dashboard(ed.Page):
        @ed.action
        def select(self, payload: FeatureSelected) -> ed.Outcome:
            return ed.success(str(payload.ids))

        def render(self) -> None:
            self.map(title="Locations", description="Locations")

    map_node = Map(title="Locations", description="Locations")
    bundle = app.map_interaction(
        map_node,
        event="feature-selected",
        payload=FeatureSelected,
        command=Dashboard.select,
        name="location-selection",
    )
    assert bundle.provider == "hedron-maps"
    assert map_node._interaction_commands["feature-selected"].endswith(
        "/maps/location-selection/feature-selected"
    )
