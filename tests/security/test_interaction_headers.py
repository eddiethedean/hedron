"""InteractionResult header and fragment-region security for 0.6 closure."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from hedron import Hedron, InteractionResult, Text
from hedron.interaction import (
    FragmentRegion,
    InteractionPolicy,
    OobUpdate,
    interaction_headers,
)


def test_evil_redirect_via_headers_rejected() -> None:
    result = InteractionResult(
        content=Text("ok"),
        headers={"HX-Redirect": "https://evil.example"},
    )
    with pytest.raises(ValueError, match="local path"):
        interaction_headers(result)


def test_evil_push_location_retarget_rejected() -> None:
    with pytest.raises(ValueError, match="local path"):
        interaction_headers(
            InteractionResult(content=Text("ok"), headers={"HX-Push-Url": "https://evil.example"})
        )
    with pytest.raises(ValueError, match="local path"):
        interaction_headers(
            InteractionResult(content=Text("ok"), headers={"HX-Location": "https://evil.example"})
        )
    with pytest.raises(ValueError, match="Unsafe"):
        interaction_headers(
            InteractionResult(
                content=Text("ok"),
                headers={"HX-Retarget": "body; script"},
            )
        )


def test_unapproved_header_name_rejected() -> None:
    with pytest.raises(ValueError, match="Unapproved"):
        interaction_headers(InteractionResult(content=Text("ok"), headers={"X-Custom-Evil": "1"}))


def test_typed_redirect_validated() -> None:
    headers = interaction_headers(InteractionResult(content=Text("ok"), redirect="/local"))
    assert headers["HX-Redirect"] == "/local"
    with pytest.raises(ValueError, match="local path"):
        interaction_headers(InteractionResult(content=Text("ok"), redirect="https://evil.example"))


def test_cache_private_and_no_store() -> None:
    private = interaction_headers(InteractionResult(content=Text("ok"), cache="private"))
    assert private["Cache-Control"] == "private"
    nostore = interaction_headers(InteractionResult(content=Text("ok"), cache="no-store"))
    assert "no-store" in nostore["Cache-Control"]


def test_route_fragment_regions_reject_unauthorized_target() -> None:
    app = Hedron(title="t", security="standard", session_secret="test-secret", explorer="off")

    @app.page(
        "/panel",
        fragment_regions=(FragmentRegion(id="main", selector="#main"),),
    )
    def panel() -> InteractionResult:
        # Handler omits policy.declared_regions — route allowlist must still enforce.
        return InteractionResult(content=Text("panel"))

    client = TestClient(app)
    bad = client.get(
        "/panel",
        headers={"HX-Request": "true", "HX-Target": "#evil"},
    )
    assert bad.status_code == 403
    good = client.get(
        "/panel",
        headers={"HX-Request": "true", "HX-Target": "#main"},
    )
    assert good.status_code == 200
    assert "panel" in good.text


def test_interaction_result_endpoint_rejects_evil_headers() -> None:
    app = Hedron(title="t", security="standard", session_secret="test-secret", explorer="off")

    @app.component("/frag")
    def frag() -> InteractionResult:
        return InteractionResult(
            content=Text("primary"),
            headers={"HX-Redirect": "https://evil.example"},
        )

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/frag", headers={"HX-Request": "true"})
    assert response.status_code >= 400
    assert "evil.example" not in response.headers.get("HX-Redirect", "")


def test_oob_update_with_element_id() -> None:
    app = Hedron(title="t", security="standard", session_secret="test-secret", explorer="off")
    regions = (
        FragmentRegion(id="main", selector="#main"),
        FragmentRegion(id="oob-status", selector="#oob-status"),
    )

    @app.component("/oob", fragment_regions=regions)
    def oob() -> InteractionResult:
        return InteractionResult(
            content=Text("primary"),
            oob=(OobUpdate(content=Text("side"), element_id="oob-status"),),
        )

    client = TestClient(app)
    response = client.get("/oob", headers={"HX-Request": "true", "HX-Target": "#main"})
    assert response.status_code == 200
    assert "hx-swap-oob" in response.text
    assert "side" in response.text


def test_oob_unauthorized_element_id_rejected() -> None:
    app = Hedron(title="t", security="standard", session_secret="test-secret", explorer="off")
    regions = (FragmentRegion(id="main", selector="#main"),)

    @app.component("/oob", fragment_regions=regions)
    def oob() -> InteractionResult:
        return InteractionResult(
            content=Text("primary"),
            oob=(OobUpdate(content=Text("evil"), element_id="evil"),),
        )

    client = TestClient(app)
    response = client.get("/oob", headers={"HX-Request": "true", "HX-Target": "#main"})
    assert response.status_code == 403


def test_oob_missing_target_with_declared_regions_rejected() -> None:
    from hedron_core.interaction import authorize_oob_update

    regions = (FragmentRegion(id="main", selector="#main"),)
    with pytest.raises(ValueError, match="element_id or select"):
        authorize_oob_update(OobUpdate(content=Text("x")), regions=regions)

    app = Hedron(title="t", security="standard", session_secret="test-secret", explorer="off")

    @app.component("/oob-missing", fragment_regions=regions)
    def oob_missing() -> InteractionResult:
        return InteractionResult(
            content=Text("primary"),
            oob=(OobUpdate(content=Text("side")),),
        )

    client = TestClient(app)
    response = client.get(
        "/oob-missing",
        headers={"HX-Request": "true", "HX-Target": "#main"},
    )
    assert response.status_code == 403


def test_undeclared_fragment_regions_reject_hx_target() -> None:
    """Fail closed: without fragment_regions, HX-Target is rejected."""
    app = Hedron(title="t", security="standard", session_secret="test-secret", explorer="off")

    @app.page("/panel")
    def panel() -> InteractionResult:
        return InteractionResult(content=Text("panel"))

    client = TestClient(app)
    response = client.get(
        "/panel",
        headers={"HX-Request": "true", "HX-Target": "#evil"},
    )
    assert response.status_code == 403


def test_allow_undeclared_targets_opt_out() -> None:
    app = Hedron(title="t", security="standard", session_secret="test-secret", explorer="off")

    @app.page("/panel")
    def panel() -> InteractionResult:
        return InteractionResult(
            content=Text("panel"),
            policy=InteractionPolicy(allow_undeclared_targets=True),
        )

    client = TestClient(app)
    response = client.get(
        "/panel",
        headers={"HX-Request": "true", "HX-Target": "#evil"},
    )
    assert response.status_code == 200
    assert "panel" in response.text


def test_explorer_interaction_trace_populated() -> None:
    from starlette.requests import Request

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "path": "/",
        "raw_path": b"/",
        "root_path": "",
        "scheme": "http",
        "server": ("test", 80),
        "client": ("test", 123),
        "headers": [(b"hx-request", b"true")],
    }
    request = Request(scope)
    interaction_headers(InteractionResult(content=Text("x"), explanation="trace"), request=request)
    assert request.state.hedron_interaction["explanation"] == "trace"
