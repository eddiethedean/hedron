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
    assert orders.edit_command is not None
    assert orders.list_view is not None

    @app.page("/")
    def home():
        return Page(orders.list_view(), title="Orders")  # type: ignore[misc]

    client = TestClient(app)

    created = client.post(
        orders.create_command.path,  # type: ignore[union-attr]
        data={"id": "2", "customer": "beta", "quantity": "3"},
        headers=csrf_headers(client),
    )
    assert created.status_code in {200, 303}
    listed = client.get(orders.list_view.path).text  # type: ignore[union-attr]
    assert "beta" in listed and "2" in listed

    edited = client.post(
        orders.edit_command.path,  # type: ignore[union-attr]
        data={"id": "2", "customer": "gamma", "quantity": "4"},
        headers=csrf_headers(client),
    )
    assert edited.status_code in {200, 303}
    assert "gamma" in client.get(orders.list_view.path).text  # type: ignore[union-attr]

    denied = _workspace(can_create=False, can_edit=False)
    app2 = make_app()
    app2.include_feature(denied)

    @app2.page("/")
    def home_denied():
        return Page(denied.list_view(), title="Denied")  # type: ignore[misc]

    client2 = TestClient(app2)
    assert (
        client2.post(
            denied.create_command.path,  # type: ignore[union-attr]
            data={"id": "9", "customer": "x", "quantity": "1"},
            headers=csrf_headers(client2),
        ).status_code
        == 403
    )
    assert (
        client2.post(
            denied.edit_command.path,  # type: ignore[union-attr]
            data={"id": "1", "customer": "nope", "quantity": "2"},
            headers=csrf_headers(client2),
        ).status_code
        == 403
    )


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


def test_workspace_policy_hook_accepts_user_and_denies_mismatch() -> None:
    seen: list[object] = []

    def can_read(user: str) -> bool:
        seen.append(user)
        return user == "ada"

    ws = DataWorkspace(
        name="notes",
        model=Order,
        source=InMemoryDataSource([{"id": "1", "customer": "acme", "quantity": 1}], key_field="id"),
        policy=DataWorkspacePolicy(can_read=can_read),
    )
    assert ws._allowed(can_read, user="ada") is True
    assert seen == ["ada"]
    assert ws._allowed(can_read) is False
    assert ws._allowed(lambda: True) is True


def test_workspace_list_pages_sorts_filters_and_searches() -> None:
    app = make_app()
    rows = [{"id": f"{i:02d}", "customer": f"c{i:02d}", "quantity": 1} for i in range(40)]
    ws = DataWorkspace(
        name="orders",
        model=Order,
        source=InMemoryDataSource(
            rows,
            key_field="id",
            search_fields=("customer", "id"),
        ),
        policy=DataWorkspacePolicy(can_read=lambda: True),
    )
    app.include_feature(ws)
    client = TestClient(app)
    path = ws.list_view.path  # type: ignore[union-attr]
    first = client.get(path)
    assert first.status_code == 200
    assert "c00" in first.text
    assert "c24" in first.text
    assert "c25" not in first.text
    second = client.get(path, params={"offset": 25})
    assert second.status_code == 200
    assert "c25" in second.text
    assert "c00" not in second.text
    last = client.get(path, params={"sort": "customer:desc", "limit": 1})
    assert last.status_code == 200
    assert "c39" in last.text
    found = client.get(path, params={"q": "c03"})
    assert found.status_code == 200
    assert "c03" in found.text
    assert "c04" not in found.text
    filtered = client.get(path, params={"customer": "c10"})
    assert filtered.status_code == 200
    assert "c10" in filtered.text
    assert "c11" not in filtered.text
    bad = client.get(path, params={"sort": "nope"})
    assert bad.status_code == 422
