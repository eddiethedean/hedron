"""REGRESS-042 locked issue packet: session, Redis status, workbench, cache, OIDC, explorer."""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any

import pytest
from fastapi.testclient import TestClient

from fastapi_workbench.config import WorkbenchConfig, WorkbenchMode
from fastapi_workbench.middleware import WorkbenchPathMiddleware, workbenchify
from fastapi_workbench.resolve import resolve_deployment
from fastapi_workbench.runner import prepare_app
from hedron import Hedron, Text, cache_data
from hedron.oidc import store_oidc_handshake
from hedron.security.policy import SecurityPolicy
from hedron.security.session_timeout import (
    SessionTimeoutError,
    check_session_timeout,
    touch_session,
)
from hedron_core.cache import get_cache_traces, reset_cache_for_tests
from hedron_core.job_status_store import RedisStatusStore
from hedron_core.jobs import _idempotency_scope_key, _legacy_idempotency_scope_key

ISSUES = (
    99,
    100,
    108,
    136,
    137,
    138,
    139,
    140,
    141,
    145,
    146,
    147,
    148,
    151,
    152,
    156,
    160,
    174,
    175,
    177,
    187,
    205,
    206,
    208,
    217,
    218,
    238,
    242,
    243,
    245,
    246,
    249,
)

# Bound executable evidence for each locked remediation (path::node).
_U = "tests/unit"
_I = "tests/integration"
_A = "tests/adapters"
_R = f"{_U}/test_regress_042_issues.py"
ISSUE_TESTS: dict[int, str] = {
    99: (
        f"{_U}/test_cache_single_flight_async.py::test_single_flight_async_safe_across_event_loops"
    ),
    100: f"{_U}/test_phase05_platform.py::test_cache_data_caches_none_results",
    108: (
        f"{_U}/test_snowflake_source.py::test_assert_select_only_allows_semicolon_inside_literals"
    ),
    136: f"{_I}/test_workbench_runner.py::test_prepare_app_exports_into_caller_environ",
    137: f"{_A}/workbench/test_cli.py::test_check_discover_binds_before_rserver_url",
    138: (
        f"{_U}/test_phase15_identity.py::test_login_csrf_accepts_valid_cookie_when_session_diverges"
    ),
    139: f"{_U}/test_phase15_identity.py::test_auth_rate_limiter_evicts_stale_ip_keys",
    140: f"{_R}::test_140_negative_session_timeout_limits_rejected",
    141: f"{_U}/test_models_security.py::test_secret_hash_handles_unhashable_inner_value",
    145: f"{_R}::test_145_redis_status_store_reads_legacy_idempotency_key",
    146: f"{_R}::test_146_redis_status_store_cross_scope_idempotency_fails_closed",
    147: f"{_R}::test_147_explicit_workers_one_beats_env",
    148: f"{_R}::test_148_workbenchify_honors_caller_environ_for_expected_origins",
    151: f"{_R}::test_151_public_cache_rejects_positional_user_id",
    152: f"{_R}::test_152_store_oidc_handshake_merges_partial_updates",
    156: f"{_R}::test_156_explorer_simulate_requires_csrf_when_disabled",
    160: f"{_R}::test_160_doctor_empty_set_cookie_fails_closed",
    174: f"{_R}::test_174_preview_root_path_rejects_cookie_injection",
    175: f"{_R}::test_175_explorer_rate_limiter_deletes_idle_client_keys",
    177: f"{_R}::test_177_mcp_validates_tool_arguments_against_schema",
    187: f"{_R}::test_187_flask_csrf_enforced_on_connect_and_purge",
    205: f"{_R}::test_205_gradio_abbreviated_loopback_is_private",
    206: f"{_R}::test_206_rq_cancel_fails_closed_on_fetch_connection_error",
    208: f"{_R}::test_208_redis_cache_tag_index_gets_ttl",
    217: f"{_R}::test_217_mcp_cancel_is_bound_to_principal",
    218: f"{_R}::test_218_redis_cache_set_and_tag_sadd_are_atomic",
    238: f"{_R}::test_238_weak_secret_rejects_repeated_placeholders",
    242: f"{_R}::test_242_redis_cache_ttl_matches_in_memory_semantics",
    243: f"{_R}::test_243_rq_local_job_cache_pruned_on_terminal_and_cleanup",
    245: f"{_R}::test_245_normalize_mount_path_rejects_cookie_attribute_injection",
    246: f"{_R}::test_246_inference_release_drops_request_maps",
    249: f"{_R}::test_249_color_mode_cookie_sets_secure_in_production",
}


