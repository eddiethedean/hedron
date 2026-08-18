"""Request-level coverage for the 0.49 typed FastAPI boundary."""

from __future__ import annotations

from typing import Annotated

from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from tests.unit._helpers_049 import make_app, reset_049

from hedron import Text, ViewParams


def setup_function() -> None:
    reset_049()


class SearchParams(BaseModel):
    query: str = "all"
    limit: int = Field(default=10, ge=1, le=100)


def _search_app():
    app = make_app()

    @app.refreshable("/search", include_in_schema=True)
    def search(params: Annotated[SearchParams, ViewParams(source="query")]):
        return Text(f"{params.query}:{params.limit}")

    return app


def test_native_query_model_is_parsed_by_real_http_route() -> None:
    app = _search_app()

    with TestClient(app) as client:
        explicit = client.get("/search", params={"query": "widgets", "limit": "3"})
        defaults = client.get("/search")

    assert explicit.status_code == 200
    assert "<p>widgets:3</p>" in explicit.text
    assert 'hx-get="/search"' in explicit.text
    assert explicit.headers["content-type"].startswith("text/html")
    assert defaults.status_code == 200
    assert "<p>all:10</p>" in defaults.text


def test_native_query_model_reports_field_level_validation_errors() -> None:
    app = _search_app()

    with TestClient(app) as client:
        non_integer = client.get("/search", params={"limit": "many"})
        out_of_range = client.get("/search", params={"limit": "101"})

    assert non_integer.status_code == 422
    assert non_integer.json()["detail"][0]["loc"] == ["query", "limit"]
    assert non_integer.json()["detail"][0]["type"] == "int_parsing"
    assert out_of_range.status_code == 422
    assert out_of_range.json()["detail"][0]["loc"] == ["query", "limit"]
    assert out_of_range.json()["detail"][0]["type"] == "less_than_equal"


def test_openapi_and_runtime_share_the_same_query_contract() -> None:
    app = _search_app()
    operation = app.openapi()["paths"]["/search"]["get"]

    parameters = {item["name"]: item for item in operation["parameters"]}
    assert set(parameters) == {"query", "limit"}
    assert parameters["query"]["in"] == "query"
    assert parameters["limit"]["schema"]["maximum"] == 100
    assert "requestBody" not in operation
    assert "text/html" in operation["responses"]["200"]["content"]
    assert operation["x-hedron-kind"] == "component"
