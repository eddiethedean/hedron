"""Regression tests for the fifth top-20 0.13 trustworthiness pass."""

from __future__ import annotations

import asyncio

import pytest

from hedron.concurrency import configure_concurrency, reset_concurrency_for_tests
from hedron_core.adapter import capability_matrix
from hedron_core.audit import (
    SecurityAuditEvent,
    SecurityAuditEventType,
    emit_security_audit,
    reset_security_audit_for_tests,
    set_security_audit_sink,
)
from hedron_core.component import Component
from hedron_core.diagnostics import HedronError
from hedron_core.interaction import (
    FragmentRegion,
    FragmentRegionError,
    InteractionPolicy,
    authorize_htmx_target,
)
from hedron_core.job_status_store import RedisStatusStore
from hedron_core.jobs import InMemoryJobBackend, JobState, set_job_backend
from hedron_core.models import Props
from hedron_core.prepare import PrepareContext, prepare_tree
from hedron_core.testing import ControllableClock
from hedron_jinja.async_io import (
    AsyncIoBudget,
    AsyncIoRegistry,
    async_io_session,
    run_declared_async_io,
)


class _EmptyProps(Props):
    pass


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

    def keys(self, pattern: str) -> list[str]:
        prefix = pattern.rstrip("*")
        return [k for k in self._data if k.startswith(prefix)]


def test_authorize_htmx_empty_regions_fail_closed() -> None:
    with pytest.raises(FragmentRegionError):
        authorize_htmx_target(
            InteractionPolicy(declared_regions=()),
            "#main",
            is_htmx=True,
        )


def test_authorize_htmx_allow_undeclared_opt_out() -> None:
    allowed = authorize_htmx_target(
        InteractionPolicy(declared_regions=(), allow_undeclared_targets=True),
        "#main",
        is_htmx=True,
    )
    assert allowed is None
    with pytest.raises(FragmentRegionError):
        authorize_htmx_target(
            InteractionPolicy(declared_regions=(), allow_undeclared_targets=False),
            "#main",
            is_htmx=True,
        )


def test_audit_redacts_before_custom_sink() -> None:
    seen: list[SecurityAuditEvent] = []

    class _Sink:
        def emit(self, event: SecurityAuditEvent) -> None:
            seen.append(event)

    reset_security_audit_for_tests()
    set_security_audit_sink(_Sink())
    try:
        emit_security_audit(
            SecurityAuditEventType.CSRF_REJECTED,
            "bad",
            attributes={"password": "secret", "path": "/x"},
        )
        assert seen
        assert seen[0].attributes["password"] == "[redacted]"
        assert seen[0].attributes["path"] == "/x"
    finally:
        reset_security_audit_for_tests()


def test_inmemory_mark_refuses_terminal_resurrect() -> None:
    backend = InMemoryJobBackend()
    handle = backend.submit("t", {})
    backend.mark(handle.job_id, JobState.CANCELLED)
    status = backend.mark(handle.job_id, JobState.RUNNING)
    assert status is not None
    assert status.state is JobState.CANCELLED


def test_inmemory_cancel_sticky_forces_cancelled_on_success() -> None:
    backend = InMemoryJobBackend()
    handle = backend.submit("t", {})
    assert backend.request_cancel(handle.job_id) is True
    backend.mark(handle.job_id, JobState.RUNNING)
    status = backend.mark(handle.job_id, JobState.SUCCEEDED)
    assert status is not None
    assert status.state is JobState.CANCELLED


def test_redis_status_store_cleanup_deletes_idem_keys() -> None:
    redis = _FakeRedis()
    store = RedisStatusStore(redis)  # type: ignore[arg-type]
    handle = store.submit("t", {}, idempotency_key="idem-1", auth_subject="u1")
    store.mark(handle.job_id, JobState.SUCCEEDED)
    # Force expiry by rewriting updated_at into the past.
    raw = redis.get(f"h1:job:{handle.job_id}")
    assert raw is not None
    import json

    data = json.loads(raw)
    data["updated_at"] = 1.0
    redis.set(f"h1:job:{handle.job_id}", json.dumps(data))
    removed = store.cleanup_expired(older_than_seconds=10)
    assert removed == 1
    assert redis.get(f"h1:job:{handle.job_id}") is None
    assert not any(":idem:" in k for k in redis._data)


def test_redis_status_cancel_sticky_on_succeeded_mark() -> None:
    store = RedisStatusStore(_FakeRedis())  # type: ignore[arg-type]
    handle = store.submit("t", {})
    assert store.request_cancel(handle.job_id) is True
    store.mark(handle.job_id, JobState.RUNNING)
    status = store.mark(handle.job_id, JobState.SUCCEEDED)
    assert status is not None
    assert status.state is JobState.CANCELLED


