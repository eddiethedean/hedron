"""EFFECT-044: declared Refreshes/Updates subset checking and OutcomeMap."""

from __future__ import annotations

from typing import Annotated, Literal

import pytest
from pydantic import BaseModel
from tests.unit._helpers_044 import make_app, reset_044

from hedron import OutcomeMap, Page, Refreshes, Text, case, refresh
from hedron_core.codes import HED_TYPE_0006, HED_TYPE_0007
from hedron_core.diagnostics import HedronError


def setup_function() -> None:
    reset_044()


def test_declared_refresh_subset_ok() -> None:
    app = make_app()

    @app.refreshable
    def notes():
        return Text("notes")

    @app.command(fallback="/")
    def add() -> Annotated[object, Refreshes(notes)]:
        return refresh(notes)

    assert add.schema is not None
    assert add.descriptor.effect == "declared"


def test_undeclared_refresh_fails() -> None:
    app = make_app()

    @app.refreshable
    def notes():
        return Text("notes")

    @app.refreshable
    def other():
        return Text("other")

    @app.command(fallback="/")
    def add() -> Annotated[object, Refreshes(notes)]:
        return refresh(other)

    from fastapi.testclient import TestClient

    @app.page("/")
    def home():
        return Page(notes(), title="Home")

    client = TestClient(app)
    home_response = client.get("/")
    token = home_response.cookies.get("hedron_csrf") or ""
    try:
        response = client.post(add.path, headers={"HX-Request": "true", "X-CSRF-Token": token})
    except HedronError as caught:
        assert caught.diagnostics[0].code == HED_TYPE_0006
        return
    assert response.status_code >= 400


def test_outcome_map_complete_coverage() -> None:
    class Saved(BaseModel):
        kind: Literal["saved"] = "saved"
        id: str

    class Conflict(BaseModel):
        kind: Literal["conflict"] = "conflict"

    SaveOutcome = Saved | Conflict

    mapping = OutcomeMap[SaveOutcome](
        case(Saved, render=lambda item: Text(item.id), status=200),
        case(Conflict, render=lambda item: Text("no"), status=409),
    )
    mapping.validate_union(SaveOutcome)
    content, status, effects = mapping.map_result(Saved(id="1"))
    assert status == 200
    assert effects is None
    incomplete = OutcomeMap(case(Saved, render=lambda item: Text("x")))
    with pytest.raises(HedronError) as inner:
        incomplete.validate_union(SaveOutcome)
    assert inner.value.diagnostics[0].code == HED_TYPE_0007