def test_every_locked_issue_has_bound_evidence() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    assert len(ISSUES) == 32
    assert tuple(ISSUE_TESTS) == ISSUES
    for issue, node in ISSUE_TESTS.items():
        path = root / node.split("::", 1)[0]
        assert path.is_file(), f"#{issue} evidence missing file {path}"
        name = node.split("::", 1)[1] if "::" in node else ""
        if name:
            assert f"def {name}(" in path.read_text(encoding="utf-8"), (
                f"#{issue} missing test {name} in {path}"
            )


class WatchError(Exception):
    """Stub WatchError so RedisStatusStore CAS works without redis-py."""


_redis_mod = ModuleType("redis")
_exc_mod = ModuleType("redis.exceptions")
_exc_mod.WatchError = WatchError  # type: ignore[attr-defined]
_redis_mod.exceptions = _exc_mod  # type: ignore[attr-defined]
sys.modules.setdefault("redis", _redis_mod)
sys.modules.setdefault("redis.exceptions", _exc_mod)


class _FakePipeline:
    def __init__(self, client: _FakeRedis) -> None:
        self._client = client
        self._watched: dict[str, str | None] = {}
        self._buffer: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

    def watch(self, key: str) -> None:
        self._watched[key] = self._client._data.get(key)

    def unwatch(self) -> None:
        self._watched.clear()
        self._buffer.clear()

    def get(self, key: str) -> str | None:
        return self._client.get(key)

    def multi(self) -> None:
        self._buffer.clear()

    def set(
        self,
        key: str,
        value: str,
        ex: int | None = None,
        nx: bool = False,
    ) -> None:
        self._buffer.append(("set", (key, value), {"ex": ex, "nx": nx}))

    def execute(self) -> list[object]:
        for watched_key, watched_value in self._watched.items():
            if self._client._data.get(watched_key) != watched_value:
                self.unwatch()
                raise WatchError("watched key changed")
        results: list[object] = []
        for op, args, kwargs in self._buffer:
            if op == "set":
                results.append(self._client.set(args[0], args[1], **kwargs))  # type: ignore[arg-type]
        self.unwatch()
        return results


class _FakeRedis:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def get(self, name: str) -> str | None:
        return self._data.get(name)

    def set(
        self,
        name: str,
        value: str,
        ex: int | None = None,
        nx: bool = False,
    ) -> bool:
        del ex
        if nx and name in self._data:
            return False
        self._data[name] = value
        return True

    def delete(self, *names: str) -> int:
        removed = 0
        for name in names:
            if name in self._data:
                del self._data[name]
                removed += 1
        return removed

    def eval(self, script: str, numkeys: int, *args: object) -> int:
        del script
        if numkeys != 1 or len(args) != 2:
            raise NotImplementedError("stub eval supports one-key compare-and-delete only")
        key = str(args[0])
        expected = str(args[1])
        if self._data.get(key) == expected:
            self._data.pop(key, None)
            return 1
        return 0

    def keys(self, pattern: str) -> list[str]:
        del pattern
        return list(self._data)

    def pipeline(self) -> _FakePipeline:
        return _FakePipeline(self)


def test_140_negative_session_timeout_limits_rejected() -> None:
    session: dict[str, float] = {}
    touch_session(session, now=1000.0)

    with pytest.raises(ValueError, match="idle_seconds"):
        check_session_timeout(session, idle_seconds=-1, absolute_seconds=None, now=1000.5)

    with pytest.raises(ValueError, match="absolute_seconds"):
        check_session_timeout(session, idle_seconds=None, absolute_seconds=-5, now=1000.5)

    # Still within limits for non-negative configuration.
    assert check_session_timeout(session, idle_seconds=10, absolute_seconds=None, now=1000.5)
    with pytest.raises(SessionTimeoutError) as idle_exc:
        check_session_timeout(session, idle_seconds=0, absolute_seconds=None, now=1000.5)
    assert idle_exc.value.reason == "idle"


def test_145_redis_status_store_reads_legacy_idempotency_key() -> None:
    redis = _FakeRedis()
    store = RedisStatusStore(redis)  # type: ignore[arg-type]
    handle, created = store.submit("t", {}, tenant_id="tenant")
    assert created is True
    legacy = _legacy_idempotency_scope_key("same", tenant_id="tenant", auth_subject=None)
    redis.set(f"h1:job:idem:{legacy}", handle.job_id)

    again, created_again = store.submit("t", {}, idempotency_key="same", tenant_id="tenant")
    assert created_again is False
    assert again.job_id == handle.job_id


