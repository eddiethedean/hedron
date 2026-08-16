"""SECURITY-044: DI shadowing, secrets, CSRF, schema bombs, forged effects."""

from __future__ import annotations

from typing import Annotated

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from pydantic import BaseModel
from tests.unit._helpers_044 import csrf_headers, make_app, reset_044

from hedron import FormBody, Page, Refreshes, Text, ViewParams, refresh
from hedron_core.codes import HED_TYPE_0001, HED_TYPE_0003, HED_TYPE_0004, HED_TYPE_0006
from hedron_core.diagnostics import HedronError
from hedron_core.type_schema import MAX_MODEL_FIELDS


def setup_function() -> None:
    reset_044()


def test_bind_cannot_populate_depends() -> None:
    app = make_app()

    def current_user() -> str:
        return "ok"

    class Params(BaseModel):
        item_id: str

    @app.refreshable("/i/{item_id}")
    def item(
        params: Annotated[Params, ViewParams()],
        user: Annotated[str, Depends(current_user)],
    ):
        return Text(user)

    with pytest.raises(HedronError) as caught:
        item.bind(item_id="1", user="forged")
    assert caught.value.diagnostics[0].code == HED_TYPE_0001


def test_csrf_still_required_for_modeled_command() -> None:
    app = make_app(security="standard")

    class Payload(BaseModel):
        title: str

    @app.refreshable
    def notes():
        return Text("n")

    @app.command(fallback="/")
    def add(data: Annotated[Payload, FormBody()]) -> Annotated[object, Refreshes(notes)]:
        return refresh(notes)

    @app.page("/")
    def home():
        return Page(notes(), title="Home")

    client = TestClient(app)
    denied = client.post(add.path, data={"title": "x"})
    assert denied.status_code in {403, 400, 422}
    headers = csrf_headers(client)
    allowed = client.post(add.path, data={"title": "x"}, headers=headers)
    # CSRF must be accepted; effect conversion still succeeds.
    assert allowed.status_code != 403


def test_formbody_rejects_json_content_type() -> None:
    app = make_app(security="standard")

    class Flags(BaseModel):
        urgent: bool = False

    @app.command(fallback="/")
    def flag(data: Annotated[Flags, FormBody()]):
        return Text(str(data.urgent))

    @app.page("/")
    def home():
        return Page(Text("h"), title="H")

    client = TestClient(app)
    headers = csrf_headers(client, htmx=False)
    refused = client.post(flag.path, json={"urgent": True}, headers=headers)
    assert refused.status_code == 415
    assert HED_TYPE_0003 in str(refused.json().get("detail"))
    assert "True" not in refused.text
    form_ok = client.post(flag.path, data={}, headers=headers)
    assert form_ok.status_code == 200
    assert "False" in form_ok.text


def test_schema_bomb_field_limit() -> None:
    namespace: dict[str, object] = {"BaseModel": BaseModel}
    fields = "\n".join(f"    f{i}: str = 'x'" for i in range(MAX_MODEL_FIELDS + 1))
    exec(f"class Bomb(BaseModel):\n{fields}", namespace)
    bomb = namespace["Bomb"]
    app = make_app()
    with pytest.raises(HedronError) as caught:

        @app.refreshable
        def huge(params: Annotated[bomb, ViewParams()]):  # type: ignore[valid-type]
            return Text("no")

    assert caught.value.diagnostics[0].code == HED_TYPE_0004


def test_cross_app_effect_rejected() -> None:
    from hedron.type_authoring.effects import assert_declared_effects
    from hedron.type_authoring.normalize import CompiledTypeHandler
    from hedron_core.htmx.policy import FragmentRegion
    from hedron_core.updates import BindingPlan, PortableTarget, RefreshIntent

    foreign = PortableTarget(
        logical_id="notes",
        dom_id="h-view-notes",
        path="/x",
        app_id="other",
        region=FragmentRegion(id="h-view-notes", selector="#h-view-notes"),
    )
    compiled = CompiledTypeHandler(
        modeled=False,
        kind="command",
        param_name=None,
        model_type=None,
        source=None,
        fields=(),
        binding_plan=BindingPlan(),
        injected_names=frozenset(),
        declared_refresh_ids=("notes",),
        declared_update_ids=(),
        outcomes=None,
        adapter=None,
        schema=None,
    )
    with pytest.raises(HedronError) as caught:
        assert_declared_effects(
            compiled,
            RefreshIntent(targets=(foreign,)),
            app_id="local",
        )
    assert caught.value.diagnostics[0].code == HED_TYPE_0006
