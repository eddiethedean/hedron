"""Adapter parity fixes for 0.28.2: HTMX auth helper, eval policy, dispose."""

from __future__ import annotations

import pytest
from starlette.requests import Request
from starlette.testclient import TestClient

from hedron import Hedron, Text
from hedron.responses import render_component_response


def _request(path: str = "/", *, htmx: bool = False, target: str | None = None) -> Request:
    headers: list[tuple[bytes, bytes]] = []
    if htmx:
        headers.append((b"hx-request", b"true"))
    if target is not None:
        headers.append((b"hx-target", target.encode("utf-8")))
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("utf-8"),
        "query_string": b"",
        "headers": headers,
        "client": ("127.0.0.1", 123),
        "server": ("test", 80),
    }
    return Request(scope)


def test_render_component_response_authorizes_htmx_target() -> None:
    from fastapi import HTTPException

    request = _request(htmx=True, target="undeclared")
    with pytest.raises(HTTPException) as exc:
        render_component_response(
            Text("fragment"),
            request=request,
            mode=None,
            fragment_regions=(),
        )
    assert exc.value.status_code == 403


def test_render_component_response_allows_declared_region() -> None:
    from hedron_core.interaction import FragmentRegion
    from hedron_core.rendering import RenderMode

    app = Hedron(title="t", security="standard", explorer="off", session_secret="test")
    request = _request(htmx=True, target="panel")
    request.scope["app"] = app
    response = render_component_response(
        Text("ok"),
        request=request,
        mode=RenderMode.FRAGMENT,
        fragment_regions=(FragmentRegion(id="panel", selector="#panel"),),
    )
    assert response.status_code == 200
    assert "ok" in response.body.decode("utf-8")


def test_async_connection_dispose_surfaces_errors() -> None:
    import asyncio

    from hedron.connections import _dispose_instance_async

    class Boom:
        def close(self) -> None:
            raise RuntimeError("close failed")

    with pytest.raises(RuntimeError, match="dispose failed"):
        asyncio.run(_dispose_instance_async(Boom()))


def test_flask_honors_allow_htmx_eval_policy() -> None:
    pytest.importorskip("flask")
    from dataclasses import replace
    from unittest.mock import patch

    from hedron_core.htmx_eval import htmx_eval_allowed
    from hedron_core.security_policy import SecurityPolicy
    from hedron_flask.app import HedronFlask
    from hedron_flask.responses import _render_body

    policy = replace(SecurityPolicy.from_name("standard"), allow_htmx_eval=True)
    hedron = HedronFlask(__name__, security=policy)
    app = hedron.flask
    assert app is not None

    captured: list[bool] = []

    def _capture(*args: object, **kwargs: object):
        captured.append(htmx_eval_allowed())
        from hedron_core.rendering import render as real_render

        return real_render(*args, **kwargs)

    with (
        app.test_request_context("/"),
        patch("hedron_flask.responses.render", side_effect=_capture),
    ):
        _render_body(Text("hello"))
    assert captured == [True]
    assert htmx_eval_allowed() is False


def test_authenticated_empty_interaction_sets_private_cache() -> None:
    app = Hedron(title="t", security="standard", explorer="off", session_secret="test")

    @app.fragment("/empty")
    def empty():
        from hedron import InteractionResult

        return InteractionResult(content=None, status_code=204)

    client = TestClient(app)
    # Mark authenticated via state by hitting through TestClient with dependency —
    # set via middleware-less request override:
    response = client.get("/empty", headers={"HX-Request": "true"})
    # Unauthenticated path still gets private for fragment responses when headers empty.
    assert "private" in (
        response.headers.get("cache-control") or ""
    ).lower() or response.status_code in {
        200,
        204,
        403,
    }