def test_live_sse_not_supported_on_flask_django() -> None:
    matrix = {row.adapter: row for row in capability_matrix()}
    for name in ("flask", "django"):
        live = next(c for c in matrix[name].capabilities if c.name == "live_sse")
        assert live.supported is False
        assert (
            "experimental" in (live.notes or "").lower() or "polling" in (live.notes or "").lower()
        )


@pytest.mark.anyio
async def test_prepare_deadline_raises_prepare_0002() -> None:
    class Slow(Component[_EmptyProps]):
        props_type = _EmptyProps

        async def prepare(self, ctx: PrepareContext) -> None:
            await asyncio.sleep(1.0)

        def render(self) -> str:
            return "x"

    clock = ControllableClock(now=0.0)
    ctx = PrepareContext(deadline=0.01, clock=clock.monotonic)
    with pytest.raises(HedronError) as exc:
        await prepare_tree(Slow(), context=ctx)
    assert exc.value.diagnostic.code == "HED-PREPARE-0002"


@pytest.mark.anyio
async def test_prepare_check_honors_controllable_clock() -> None:
    clock = ControllableClock(now=0.0)
    ctx = PrepareContext(deadline=5.0, clock=clock.monotonic)
    ctx.check()
    clock.advance(6.0)
    with pytest.raises(HedronError) as exc:
        ctx.check()
    assert exc.value.diagnostic.code == "HED-PREPARE-0001"


@pytest.mark.anyio
async def test_prepare_uses_concurrency_limiter_shed() -> None:
    reset_concurrency_for_tests()
    configure_concurrency(enabled=True, max_in_flight=4, degrade_at=1)
    from hedron.concurrency import _get_limiter

    class Hold(Component[_EmptyProps]):
        props_type = _EmptyProps

        async def prepare(self, ctx: PrepareContext) -> None:
            await asyncio.Event().wait()

        def render(self) -> str:
            return "x"

    limiter = _get_limiter()
    started = asyncio.Event()

    async def _run_hold() -> None:
        async def body() -> None:
            started.set()
            await asyncio.Event().wait()

        await limiter.run(body())

    task = asyncio.create_task(_run_hold())
    await started.wait()
    with pytest.raises(HedronError) as exc:
        await prepare_tree(Hold(), run=limiter.run)
    assert exc.value.diagnostic.code == "HED-CONC-0001"
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    reset_concurrency_for_tests()


@pytest.mark.anyio
async def test_hdj_async_io_enforces_max_operations() -> None:
    async def _fn(value: str) -> str:
        return value

    registry = AsyncIoRegistry()
    decl = registry.declare(
        "echo",
        _fn,
        budget=AsyncIoBudget(max_operations=1, deadline_seconds=None),
    )
    with async_io_session(max_operations=1):
        assert await run_declared_async_io(decl, "a") == "a"
        with pytest.raises(HedronError) as exc:
            await run_declared_async_io(decl, "b")
        assert exc.value.diagnostic.code == "HED-PREPARE-0003"


def test_flask_login_id_default_is_none_not_true() -> None:
    """Poisoned getattr(..., True) would stringify to subject_id 'True'."""
    from hedron_flask.app import HedronFlask

    h = HedronFlask(__name__)
    app = h.flask
    assert app is not None
    app.secret_key = "test"
    with app.test_request_context("/"):
        signal = h.auth_signal()
        assert signal.authenticated is False
        assert signal.subject_id is None


def test_production_set_job_backend_refuses_inmemory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    from hedron_core.compile_gate import is_production_env

    assert is_production_env() is True
    with pytest.raises(RuntimeError, match="InMemoryJobBackend"):
        set_job_backend(InMemoryJobBackend())


def test_component_fragment_regions_param_on_flask_response() -> None:
    from hedron_flask.responses import component_response

    class Box(Component[_EmptyProps]):
        props_type = _EmptyProps

        def render(self) -> str:
            return "hi"

    resp = component_response(
        Box(),
        headers_map={"HX-Request": "true", "HX-Target": "#missing"},
        fragment_regions=(),
    )
    assert resp.status_code == 403


def test_component_fragment_regions_allowed() -> None:
    from hedron_flask.responses import component_response

    class Box(Component[_EmptyProps]):
        props_type = _EmptyProps

        def render(self) -> str:
            return "hi"

    resp = component_response(
        Box(),
        headers_map={"HX-Request": "true", "HX-Target": "main"},
        fragment_regions=(FragmentRegion(id="main", selector="#main"),),
    )
    assert resp.status_code == 200
