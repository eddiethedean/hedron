"""Packaged 0.49 FastAPI/Pydantic convergence sample."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel

from hedron import FormBody, Hedron, Page, RequiresScopes, Text, ViewParams

app = Hedron(title="FastAPI/Pydantic", explorer="off", session_secret="dev-secret")


class Filters(BaseModel):
    q: str = ""


class Item(BaseModel):
    item_id: str
    q: str = ""


class Payload(BaseModel):
    title: str = "ok"


@app.page("/")
def home() -> Page:
    return Page(Text("0.49 lifetimes, binding, and TypeSchema v2."), title="FastAPI/Pydantic")


@app.view("/items")
def items(filters: Annotated[Filters, ViewParams(source="query")]):
    return Text(filters.q or "all")


@app.view("/items/{item_id}")
def item(params: Annotated[Item, ViewParams()]):
    return Text(params.item_id)


@app.action("/save", fallback="/", authorization=RequiresScopes("write"))
def save(data: Annotated[Payload, FormBody()]):
    return Text(data.title)
