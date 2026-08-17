"""COMPAT-049 / REGRESS-049 upgrade fixtures from Verified 0.48."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel
from tests.unit._helpers_049 import make_app, reset_049

from hedron import FormBody, Text, ViewParams
from hedron_core.research_disposition import EXPERIMENTAL_SYMBOLS
from hedron_core.type_schema import TYPE_SCHEMA_VERSION, TypeSchema, upgrade_type_schema


def setup_function() -> None:
    reset_049()


class Filters(BaseModel):
    q: str = ""


class Mixed(BaseModel):
    item_id: str
    q: str = ""


def test_fixture_expanded_viewparams_still_bind() -> None:
    app = make_app()

    @app.refreshable("/items/{item_id}")
    def item(params: Annotated[Mixed, ViewParams()]):
        return Text(params.item_id)

    payload = item.descriptor.extensions["hedron.type"]
    assert payload["schema_version"] in {1, TYPE_SCHEMA_VERSION}
    assert item.path.endswith("/items/{item_id}")


def test_fixture_query_native_and_v1_upgrade() -> None:
    app = make_app()

    @app.refreshable("/q")
    def search(params: Annotated[Filters, ViewParams(source="query")]):
        return Text(params.q)

    assert search.schema is not None
    v1 = TypeSchema(schema_version=1)
    assert upgrade_type_schema(v1).schema_version == 2


def test_fixture_research_flags_leave_no_symbols() -> None:
    import hedron

    for name in EXPERIMENTAL_SYMBOLS:
        assert name not in hedron.__all__


def test_formbody_and_direct_fastapi_still_work() -> None:
    app = make_app()

    class Body(BaseModel):
        title: str = "ok"

    @app.command(fallback="/")
    def save(data: Annotated[Body, FormBody()]):
        return Text(data.title)

    @app.page("/raw")
    def raw():
        return Text("html")

    assert save.path
    assert any("/raw" in str(getattr(route, "path", "")) for route in app.routes)