def test_146_redis_status_store_cross_scope_idempotency_fails_closed() -> None:
    redis = _FakeRedis()
    store = RedisStatusStore(redis)  # type: ignore[arg-type]
    other, _ = store.submit("t", {}, idempotency_key="same", tenant_id="other")
    scoped = _idempotency_scope_key("same", tenant_id="expected", auth_subject=None)
    idem_key = f"h1:job:idem:{scoped}"
    redis.set(idem_key, other.job_id)

    with pytest.raises(PermissionError, match="another scope"):
        store.submit("t", {}, idempotency_key="same", tenant_id="expected")
    assert redis.get(idem_key) == other.job_id


def test_147_explicit_workers_one_beats_env() -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(workers=1),
        environ={"FASTAPI_WORKBENCH_WORKERS": "4"},
    )
    assert resolved.workers == 1

    from_env = resolve_deployment(
        WorkbenchConfig(),
        environ={"FASTAPI_WORKBENCH_WORKERS": "4"},
    )
    assert from_env.workers == 4


def test_148_workbenchify_honors_caller_environ_for_expected_origins() -> None:
    custom = {
        "FASTAPI_WORKBENCH_MODE": "on",
        "FASTAPI_WORKBENCH_MOUNT": "/session/app",
        "FASTAPI_WORKBENCH_PUBLIC_BASE_URL": "https://workbench.example/session/app",
    }
    cfg = WorkbenchConfig(mode=WorkbenchMode.ON)
    resolved = resolve_deployment(cfg, environ=custom)
    wrapped = workbenchify(
        object(),
        config=cfg,
        mode=resolved.mode,
        expected_mount=resolved.browser_mount,
        environ=custom,
    )
    assert isinstance(wrapped, WorkbenchPathMiddleware)
    assert resolved.external_origin == "https://workbench.example"
    assert wrapped.expected_origins == frozenset({resolved.external_origin})


def test_148_prepare_app_forwards_environ_to_expected_origins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    custom = {
        "FASTAPI_WORKBENCH_MODE": "on",
        "FASTAPI_WORKBENCH_MOUNT": "/session/app",
        "FASTAPI_WORKBENCH_PUBLIC_BASE_URL": "https://workbench.example/session/app",
    }

    class _App:
        pass

    monkeypatch.setattr(
        "fastapi_workbench.runner.load_app",
        lambda *_a, **_k: _App(),
    )
    app, resolved = prepare_app(
        target="unused:app",
        config=WorkbenchConfig(mode=WorkbenchMode.ON),
        environ=custom,
        apply_environ=False,
    )
    assert isinstance(app, WorkbenchPathMiddleware)
    assert resolved.external_origin == "https://workbench.example"
    assert app.expected_origins == frozenset({resolved.external_origin})


def test_151_public_cache_rejects_positional_user_id() -> None:
    reset_cache_for_tests()

    @cache_data(scope="public", ttl=60)
    def load(user_id: str) -> str:
        return f"secret-{user_id}"

    assert load("alice") == "secret-alice"
    rejects = [e for e in get_cache_traces() if e.kind == "reject"]
    assert rejects
    assert any("user-specific" in (e.detail or "") for e in rejects)
    assert not any(e.kind == "store" for e in get_cache_traces())


def test_152_store_oidc_handshake_merges_partial_updates() -> None:
    session: dict[str, Any] = {}
    store_oidc_handshake(session, state="s1", nonce="n1")
    store_oidc_handshake(session, state="s2")
    handshake = session["hedron_oidc_handshake"]
    assert handshake["state"] == "s2"
    assert handshake["nonce"] == "n1"


def test_156_explorer_simulate_requires_csrf_when_disabled() -> None:
    app = Hedron(
        title="t",
        security=SecurityPolicy(csrf_enabled=False, security_headers=False),
        explorer="development",
        session_secret="dev-secret-for-test",
    )

    @app.page("/")
    def home() -> Text:
        return Text("home")

    @app.action("/secret-act")
    def secret_act() -> Text:
        return Text("acted")

    client = TestClient(app)
    denied = client.post(
        "/hedron-explorer/api/simulate",
        json={"route": "secret_act", "allow_mutations": False},
    )
    assert denied.status_code == 403
    assert "CSRF" in denied.json()["detail"]


