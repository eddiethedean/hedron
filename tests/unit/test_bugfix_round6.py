"""Round-6 hardening: HTMX region auth, 204 auth, adapter/header parity seeds."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from hedron import Hedron, InteractionResult, Text
from hedron.interaction import FragmentRegion, InteractionPolicy, OobUpdate
from hedron.routing.router import _normalize_fragment_regions
from hedron_core.interaction import (
    FragmentRegionError,
    authorize_htmx_target,
    resolve_fragment_region,
    select_htmx_auth_target,
)


def test_resolve_requires_selector_not_divergent_id() -> None:
    policy = InteractionPolicy(
        declared_regions=(FragmentRegion(id="main", selector="#panel"),),
    )
    assert resolve_fragment_region(policy, "#panel") is not None
    # HTMX bare-id form for the selector id is accepted.
    assert resolve_fragment_region(policy, "panel") is not None
    # Bookkeeping id must not authorize when selector differs.
    with pytest.raises(FragmentRegionError):
        resolve_fragment_region(policy, "#main")
    with pytest.raises(FragmentRegionError):
        resolve_fragment_region(policy, "main")
    with pytest.raises(FragmentRegionError):
        authorize_htmx_target(policy, "#main", is_htmx=True)


def test_resolve_rejects_double_hash_allows_htmx_bare_id() -> None:
    policy = InteractionPolicy(
        declared_regions=(FragmentRegion(id="panel", selector="#panel"),),
    )
    assert resolve_fragment_region(policy, "#panel") is not None
    assert resolve_fragment_region(policy, "panel") is not None
    for bad in ("##panel", "###panel"):
        with pytest.raises(FragmentRegionError):
            resolve_fragment_region(policy, bad)


def test_select_htmx_auth_target_normalizes_server_region_id() -> None:
    assert select_htmx_auth_target(client_target="#main", region_id=None) == "#main"
    assert select_htmx_auth_target(client_target=None, region_id="main") == "#main"
    assert select_htmx_auth_target(client_target="#main", region_id="main") == "#main"
    with pytest.raises(FragmentRegionError):
        select_htmx_auth_target(client_target="#evil", region_id="main")
    with pytest.raises(FragmentRegionError):
        select_htmx_auth_target(client_target="##main", region_id="main")


def test_fastapi_string_regions_strip_single_hash() -> None:
    regions = _normalize_fragment_regions(("#panel", "status"))
    assert regions[0] == FragmentRegion(id="panel", selector="#panel")
    assert regions[1] == FragmentRegion(id="status", selector="#status")


def test_fastapi_string_region_accepts_hash_selector_only() -> None:
    app = Hedron(title="t", security="standard", session_secret="test-secret", explorer="off")

    @app.page("/", fragment_regions=("#panel",))
    def home() -> InteractionResult:
        return InteractionResult(content=Text("ok"))

    client = TestClient(app)
    assert client.get("/", headers={"HX-Request": "true", "HX-Target": "#panel"}).status_code == 200
    assert (
        client.get("/", headers={"HX-Request": "true", "HX-Target": "##panel"}).status_code == 403
    )
    assert client.get("/", headers={"HX-Request": "true", "HX-Target": "panel"}).status_code == 200
    assert client.get("/", headers={"HX-Request": "true", "HX-Target": "#main"}).status_code == 403


def test_divergent_id_selector_rejects_id_target() -> None:
    app = Hedron(title="t", security="standard", session_secret="test-secret", explorer="off")

    @app.component(
        "/frag",
        fragment_regions=(FragmentRegion(id="main", selector="#panel"),),
    )
    def frag() -> InteractionResult:
        return InteractionResult(content=Text("frag"))

    client = TestClient(app)
    assert (
        client.get("/frag", headers={"HX-Request": "true", "HX-Target": "#panel"}).status_code
        == 200
    )
    assert (
        client.get("/frag", headers={"HX-Request": "true", "HX-Target": "#main"}).status_code == 403
    )


def test_flask_evil_interaction_headers_are_403() -> None:
    from hedron_flask import HedronFlask, interaction_response

    hedron = HedronFlask(__name__)
    with hedron.flask.test_request_context("/"):
        response = interaction_response(
            InteractionResult(
                content=Text("primary"),
                headers={"HX-Redirect": "https://evil.example"},
            )
        )
    assert response.status_code == 403


def test_flask_component_extra_headers_reject_open_redirect() -> None:
    from hedron_core.component import Component
    from hedron_core.models import Model
    from hedron_flask import HedronFlask
    from hedron_flask.responses import component_response

    class _EmptyProps(Model):
        pass

    class Box(Component[_EmptyProps]):
        props_type = _EmptyProps

        def render(self) -> str:
            return "hi"

    hedron = HedronFlask(__name__)
    with hedron.flask.test_request_context("/"):
        response = component_response(
            Box(),
            extra_headers={"HX-Redirect": "https://evil.example"},
        )
    assert response.status_code == 403


def test_204_rejects_evil_target_and_oob() -> None:
    app = Hedron(title="t", security="standard", session_secret="test-secret", explorer="off")
    regions = (FragmentRegion(id="main", selector="#main"),)

    @app.component("/gone", fragment_regions=regions)
    def gone() -> InteractionResult:
        return InteractionResult(content=None, status_code=204, redirect="/done")

    @app.component("/gone-oob", fragment_regions=regions)
    def gone_oob() -> InteractionResult:
        return InteractionResult(
            content=None,
            status_code=204,
            oob=(OobUpdate(content=Text("toast"), element_id="hedron-toast"),),
        )

    client = TestClient(app)
    evil = client.get(
        "/gone",
        headers={"HX-Request": "true", "HX-Target": "#evil"},
    )
    assert evil.status_code == 403
    good = client.get(
        "/gone",
        headers={"HX-Request": "true", "HX-Target": "#main"},
    )
    assert good.status_code == 204
    assert good.headers.get("HX-Redirect") == "/done"
    oob = client.get(
        "/gone-oob",
        headers={"HX-Request": "true", "HX-Target": "#main"},
    )
    assert oob.status_code == 403
