"""DASH-058 evidence."""

from __future__ import annotations

import html
import re

from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from hedron import CachePolicy, DashboardWorkspace, Hedron, Text
from hedron_core.bundles import FeatureBundle


def test_dashboard_workspace_to_bundle() -> None:
    class Filters(BaseModel):
        region: str = "all"
        limit: int = Field(default=5, ge=1, le=50)

    dash = DashboardWorkspace(
        name="sales",
        path="/sales",
        title="Sales",
        filters=Filters,
        load=lambda filters: {"region": filters.region, "total": filters.limit},
        panels={"summary": lambda data: Text(str(data))},
        history="replace",
    )
    bundle = dash.to_bundle()
    assert isinstance(bundle, FeatureBundle)
    assert bundle.logical_id


def test_dashboard_propagates_active_scalar_and_list_filters() -> None:
    class Filters(BaseModel):
        region: str = "all"
        tags: list[str] = []

    seen: list[tuple[str, list[str]]] = []

    def load(filters: Filters) -> dict[str, object]:
        seen.append((filters.region, filters.tags))
        return {"region": filters.region, "tags": filters.tags}

    app = Hedron(
        title="dashboard",
        security="development",
        explorer="off",
        session_secret="test-secret",
    )
    dashboard = DashboardWorkspace(
        name="sales",
        path="/sales",
        title="Sales",
        filters=Filters,
        load=load,
        panels={
            "summary": lambda data: Text(str(data)),
            "detail": lambda data: Text(str(data)),
        },
        cache=CachePolicy(hint="private", ttl_seconds=30),
    )
    app.include(dashboard)
    client = TestClient(app)

    page = client.get("/sales", params=[("region", "a&b=1"), ("tags", "x"), ("tags", "y")])
    assert page.status_code == 200
    assert 'name="region" value="a&amp;b=1"' in page.text
    urls = [html.unescape(value) for value in re.findall(r'hx-get="([^"]+)"', page.text)]
    panel_urls = [value for value in urls if "/sales/panels/" in value]
    assert len(panel_urls) == 2
    assert all("region=a%26b%3D1" in value for value in panel_urls)
    assert all("tags=x&tags=y" in value for value in panel_urls)

    panel = client.get(panel_urls[0])
    assert panel.status_code == 200
    assert panel.headers["cache-control"] == "private, max-age=30"
    assert seen[-1] == ("a&b=1", ["x", "y"])