def test_160_doctor_cookie_path_rejects_prefix_siblings_and_accepts_quoted() -> None:
    from fastapi_workbench.cli import _cookie_path_matches_mount

    mount = "/s/x/p/1"
    assert not _cookie_path_matches_mount("session=abc; Path=/s/x/p/10; HttpOnly", mount)
    assert _cookie_path_matches_mount('session=abc; Path="/s/x/p/1"; HttpOnly', mount)
    assert _cookie_path_matches_mount("session=abc; path=/s/x/p/1; HttpOnly", mount)
    assert not _cookie_path_matches_mount("session=abc; HttpOnly", mount)


def test_160_doctor_empty_set_cookie_fails_closed() -> None:
    """Call production doctor probe: empty Set-Cookie must fail closed (#160)."""
    import asyncio

    from hedron_posit.cli import _probe_app

    class _NoCookieApp:
        async def __call__(self, scope: object, receive: object, send: object) -> None:
            if not isinstance(scope, dict) or scope.get("type") != "http":
                return
            await send(  # type: ignore[misc]
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"text/html")],
                }
            )
            await send(  # type: ignore[misc]
                {"type": "http.response.body", "body": b"<html></html>"}
            )

    probe = asyncio.run(_probe_app(_NoCookieApp(), "/s/x/p/1"))
    assert probe["cookie_paths_mounted"] is False
    assert probe["reachable"] is True


def test_174_preview_root_path_rejects_cookie_injection() -> None:
    from hedron_notebook.preview import _normalize_root_path, _set_cookie_header

    with pytest.raises(ValueError, match="Unsafe root_path"):
        _normalize_root_path("/ok; Secure; Domain=evil.com")
    with pytest.raises(ValueError, match="Unsafe root_path"):
        _normalize_root_path("/ok\r\nSet-Cookie: x=1")

    safe = _normalize_root_path("/preview/app")
    header = _set_cookie_header("tokensecret", root_path=safe)
    assert header == (
        b"hedron_preview_token=tokensecret; Path=/preview/app; HttpOnly; SameSite=Lax"
    )
    assert b"Domain=" not in header


def test_175_explorer_rate_limiter_deletes_idle_client_keys() -> None:
    from hedron_explorer.router import _RATE, _prune_explorer_rate, reset_explorer_runtime_for_tests

    reset_explorer_runtime_for_tests()
    now = 1_000_000.0
    for i in range(100):
        _RATE[f"ip-{i}"] = [0.0]  # all expired relative to `now`
    _RATE["ip-0"] = [now - 1.0]  # still live
    _prune_explorer_rate(now)
    assert "ip-0" in _RATE
    assert len(_RATE) == 1
    _prune_explorer_rate(now + 61.0)
    assert "ip-0" not in _RATE
    assert _RATE == {}
    reset_explorer_runtime_for_tests()


def test_177_mcp_validates_tool_arguments_against_schema() -> None:
    from hedron_mcp import InvalidParamsError, McpProjection, McpTool

    def typed(x: int) -> dict[str, int]:
        return {"x": x}

    proj = McpProjection(enabled=True)
    proj.register_tool(
        McpTool(
            name="typed",
            schema={
                "type": "object",
                "properties": {"x": {"type": "integer"}},
                "required": ["x"],
                "additionalProperties": False,
            },
            mutate=False,
            handler=typed,
        )
    )
    with pytest.raises(InvalidParamsError, match="typed"):
        proj.call_tool("typed", {"x": "not-int"}, principal="a")
    with pytest.raises(InvalidParamsError, match="typed"):
        proj.call_tool("typed", {"x": 1, "extra": "boom"}, principal="a")
    assert proj.call_tool("typed", {"x": 1}, principal="a") == {"x": 1}


def test_187_flask_csrf_enforced_on_connect_and_purge() -> None:
    from hedron_core import Text
    from hedron_flask import HedronFlask, hedron_route

    h = HedronFlask(__name__)
    h.flask.secret_key = "test"
    app = h.flask

    @hedron_route(app, "/mutate", methods=["CONNECT", "PURGE", "POST"], endpoint="mutate_multi")
    def mutate_multi() -> Text:
        return Text("mutated-without-csrf")

    client = app.test_client()
    assert client.open("/mutate", method="CONNECT").status_code == 403
    assert client.open("/mutate", method="PURGE").status_code == 403
    assert client.post("/mutate", data={"x": "1"}).status_code == 403


