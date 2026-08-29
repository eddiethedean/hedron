"""MODEL-044: ViewParams/FormBody boundaries, adapter, DI isolation."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID, uuid4

import pytest
from fastapi import Depends
from pydantic import BaseModel, Field
from tests.unit._helpers_044 import make_app, reset_044

from hedron import FragmentHandle, Page, Text, ViewParams
from hedron.type_authoring.adapter import PydanticBindingAdapter
from hedron_core.codes import HED_TYPE_0001, HED_TYPE_0002, HED_VIEW_0004
from hedron_core.diagnostics import HedronError


def setup_function() -> None:
    reset_044()


class UserCardParams(BaseModel):
    user_id: UUID
    tab: str = "overview"


def test_viewparams_bind_model_and_fields() -> None:
    app = make_app()

    @app.refreshable("/users/{user_id}")
    def user_card(params: Annotated[UserCardParams, ViewParams()]):
        return Text(str(params.user_id))

    uid = uuid4()
    bound = user_card.bind(UserCardParams(user_id=uid))
    assert bound.handle.bound
    via_fields = user_card.bind(user_id=uid)
    assert via_fields.handle.dom_id == bound.handle.dom_id
    assert user_card.schema is not None
    assert user_card.parameter_model is UserCardParams
    assert isinstance(user_card.adapter, PydanticBindingAdapter)


def test_viewparams_bind_rejects_non_model_non_mapping_value() -> None:
    app = make_app()

    @app.refreshable("/users/{user_id}")
    def user_card(params: Annotated[UserCardParams, ViewParams()]):
        return Text(str(params.user_id))

    with pytest.raises(HedronError) as caught:
        user_card.bind(42)  # type: ignore[arg-type]

    assert caught.value.diagnostics[0].code == HED_VIEW_0004


def test_unmodeled_handler_has_no_schema() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    assert isinstance(status, FragmentHandle)
    assert status.schema is None
    assert status.parameter_model is None


def test_bind_rejects_dependency_names() -> None:
    app = make_app()

    def current_user() -> str:
        return "actor"

    @app.refreshable("/users/{user_id}")
    def user_card(
        params: Annotated[UserCardParams, ViewParams()],
        actor: Annotated[str, Depends(current_user)],
    ):
        return Text(actor)

    with pytest.raises(HedronError) as caught:
        user_card.bind(user_id=uuid4(), actor="evil")
    assert caught.value.diagnostics[0].code == HED_TYPE_0001


def test_duplicate_viewparams_fails_registration() -> None:
    app = make_app()

    with pytest.raises(HedronError) as caught:

        @app.refreshable
        def twice(
            a: Annotated[UserCardParams, ViewParams()],
            b: Annotated[UserCardParams, ViewParams()],
        ):
            return Text("no")

    assert caught.value.diagnostics[0].code == HED_TYPE_0002


def test_get_modeled_view_roundtrip() -> None:
    from fastapi.testclient import TestClient

    app = make_app()

    @app.refreshable("/users/{user_id}")
    def user_card(params: Annotated[UserCardParams, ViewParams()]):
        return Text(params.tab)

    @app.page("/")
    def home():
        uid = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
        return Page(user_card.bind(user_id=uid), title="Home")

    client = TestClient(app)
    uid = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    frag = client.get(
        f"/users/{uid}?tab=activity",
        headers={"HX-Request": "true", "HX-Target": user_card.dom_id},
    )
    assert frag.status_code == 200
    assert "activity" in frag.text


def test_viewparams_path_matches_python_name_when_alias_differs() -> None:
    from fastapi.testclient import TestClient

    class Params(BaseModel):
        item_id: Annotated[str, Field(alias="itemId")]

    app = make_app()

    @app.refreshable("/items/{item_id}")
    def item(params: Annotated[Params, ViewParams()]):
        return Text(params.item_id)

    bound = item.bind(item_id="abc")
    assert bound.handle.bound
    client = TestClient(app)
    frag = client.get(
        "/items/xyz",
        headers={"HX-Request": "true", "HX-Target": item.dom_id},
    )
    assert frag.status_code == 200
    assert "xyz" in frag.text


def test_viewparams_query_alias_is_the_public_name() -> None:
    from fastapi.testclient import TestClient

    class Params(BaseModel):
        item_id: str
        nick: Annotated[str, Field(alias="displayName")] = "anon"

    app = make_app()

    @app.refreshable("/items/{item_id}")
    def item(params: Annotated[Params, ViewParams()]):
        return Text(params.nick)

    bound = item.bind(item_id="1", nick="zed")
    assert "displayName=zed" in bound.handle.path
    client = TestClient(app)
    frag = client.get(
        "/items/1?displayName=zed",
        headers={"HX-Request": "true", "HX-Target": item.dom_id},
    )
    assert frag.status_code == 200
    assert "zed" in frag.text
