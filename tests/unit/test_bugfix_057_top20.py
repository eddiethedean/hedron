"""Regression tests for the 0.57 top-20 bugfix pass (no tag)."""

from __future__ import annotations

import threading
from types import SimpleNamespace
from typing import Any

import pytest
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from hedron.auth.oidc import OidcClientConfig, _validate_post_logout_redirect_uri
from hedron.builtins.live import Pagination
from hedron.connections.registry import ConnectionRegistry
from hedron.htmx import render_mode_for_request
from hedron.routing.router import _abort_replay, _complete_replay, _ReplayGuard
from hedron.security.auth_rate_limit import _client_ip_for_rate_limit
from hedron.security.csrf import ensure_csrf_cookie
from hedron.security.policy import SecurityPolicy
from hedron_charts.limits import reject_callbacks, reject_remote_urls
from hedron_core.active_markup import active_markup_reason
from hedron_core.css.compiler import compile_css
from hedron_core.diagnostics import HedronError
from hedron_core.redis_cache import RedisCacheBackend
from hedron_core.rendering import RenderMode
from hedron_data.memory import InMemoryDataSource, _row_key
from hedron_data.sources import DataQuery
from hedron_data.workspace import DataWorkspace, DataWorkspacePolicy
from hedron_maps import Map, MapPolicy, OpenStreetMap
from hedron_mcp import AuthorizationError, McpProjection, McpTool


def _request(headers: dict[str, str] | None = None, *, client: str = "127.0.0.1") -> Request:
    hdrs = [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()]
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": hdrs,
        "client": (client, 1),
        "server": ("127.0.0.1", 80),
    }
    return Request(scope)


def test_map_tiles_preserves_policy_restrictions() -> None:
    policy = MapPolicy(
        remote_requests_permitted=False,
        allowed_source_kinds=("pmtiles",),
        allow_proxy=True,
        allowed_origins=("https://good.example",),
    )
    m = Map(
        tiles="https://evil.example/{z}/{x}/{y}.png",
        tile_allowlist=["https://evil.example/"],
        policy=policy,
        title="t",
        description="d",
    )
    assert m._spec.policy.remote_requests_permitted is False
    assert m._spec.policy.allowed_source_kinds == ("pmtiles",)
    assert m._spec.policy.allow_proxy is True
    assert "https://evil.example" in m._spec.policy.allowed_origins


def test_workspace_does_not_overwrite_empty_search_fields() -> None:
    class Row(BaseModel):
        id: str
        secret: str
        name: str

    src = InMemoryDataSource(
        [{"id": "1", "secret": "classified", "name": "n"}],
        key_field="id",
        search_fields=(),
    )
    DataWorkspace(name="items", source=src, model=Row, policy=DataWorkspacePolicy())
    assert src._search_fields == ()
    with pytest.raises(HedronError, match="HED-DATA"):
        src.fetch(DataQuery(search="classified", limit=10))


def test_workspace_does_not_widen_explicit_empty_query_allowlists() -> None:
    class Row(BaseModel):
        id: str
        name: str

    src = InMemoryDataSource(
        [{"id": "1", "name": "Ada"}],
        key_field="id",
        allowlisted_sort_fields=frozenset(),
        allowlisted_filter_fields=frozenset(),
        allowlisted_projection_fields=frozenset(),
    )
    DataWorkspace(name="items", source=src, model=Row, policy=DataWorkspacePolicy())

    with pytest.raises(ValueError, match="Sort field 'name' is not allowlisted"):
        src.fetch(
            DataQuery(
                sort=(("name", "asc"),),
                allowlisted_sort_fields=frozenset({"name"}),
            )
        )
    with pytest.raises(ValueError, match="Filter field 'name' is not allowlisted"):
        src.fetch(
            DataQuery(
                filters={"name": "Ada"},
                allowlisted_filter_fields=frozenset({"name"}),
            )
        )
    with pytest.raises(ValueError, match="Projection field 'name' is not allowlisted"):
        src.fetch(
            DataQuery(
                projection=("name",),
                allowlisted_projection_fields=frozenset({"name"}),
            )
        )