def test_205_gradio_abbreviated_loopback_is_private() -> None:
    from hedron_gradio.errors import GradioRemoteError
    from hedron_gradio.policy import GradioRemoteConfig, _host_is_private, validate_remote_url

    assert _host_is_private("127.1") is True
    assert _host_is_private("127.0.1") is True
    assert _host_is_private("127.0.0.1") is True

    cfg = GradioRemoteConfig(
        base_url="https://example.com",
        allowed_hosts=frozenset({"127.1"}),
        allowed_schemes=frozenset({"http"}),
        allow_private_hosts=False,
    )
    with pytest.raises(GradioRemoteError, match="Private or loopback"):
        validate_remote_url("http://127.1/", cfg)


def test_206_rq_cancel_fails_closed_on_fetch_connection_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import types
    from types import ModuleType

    from hedron_core.jobs import JobState
    from hedron_core.jobs_rq import RQJobBackend

    class _WatchError(Exception):
        pass

    _redis_mod = ModuleType("redis")
    _exc_mod = ModuleType("redis.exceptions")
    _exc_mod.WatchError = _WatchError  # type: ignore[attr-defined]
    _redis_mod.exceptions = _exc_mod  # type: ignore[attr-defined]
    sys.modules.setdefault("redis", _redis_mod)
    sys.modules.setdefault("redis.exceptions", _exc_mod)

    class _FakePipeline:
        def __init__(self, client: _MemRedis) -> None:
            self._client = client
            self._watched: dict[str, str | None] = {}
            self._buffer: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

        def watch(self, key: str) -> None:
            self._watched[key] = self._client._data.get(key)

        def unwatch(self) -> None:
            self._watched.clear()
            self._buffer.clear()

        def get(self, key: str) -> str | None:
            return self._client.get(key)

        def multi(self) -> None:
            self._buffer.clear()

        def set(
            self,
            key: str,
            value: str,
            ex: int | None = None,
            nx: bool = False,
        ) -> None:
            self._buffer.append(("set", (key, value), {"ex": ex, "nx": nx}))

        def execute(self) -> list[object]:
            for watched_key, watched_value in self._watched.items():
                if self._client._data.get(watched_key) != watched_value:
                    self.unwatch()
                    raise _WatchError("watched key changed")
            results: list[object] = []
            for op, args, kwargs in self._buffer:
                if op == "set":
                    results.append(self._client.set(args[0], args[1], **kwargs))  # type: ignore[arg-type]
            self.unwatch()
            return results

    class _MemRedis:
        def __init__(self) -> None:
            self._data: dict[str, str] = {}

        def get(self, name: str) -> str | None:
            return self._data.get(name)

        def set(
            self,
            name: str,
            value: str,
            ex: int | None = None,
            nx: bool = False,
        ) -> bool:
            del ex
            if nx and name in self._data:
                return False
            self._data[name] = value
            return True

        def delete(self, *names: str) -> int:
            removed = 0
            for name in names:
                if name in self._data:
                    del self._data[name]
                    removed += 1
            return removed

        def pipeline(self) -> _FakePipeline:
            return _FakePipeline(self)

    no_such = type("NoSuchJobError", (Exception,), {})
    exceptions = types.ModuleType("rq.exceptions")
    exceptions.NoSuchJobError = no_such  # type: ignore[attr-defined]

    class _Job:
        @staticmethod
        def fetch(*_a: object, **_k: object) -> object:
            raise ConnectionError("broker blip")

    job_mod = types.ModuleType("rq.job")
    job_mod.Job = _Job  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "rq", types.ModuleType("rq"))
    monkeypatch.setitem(sys.modules, "rq.exceptions", exceptions)
    monkeypatch.setitem(sys.modules, "rq.job", job_mod)

    class _Queue:
        connection = object()

        def enqueue(self, fn: object, payload: object, *, job_id: str) -> object:
            del fn, payload, job_id
            return object()

    def _task(payload: dict[str, object]) -> None:
        del payload

    backend = RQJobBackend(
        _Queue(),
        redis_client=_MemRedis(),  # type: ignore[arg-type]
        task_registry={"demo": _task},
    )
    handle = backend.submit("demo", {"n": 1})
    backend._rq_jobs.clear()  # cross-worker: must fetch from broker
    prior_state = backend.get(handle.job_id)
    assert prior_state is not None
    assert prior_state.state is JobState.QUEUED

    assert backend.request_cancel(handle.job_id) is False
    restored = backend.get(handle.job_id)
    assert restored is not None
    assert restored.cancel_requested is False
    assert restored.state is JobState.QUEUED


