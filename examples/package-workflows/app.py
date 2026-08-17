"""Reference FastAPI app combining a DataWorkspace, ChartInteraction, and enhanced form."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

from hedron import Control, FormBody, Hedron, Page, Text
from hedron_charts import ChartInteraction
from hedron_data import DataWorkspace, DataWorkspacePolicy, InMemoryDataSource


class Order(BaseModel):
    id: str
    customer: str = "acme"
    quantity: int = Field(gt=0, le=100)


class Selection(BaseModel):
    ids: list[str] = Field(default_factory=list)


app = Hedron(title="package-workflows-046", explorer="development")

orders = DataWorkspace(
    name="orders",
    model=Order,
    source=InMemoryDataSource(
        [{"id": "1", "customer": "acme", "quantity": 2}],
        key_field="id",
        writable_fields=frozenset({"customer", "quantity"}),
    ),
    policy=DataWorkspacePolicy(
        can_read=lambda: True,
        can_create=lambda: True,
        can_edit=lambda: True,
    ),
)
app.include_feature(orders)


@app.command("/filter-orders")
def filter_orders(payload: Selection):
    return Text(f"selected {len(payload.ids)}")


app.include_feature(
    ChartInteraction(
        chart=orders.list_view,
        event="select",
        payload=Selection,
        command=filter_orders,
        refreshes=(orders.list_view,) if orders.list_view is not None else (),
        name="demo:orders-select",
    )
)


class NoteIn(BaseModel):
    title: Annotated[str, Control(kind="text", label="Title")]
    kind: Literal["work", "personal"] = "work"


@app.command("/notes", fallback="/")
def add_note(data: Annotated[NoteIn, FormBody()]):
    return Text(data.title)


@app.page("/")
def home():
    return Page(
        orders.list_view(),  # type: ignore[misc]
        add_note.form(enhance="elements"),
        title="Orders",
    )