def test_css_import_url_not_class_rewritten_and_expression_rejected() -> None:
    with pytest.raises(HedronError, match="Remote CSS URL|HED-CSS"):
        compile_css(
            "@import url('https://evil.com/x.css');\ndiv{color:red}",
            component_id="demo",
        )
    with pytest.raises(HedronError, match="Unsafe CSS|banned"):
        compile_css("div { color: expression(alert(1)); }", component_id="demo")


def test_active_markup_rejects_fullwidth_script() -> None:
    reason = active_markup_reason("<svg><ｓｃｒｉｐｔ>alert(1)</ｓｃｒｉｐｔ></svg>")
    assert reason == "banned active tag"


def test_chart_rejects_fullwidth_javascript_schemes() -> None:
    with pytest.raises(HedronError, match="HED-CHART-0005"):
        reject_remote_urls({"src": "ｊａｖａｓｃｒｉｐｔ:alert(1)"})
    with pytest.raises(HedronError, match="HED-CHART"):
        reject_callbacks("ｊａｖａｓｃｒｉｐｔ:alert(1)")
    with pytest.raises(HedronError, match="HED-CHART-0005"):
        reject_remote_urls({"layout": {"images": [{"source": "ｊａｖａｓｃｒｉｐｔ:alert(1)"}]}})


def test_connection_registry_waiter_gets_factory_error() -> None:
    registry = ConnectionRegistry()

    def boom() -> object:
        raise RuntimeError("factory failed")

    registry.register("db", boom)
    errors: list[BaseException] = []

    def waiter() -> None:
        try:
            registry.get("db")
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=waiter) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=2)
    assert errors
    assert all(isinstance(exc, RuntimeError) for exc in errors)
    assert all("factory failed" in str(exc) for exc in errors)


def test_connection_registry_reset_is_locked() -> None:
    registry = ConnectionRegistry()
    registry.register("db", lambda: object())
    registry.get("db")
    registry.reset("db")
    assert "db" not in registry._instances


def test_oidc_post_logout_requires_scheme_match() -> None:
    cfg = OidcClientConfig(
        issuer="https://idp.example",
        client_id="c",
        redirect_uri="https://app.example/cb",
    )
    with pytest.raises(ValueError, match="scheme"):
        _validate_post_logout_redirect_uri("http://app.example/logout", cfg)


def test_history_restore_without_hx_request_stays_page() -> None:
    req = _request({"HX-History-Restore-Request": "true"})
    policy = SimpleNamespace(history_restore="primary")
    assert render_mode_for_request(req, policy=policy) is RenderMode.PAGE


def test_flask_auth_signal_clears_scopes_when_unauthenticated() -> None:
    from flask import Flask, session

    from hedron_flask.app import HedronFlask

    app = Flask("bugfix057")
    app.secret_key = "x"
    ext = HedronFlask()
    ext.init_app(app)
    with app.test_request_context("/"):
        session["scopes"] = ("admin", "write")
        session["tenant_id"] = "t1"
        signal = ext.auth_signal()
        assert signal.authenticated is False
        assert signal.scopes == ()
        assert signal.tenant_id is None


def test_relative_osm_tile_url_does_not_forge_cdn_origin() -> None:
    from hedron_maps.compile import OSM_STANDARD_ORIGIN

    plan = Map(
        basemap=OpenStreetMap(tile_url="/assets/{z}/{x}/{y}.png", attribution="local"),
        title="t",
        description="d",
    ).compile_plan()
    assert OSM_STANDARD_ORIGIN not in plan.origins
    assert any(str(r).startswith("/assets/") for r in plan.resources)