def test_208_redis_cache_tag_index_gets_ttl() -> None:
    from hedron_core.redis_cache import RedisCacheBackend

    class _StubRedis:
        def __init__(self) -> None:
            self._store: dict[str, str] = {}
            self._sets: dict[str, set[str]] = {}
            self._ttls: dict[str, int] = {}

        def get(self, key: str) -> str | None:
            return self._store.get(key)

        def set(self, key: str, value: str, ex: int | None = None, px: int | None = None) -> bool:
            self._store[key] = value
            if px is not None:
                self._ttls[key] = max(1, int(px))
            elif ex is not None:
                self._ttls[key] = max(1, int(ex) * 1000)
            return True

        def delete(self, key: str) -> int:
            self._sets.pop(key, None)
            self._ttls.pop(key, None)
            return 1 if self._store.pop(key, None) is not None else 0

        def sadd(self, key: str, member: str) -> int:
            self._sets.setdefault(key, set()).add(member)
            return 1

        def smembers(self, key: str) -> set[str]:
            return set(self._sets.get(key, set()))

        def ttl(self, key: str) -> int:
            ms = self._ttls.get(key)
            if ms is None:
                return -2 if key not in self._sets and key not in self._store else -1
            return max(1, ms // 1000)

        def pttl(self, key: str) -> int:
            ms = self._ttls.get(key)
            if ms is None:
                return -2 if key not in self._sets and key not in self._store else -1
            return ms

        def expire(self, key: str, seconds: int) -> bool:
            self._ttls[key] = max(1, int(seconds) * 1000)
            return True

        def pexpire(self, key: str, milliseconds: int) -> bool:
            self._ttls[key] = max(1, int(milliseconds))
            return True

        def ping(self) -> bool:
            return True

    client = _StubRedis()
    backend = RedisCacheBackend(client)
    backend.set("k1", {"n": 1}, ttl=1.5, tags=("t",))
    tag_key = "h1:tag:t"
    assert "k1" in client._sets[tag_key]
    assert client.pttl(tag_key) >= 1500
    # Longer entry extends tag TTL rather than leaving it immortal.
    backend.set("k2", {"n": 2}, ttl=5.0, tags=("t",))
    assert client.pttl(tag_key) >= 5000


def test_217_mcp_cancel_is_bound_to_principal() -> None:
    from starlette.applications import Starlette
    from starlette.testclient import TestClient

    from hedron_mcp import McpProjection, McpTool, mount_mcp

    principals = {"who": "alice"}

    app = Starlette()
    projection = McpProjection(
        enabled=True,
        principal_resolver=lambda _r: principals["who"],
    )
    projection.register_tool(
        McpTool(
            name="ping",
            schema={"type": "object"},
            mutate=False,
            handler=lambda: "pong",
        )
    )
    mount_mcp(app, projection)
    client = TestClient(app)

    principals["who"] = "bob"
    cancelled = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "method": "notifications/cancelled",
            "params": {"requestId": 99},
        },
    )
    assert cancelled.status_code == 200
    assert projection.bounds.is_cancelled("99", owner="principal:bob")
    assert not projection.bounds.is_cancelled("99", owner="principal:alice")

    principals["who"] = "alice"
    allowed = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 99,
            "method": "tools/call",
            "params": {"name": "ping", "arguments": {}},
        },
    )
    assert allowed.status_code == 200


