"""VISUAL-046: ChartInteraction Supported events and bounds."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel
from tests.unit._helpers_046 import csrf_headers, make_app, reset_046

from hedron import Text
from hedron_charts import ChartInteraction
from hedron_core.bundles import FeatureConflictError
from hedron_core.codes import HED_BUNDLE_0005, HED_BUNDLE_0007


def setup_function() -> None:
    reset_046()


class Selection(BaseModel):
    ids: list[str]


def test_supported_select_compiles_to_export_command() -> None:
    app = make_app()

    @app.command("/filter")
    def filter_sales(payload: Selection):
        return Text(str(len(payload.ids)))

    @app.refreshable
    def sales_table():
        return Text("table")

    binding = ChartInteraction(
        chart=sales_table,
        event="select",
        payload=Selection,
        command=filter_sales,
        refreshes=(sales_table,),
        max_items=10,
        name="tests:sales-select",
    )
    app.include_feature(binding)
    catalog = app.interactions
    assert catalog.require(filter_sales.logical_id).kind == "command"
    assert any(
        item.namespace.startswith("hedron.charts.interaction")
        for item in catalog.catalog_projections.values()
    )


def test_select_event_invokes_bound_command() -> None:
    app = make_app()
    seen: list[list[str]] = []

    @app.command("/filter")
    def filter_sales(payload: Selection):
        seen.append(list(payload.ids))
        return Text(str(len(payload.ids)))

    @app.refreshable
    def sales_table():
        return Text("table")

    live = app.include_feature(
        ChartInteraction(
            chart=sales_table,
            event="select",
            payload=Selection,
            command=filter_sales,
            refreshes=(sales_table,),
            name="tests:sales-select",
        )
    )

    @app.page("/")
    def home():
        return Text("home")

    event_handle = live.commands[0]
    client = TestClient(app)
    posted = client.post(
        event_handle.path,
        json={"ids": ["east", "west"]},
        headers=csrf_headers(client),
    )
    assert posted.status_code == 200
    assert seen == [["east", "west"]]
    assert getattr(live.commands[1], "name", "").endswith("-export") or any(
        "export" in str(getattr(item, "logical_id", "")) for item in live.commands
    )


def test_experimental_event_requires_flag() -> None:
    app = make_app()

    @app.command("/brush")
    def on_brush(payload: Selection):
        return Text("ok")

    with pytest.raises(FeatureConflictError) as raised:
        ChartInteraction(
            chart=object(),
            event="brush",
            payload=Selection,
            command=on_brush,
        )
    assert raised.value.diagnostic.code == HED_BUNDLE_0007


def test_fanout_and_cardinality_bounds() -> None:
    app = make_app()

    @app.command("/sel")
    def on_select(payload: Selection):
        return Text("ok")

    with pytest.raises(FeatureConflictError) as items:
        ChartInteraction(
            chart=object(),
            event="select",
            payload=Selection,
            command=on_select,
            max_items=1001,
        )
    assert items.value.diagnostic.code == HED_BUNDLE_0005
    with pytest.raises(FeatureConflictError) as fan:
        ChartInteraction(
            chart=object(),
            event="select",
            payload=Selection,
            command=on_select,
            refreshes=tuple(object() for _ in range(33)),
        )
    assert fan.value.diagnostic.code == HED_BUNDLE_0005
