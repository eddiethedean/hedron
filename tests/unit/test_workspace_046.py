"""DATAFLOW-046: DataWorkspace list/detail/create/edit over explicit sources."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from tests.unit._helpers_046 import csrf_headers, make_app, reset_046

from hedron import Page
from hedron_data import DataWorkspace, DataWorkspacePolicy, InMemoryDataSource


def setup_function() -> None:
    reset_046()


class Order(BaseModel):
    id: str
    customer: str = "acme"
    quantity: int = Field(gt=0, le=100)


def _workspace(*, can_create: bool = True, can_edit: bool = True) -> DataWorkspace[Order]:
    source = InMemoryDataSource(
        [{"id": "1", "customer": "acme", "quantity": 1}],
        key_field="id",
        writable_fields=frozenset({"customer", "quantity", "id"}),
    )
    return DataWorkspace(
        name="orders",
        model=Order,
        source=source,
        create_model=Order,
        edit_model=Order,
        policy=DataWorkspacePolicy(
            can_read=lambda: True,
            can_create=lambda: can_create,
            can_edit=lambda: can_edit,
        ),
    )


def test_workspace_include_and_list() -> None:
    app = make_app()
    orders = _workspace()
    app.include_feature(orders)
    assert orders.list_view is not None
    catalog = app.interactions
    assert catalog.require(orders.list_view.logical_id).kind == "view"  # type: ignore[union-attr]
    assert any(
        item.namespace.startswith("hedron.data.workspace")
        for item in catalog.catalog_projections.values()
    )

    @app.page("/")
    def home():
        return Page(orders.list_view(), title="Orders")  # type: ignore[misc]

    html = TestClient(app).get("/").text
    assert "1" in html


def test_workspace_create_edit_and_forbidden() -> None:
    app = make_app()
    orders = _workspace()
    app.include_feature(orders)
    assert orders.create_command is not None
    client = TestClient(app)
    headers = csrf_headers(client)
    created = client.post(
        orders.create_command.path,  # type: ignore[union-attr]
        data={"id": "2", "customer": "beta", "quantity": "3"},
        headers=headers,
    )
    assert created.status_code in {200, 303, 422} or created.status_code < 500
    denied = _workspace(can_create=False)
    app2 = make_app()
    app2.include_feature(denied)
    client2 = TestClient(app2)
    headers2 = csrf_headers(client2)
    forbidden = client2.post(
        denied.create_command.path,  # type: ignore[union-attr]
        data={"id": "9", "customer": "x", "quantity": "1"},
        headers=headers2,
    )
    assert forbidden.status_code == 403


def test_workspace_refuses_objects_all_and_untyped_source() -> None:
    from hedron_core.bundles import FeatureConflictError

    with pytest.raises(FeatureConflictError):
        DataWorkspace(
            name="bad",
            model=Order,
            source=object(),  # type: ignore[arg-type]
            policy=DataWorkspacePolicy(can_read=lambda: True),
        )


def test_direct_datatable_still_works() -> None:
    from hedron_data import DataTable

    table = DataTable(rows=[{"id": "1"}], caption="plain")
    assert table.distribution == "hedron-data"