def test_218_redis_cache_set_and_tag_sadd_are_atomic() -> None:
    from hedron_core.redis_cache import RedisCacheBackend

    class _Pipe:
        def __init__(self, client: _Client) -> None:
            self._client = client
            self._ops: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

        def set(self, *a: object, **k: object) -> _Pipe:
            self._ops.append(("set", a, k))
            return self

        def sadd(self, *a: object, **k: object) -> _Pipe:
            self._ops.append(("sadd", a, k))
            return self

        def pexpire(self, *a: object, **k: object) -> _Pipe:
            self._ops.append(("pexpire", a, k))
            return self

        def execute(self) -> list[object]:
            # Commit only on EXEC — simulates MULTI crash-safety (#218).
            out: list[object] = []
            for name, args, kwargs in self._ops:
                out.append(getattr(self._client, f"_apply_{name}")(*args, **kwargs))
            self._ops.clear()
            return out

    class _Client:
        def __init__(self) -> None:
            self.store: dict[str, str] = {}
            self.sets: dict[str, set[str]] = {}
            self.ttls: dict[str, int] = {}

        def pipeline(self, transaction: bool = True) -> _Pipe:
            del transaction
            return _Pipe(self)

        def get(self, key: str) -> str | None:
            return self.store.get(key)

        def delete(self, key: str) -> int:
            self.sets.pop(key, None)
            self.ttls.pop(key, None)
            return 1 if self.store.pop(key, None) is not None else 0

        def smembers(self, key: str) -> set[str]:
            return set(self.sets.get(key, set()))

        def pttl(self, key: str) -> int:
            return self.ttls.get(key, -2)

        def _apply_set(
            self, key: str, value: str, ex: int | None = None, px: int | None = None
        ) -> bool:
            del ex
            self.store[key] = value
            if px is not None:
                self.ttls[key] = int(px)
            return True

        def _apply_sadd(self, key: str, member: str) -> int:
            self.sets.setdefault(key, set()).add(member)
            return 1

        def _apply_pexpire(self, key: str, milliseconds: int) -> bool:
            self.ttls[key] = int(milliseconds)
            return True

        # Direct mutators must not be used by RedisCacheBackend.set (atomic path).
        def set(self, *a: object, **k: object) -> bool:
            raise AssertionError("set must go through pipeline")

        def sadd(self, *a: object, **k: object) -> int:
            raise AssertionError("sadd must go through pipeline")

    client = _Client()
    backend = RedisCacheBackend(client)
    backend.set("k1", {"secret": True}, ttl=30, tags=("user:1",))
    assert backend.invalidate(tags=("user:1",)) == 1
    assert backend.get("k1") is None


def test_238_weak_secret_rejects_repeated_placeholders() -> None:
    from hedron_core.production_gate import _is_weak_secret

    assert _is_weak_secret("password") is True
    assert _is_weak_secret("password" * 4) is True
    assert _is_weak_secret("secret" * 6) is True
    assert _is_weak_secret("test" * 8) is True
    assert _is_weak_secret("changeme" * 4) is True
    assert _is_weak_secret("0" * 32) is True
    assert _is_weak_secret("a" * 32) is True
    assert _is_weak_secret("a-sufficiently-long-production-secret") is False


def test_242_redis_cache_ttl_matches_in_memory_semantics() -> None:
    from hedron_core.cache import InMemoryCacheBackend
    from hedron_core.redis_cache import RedisCacheBackend

    class _Client:
        def __init__(self) -> None:
            self.store: dict[str, str] = {}
            self.px: dict[str, int] = {}

        def get(self, key: str) -> str | None:
            return self.store.get(key)

        def set(self, key: str, value: str, ex: int | None = None, px: int | None = None) -> bool:
            del ex
            self.store[key] = value
            if px is not None:
                self.px[key] = int(px)
            return True

        def delete(self, key: str) -> int:
            self.px.pop(key, None)
            return 1 if self.store.pop(key, None) is not None else 0

        def sadd(self, key: str, member: str) -> int:
            del key, member
            return 1

        def pipeline(self, transaction: bool = True) -> _Client:
            del transaction
            return self

        def execute(self) -> list[bool]:
            return [True]

        def pttl(self, key: str) -> int:
            return self.px.get(key, -2)

        def pexpire(self, key: str, milliseconds: int) -> bool:
            self.px[key] = int(milliseconds)
            return True

    mem = InMemoryCacheBackend()
    redis = RedisCacheBackend(_Client())
    mem.set("k", "v", ttl=0)
    redis.set("k", "v", ttl=0)
    assert mem.get("k") is None
    assert redis.get("k") is None

    client = _Client()
    redis = RedisCacheBackend(client)
    redis.set("frac", "v", ttl=1.9)
    assert client.px["h1:frac"] == 1900


