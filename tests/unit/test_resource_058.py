"""RESOURCE-058 evidence."""

from __future__ import annotations

from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from hedron import Hedron
from hedron_core.registry import reset_registry_for_tests
from hedron_data import DataWorkspace, DataWorkspacePolicy, InMemoryDataSource


def _app() -> Hedron:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    return Hedron(
        title="t",
        security="development",
        session_secret="test-secret",
        explorer="off",
    )


def test_workspace_with_screen_stores_meta_and_materializes() -> None:
    class Order(BaseModel):
        id: str
        customer: str = "acme"
        quantity: int = Field(gt=0, le=100)

    source = InMemoryDataSource(
        [{"id": "1", "customer": "acme", "quantity": 2}],
        key_field="id",
        writable_fields=frozenset({"customer", "quantity"}),
        search_fields=(),
    )
    workspace = DataWorkspace(
        name="orders",
        model=Order,
        source=source,
        policy=DataWorkspacePolicy(
            can_read=lambda: True,
            can_create=lambda: True,
            can_edit=lambda: True,
        ),
    ).with_screen(path="/orders", title="Orders", layout="grid")

    assert workspace._screen_meta is not None
    assert workspace._screen_meta["path"] == "/orders"
    assert workspace._screen_meta["title"] == "Orders"

    app = _app()
    bundle = app.include(workspace)
    assert bundle.logical_id
    assert workspace.screen is not None
    response = TestClient(app).get("/orders")
    assert response.status_code == 200
    assert 'data-hedron-layout="grid"' in response.text
    assert 'data-hedron-layout="stack"' not in response.text


def test_in_memory_data_source_constructs() -> None:
    source = InMemoryDataSource([{"id": "a"}], key_field="id", search_fields=())
    assert source is not None
