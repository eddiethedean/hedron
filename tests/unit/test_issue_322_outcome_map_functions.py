"""#322: OutcomeMap on function commands; skip inspect.Parameter.empty."""

from __future__ import annotations

import inspect
from typing import Annotated, Literal

from fastapi.testclient import TestClient
from pydantic import BaseModel
from tests.unit._helpers_044 import make_app, reset_044

from hedron import FormBody, OutcomeMap, Page, Text, case
from hedron.type_authoring.outcomes import _union_variants


def setup_function() -> None:
    reset_044()


class Flags(BaseModel):
    urgent: bool = False


class Saved(BaseModel):
    kind: Literal["saved"] = "saved"
    id: str


def test_empty_annotation_is_not_a_union_variant() -> None:
    assert _union_variants(inspect.Parameter.empty) == ()


def test_function_command_outcomes_map_status() -> None:
    app = make_app()
    mapping = OutcomeMap(case(Saved, render=lambda item: Text(f"ok:{item.id}"), status=409))

    @app.page("/")
    def home():
        return Page(Text("h"), title="Home")

    @app.command(fallback="/", outcomes=mapping)
    def save_it(data: Annotated[Flags, FormBody()]) -> Saved:
        return Saved(id="9")

    client = TestClient(app)
    token = client.get("/").cookies.get("hedron_csrf") or ""
    response = client.post(
        save_it.path,
        data={"urgent": "false"},
        headers={"X-CSRF-Token": token, "HX-Request": "true"},
    )
    assert response.status_code == 409
    assert "ok:9" in response.text