def test_243_rq_local_job_cache_pruned_on_terminal_and_cleanup() -> None:
    from unittest.mock import MagicMock

    from hedron_core.jobs import JobState
    from hedron_core.jobs_rq import RQJobBackend

    class _Pipe:
        def __init__(self, client: _Redis) -> None:
            self._client = client
            self._watched: dict[str, str | None] = {}
            self._buffer: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

        def watch(self, key: str) -> None:
            self._watched[key] = self._client._data.get(key)

        def unwatch(self) -> None:
            self._watched.clear()
            self._buffer.clear()

        def get(self, key: str) -> str | None:
            return self._client.get(key)

        def multi(self) -> None:
            self._buffer.clear()

        def set(
            self,
            key: str,
            value: str,
            ex: int | None = None,
            nx: bool = False,
        ) -> None:
            self._buffer.append(("set", (key, value), {"ex": ex, "nx": nx}))

        def execute(self) -> list[object]:
            for watched_key, watched_value in self._watched.items():
                if self._client._data.get(watched_key) != watched_value:
                    self.unwatch()
                    raise WatchError("watched key changed")
            results: list[object] = []
            for _op, args, kwargs in self._buffer:
                results.append(self._client.set(args[0], args[1], **kwargs))  # type: ignore[arg-type]
            self.unwatch()
            return results

    class _Redis:
        def __init__(self) -> None:
            self._data: dict[str, str] = {}

        def get(self, name: str) -> str | None:
            return self._data.get(name)

        def set(
            self,
            name: str,
            value: str,
            ex: int | None = None,
            nx: bool = False,
        ) -> bool:
            del ex
            if nx and name in self._data:
                return False
            self._data[name] = value
            return True

        def delete(self, *names: str) -> int:
            removed = 0
            for name in names:
                if name in self._data:
                    del self._data[name]
                    removed += 1
            return removed

        def keys(self, pattern: str) -> list[str]:
            prefix = pattern.rstrip("*")
            return [k for k in self._data if k.startswith(prefix)]

        def pipeline(self) -> _Pipe:
            return _Pipe(self)

    def _task(payload: dict[str, object]) -> None:
        del payload

    queue = MagicMock()
    queue.enqueue.side_effect = lambda *_a, **_k: MagicMock()
    backend = RQJobBackend(
        queue,
        redis_client=_Redis(),  # type: ignore[arg-type]
        task_registry={"demo": _task},
    )
    handles = [backend.submit("demo", {"n": i}) for i in range(5)]
    assert len(backend._rq_jobs) == 5
    for handle in handles:
        backend.mark(handle.job_id, JobState.SUCCEEDED, result={"ok": True})
    assert backend._rq_jobs == {}

    more = [backend.submit("demo", {"n": i}) for i in range(3)]
    assert len(backend._rq_jobs) == 3
    for handle in more:
        backend.mark(handle.job_id, JobState.SUCCEEDED, result={"ok": True})
    # Even if mark did not pop, cleanup must drop finished entries.
    backend._rq_jobs[more[0].job_id] = MagicMock()
    assert backend.cleanup_expired(older_than_seconds=0) >= 0
    assert more[0].job_id not in backend._rq_jobs


def test_245_normalize_mount_path_rejects_cookie_attribute_injection() -> None:
    from starlette.responses import Response

    from fastapi_workbench.mount import normalize_mount_path as wb_normalize
    from hedron_core.mount import cookie_path_for_mount, normalize_mount_path

    for raw in (
        "/app;Max-Age=0",
        "/app;Secure",
        "/app;Domain=evil.com",
        "/app,evil",
        '/app"evil',
        "/app=evil",
    ):
        assert normalize_mount_path(raw) == ""
        assert wb_normalize(raw) == ""

    path = cookie_path_for_mount("/app;Max-Age=0")
    assert path == "/"
    response = Response()
    response.set_cookie("session", "secret", path=path, httponly=True, samesite="lax")
    header = response.headers["set-cookie"]
    assert "Max-Age=0" not in header or "Path=/" in header
    assert ";Max-Age=0;" not in header.replace(" ", "")


def test_246_inference_release_drops_request_maps() -> None:
    from hedron_core.inference import ConcurrencyGroup, InferencePolicy
    from hedron_core.jobs import InMemoryJobBackend, set_job_backend

    set_job_backend(InMemoryJobBackend())
    policy = InferencePolicy(groups={"g": ConcurrencyGroup(name="g", limit=8)})
    for _ in range(20):
        status = policy.admit(job_type="t", payload={}, group="g")
        policy.release("g", request_id=status.request_id)
    assert policy._diagnostics == {}
    assert policy._request_jobs == {}
    assert policy._request_auth == {}
    assert policy._request_groups == {}
    assert policy._inflight["g"] == 0


def test_249_color_mode_cookie_sets_secure_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from starlette.responses import Response

    from hedron.color_mode import apply_color_mode_cookie
    from hedron_core.color_mode import ColorMode

    monkeypatch.setenv("HEDRON_ENV", "production")
    resp = Response()
    apply_color_mode_cookie(resp, ColorMode.DARK)
    header = resp.headers["set-cookie"].lower()
    assert "hedron_color_mode=dark" in header
    assert "secure" in header
    assert "httponly" not in header