def test_complete_replay_aborts_streaming_response() -> None:
    from hedron.replay import MemoryReplayStore, ReplayState

    store = MemoryReplayStore()
    claim = store.claim(key="k", scope="s", fingerprint="fp", retention_seconds=60)
    assert claim.state is ReplayState.FIRST
    guard = _ReplayGuard(claim=claim, store=store, key="k", fingerprint="fp", scope_key="s")

    def _gen() -> Any:
        yield b"chunk"

    response = StreamingResponse(_gen(), media_type="text/plain")
    _complete_replay(guard, response)
    again = store.claim(key="k", scope="s", fingerprint="fp", retention_seconds=60)
    assert again.state is ReplayState.FIRST


def test_redis_invalidate_drops_tag_membership() -> None:
    from tests.ops.test_external_cache import _StubRedis

    client = _StubRedis()
    backend = RedisCacheBackend(client)  # type: ignore[arg-type]
    backend.set("k1", "v1", tags=("t1",))
    backend.invalidate(keys=("k1",))
    assert backend._key("k1") not in client._store
    assert "k1" not in client._sets.get(backend._tag_key("t1"), set())
    assert backend._ktags_key("k1") not in client._sets


def test_pagination_rejects_zero_page_size() -> None:
    with pytest.raises(ValueError, match="page_size"):
        Pagination(page=1, page_size=0, total=10, base_path="/x")


def test_mcp_authz_fails_closed_without_hooks() -> None:
    projection = McpProjection(enabled=True)
    projection.register_tool(
        McpTool(name="do", schema={"type": "object"}, mutate=False, handler=lambda: {})
    )
    with pytest.raises(AuthorizationError, match="authz_hook|deny-by-default"):
        projection.check_authz(principal="alice", action="tools/call", resource="do")


def test_auth_rate_limit_uses_trusted_forwarded_for() -> None:
    req = _request({"X-Forwarded-For": "203.0.113.9"}, client="10.0.0.1")
    req.scope["app"] = SimpleNamespace(state=SimpleNamespace(hedron_trusted_peers=["10.0.0.1"]))
    assert _client_ip_for_rate_limit(req) == "203.0.113.9"
    untrusted = _request({"X-Forwarded-For": "203.0.113.9"}, client="198.51.100.1")
    assert _client_ip_for_rate_limit(untrusted) == "198.51.100.1"


def test_ensure_csrf_session_strategy_requires_request() -> None:
    from hedron_core.csrf_strategy import SessionTokenCsrf

    policy = SecurityPolicy(csrf=SessionTokenCsrf(get_expected=lambda _r: "tok"))
    with pytest.raises(ValueError, match="requires a Request"):
        ensure_csrf_cookie(Response(), policy, request=None)


def test_workspace_identity_reads_user_id() -> None:
    class Row(BaseModel):
        id: str
        name: str

    seen: dict[str, object] = {}

    def can_read(*, user: object = None, **_kwargs: object) -> bool:
        seen["user"] = user
        return True

    src = InMemoryDataSource([{"id": "1", "name": "n"}], key_field="id")
    ws = DataWorkspace(
        name="items",
        source=src,
        model=Row,
        policy=DataWorkspacePolicy(can_read=can_read),
    )
    from hedron.routing import router as router_mod

    token = router_mod.current_request.set(
        SimpleNamespace(
            scope={"session": True},
            session={"user_id": "ada"},
            user=None,
        )
    )
    try:
        assert ws._allowed(ws.policy.can_read) is True
        assert seen["user"] == "ada"
    finally:
        router_mod.current_request.reset(token)


def test_row_key_raises_hedron_error() -> None:
    with pytest.raises(HedronError, match="HED-DATA-0010"):
        _row_key({"name": "x"}, "id")


def test_abort_replay_helper_covers_cancel_path() -> None:
    from hedron.replay import MemoryReplayStore, ReplayState

    store = MemoryReplayStore()
    claim = store.claim(key="k2", scope="s", fingerprint="fp", retention_seconds=60)
    guard = _ReplayGuard(claim=claim, store=store, key="k2", fingerprint="fp", scope_key="s")
    _abort_replay(guard)
    again = store.claim(key="k2", scope="s", fingerprint="fp", retention_seconds=60)
    assert again.state is ReplayState.FIRST
