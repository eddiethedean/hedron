"""Redis job backend shared-client protocol (in-process stub).

Not a multi-process / real-Redis worker proof — see opt-in redis markers for that.
"""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any

import pytest

from hedron_core.jobs import JobState, RedisJobBackend, _legacy_idempotency_scope_key


class WatchError(Exception):
    """Stub WatchError so RedisJobBackend CAS works without redis-py installed."""


_redis_mod = ModuleType("redis")
_exc_mod = ModuleType("redis.exceptions")
_exc_mod.WatchError = WatchError  # type: ignore[attr-defined]
_redis_mod.exceptions = _exc_mod  # type: ignore[attr-defined]
sys.modules.setdefault("redis", _redis_mod)
sys.modules.setdefault("redis.exceptions", _exc_mod)


class _SharedRedis:
    """Minimal shared Redis stub used by two backend instances."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self._sets: dict[str, set[str]] = {}
        self._ttl: dict[str, int] = {}

    def get(self, key: str) -> str | None:
        return self._store.get(key)

    def set(
        self,
        key: str,
        value: str,
        ex: int | None = None,
        nx: bool = False,
    ) -> bool:
        if nx and key in self._store:
            return False
        self._store[key] = value
        if ex is not None:
            self._ttl[key] = int(ex)
        return True

    def delete(self, key: str) -> int:
        self._ttl.pop(key, None)
        return 1 if self._store.pop(key, None) is not None else 0

    def eval(self, script: str, numkeys: int, *args: object) -> object:
        """Minimal Lua compare-and-delete for idempotency release (#236)."""
        if numkeys != 1 or len(args) != 2:
            raise NotImplementedError("stub eval supports one-key compare-and-delete only")
        key = str(args[0])
        expected = str(args[1])
        if self._store.get(key) == expected:
            self.delete(key)
            return 1
        return 0

    def keys(self, pattern: str) -> list[str]:
        prefix = pattern.rstrip("*")
        return [k for k in self._store if k.startswith(prefix)]

    def sadd(self, key: str, member: str) -> int:
        self._sets.setdefault(key, set()).add(member)
        return 1

    def smembers(self, key: str) -> set[str]:
        return set(self._sets.get(key, set()))

    def pipeline(self) -> _SharedPipeline:
        return _SharedPipeline(self)


class _SharedPipeline:
    """WATCH/MULTI/EXEC stub that raises WatchError on concurrent mutation."""

    def __init__(self, client: _SharedRedis) -> None:
        self._client = client
        self._watched: dict[str, str | None] = {}
        self._buffer: list[tuple[str, tuple[object, ...], dict[str, object]]] = []
        self._in_multi = False

    def watch(self, key: str) -> None:
        self._watched[key] = self._client._store.get(key)

    def unwatch(self) -> None:
        self._watched.clear()
        self._buffer.clear()
        self._in_multi = False

    def get(self, key: str) -> str | None:
        return self._client.get(key)

    def multi(self) -> None:
        self._in_multi = True
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
            current = self._client._store.get(watched_key)
            if current != watched_value:
                self.unwatch()
                raise WatchError("watched key changed")
        results: list[object] = []
        for op, args, kwargs in self._buffer:
            if op == "set":
                results.append(self._client.set(args[0], args[1], **kwargs))  # type: ignore[arg-type]
        self.unwatch()
        return results


def test_redis_job_backend_shares_state_via_client_protocol() -> None:
    """Stub client only — not a multi-process worker proof."""
    shared: Any = _SharedRedis()
    a = RedisJobBackend(shared)
    b = RedisJobBackend(shared)
    handle = a.submit("demo", {"n": 1}, idempotency_key="k1", tenant_id="t")
    again = b.submit("demo", {"n": 2}, idempotency_key="k1", tenant_id="t")
    assert handle.job_id == again.job_id
    assert b.get(handle.job_id) is not None
    assert b.request_cancel(handle.job_id, tenant_id="t") is True
    st = a.get(handle.job_id)
    assert st is not None and st.cancel_requested is True
    marked = b.mark(handle.job_id, JobState.CANCELLED)
    assert marked is not None
    assert a.get(handle.job_id) is not None


def test_redis_idempotency_distinguishes_missing_and_empty_scopes() -> None:
    shared: Any = _SharedRedis()
    backend = RedisJobBackend(shared)
    unscoped = backend.submit("demo", {}, idempotency_key="same")
    empty_scoped = backend.submit("demo", {}, idempotency_key="same", tenant_id="", auth_subject="")

    assert unscoped.job_id != empty_scoped.job_id
    assert backend.submit("demo", {}, idempotency_key="same").job_id == unscoped.job_id
    assert (
        backend.submit("demo", {}, idempotency_key="same", tenant_id="", auth_subject="").job_id
        == empty_scoped.job_id
    )


def test_redis_idempotency_reads_matching_legacy_scope() -> None:
    shared: Any = _SharedRedis()
    backend = RedisJobBackend(shared)
    original = backend.submit("demo", {}, tenant_id="tenant")
    legacy_scope = _legacy_idempotency_scope_key("same", tenant_id="tenant", auth_subject=None)
    shared.set(f"h1:job:idem:{legacy_scope}", original.job_id)

    repeated = backend.submit("demo", {}, idempotency_key="same", tenant_id="tenant")
    assert repeated.job_id == original.job_id


def test_redis_job_backend_cas_contends_on_watch() -> None:
    """Concurrent mutation during WATCH raises WatchError and retries safely."""
    shared: Any = _SharedRedis()
    backend = RedisJobBackend(shared)
    handle = backend.submit("demo", {"n": 1}, tenant_id="t")
    key = f"h1:job:{handle.job_id}"
    original = shared.get(key)
    assert original is not None

    pipe = shared.pipeline()
    pipe.watch(key)
    # Mutate under another client while watched.
    shared.set(key, original.replace('"queued"', '"running"'))
    pipe.multi()
    pipe.set(key, original)
    with pytest.raises(WatchError):
        pipe.execute()

    # Backend mark still succeeds via CAS retry after contention.
    marked = backend.mark(handle.job_id, JobState.SUCCEEDED)
    assert marked is not None
    assert marked.state is JobState.SUCCEEDED


def test_redis_mark_refreshes_idempotency_ttl_skew() -> None:
    """#210: body TTL refresh must also refresh/recreate the idempotency key."""
    shared: Any = _SharedRedis()
    backend = RedisJobBackend(shared, ttl_seconds=10)
    handle = backend.submit("demo", {"n": 1}, idempotency_key="k-skew", tenant_id="t")
    idem_keys = [k for k in shared._store if ":idem:" in k]
    assert len(idem_keys) == 1
    idem_key = idem_keys[0]
    assert shared._ttl[idem_key] == 10

    # Simulate write-once idem TTL decaying while mark refreshes the body.
    shared._ttl[idem_key] = 1
    marked = backend.mark(handle.job_id, JobState.RUNNING)
    assert marked is not None
    assert marked.state is JobState.RUNNING
    assert shared._ttl[idem_key] == 10
    assert shared.get(idem_key) == handle.job_id

    # Force-expire only the idempotency key while the body remains.
    shared.delete(idem_key)
    assert shared.get(idem_key) is None
    assert shared.get(f"h1:job:{handle.job_id}") is not None

    recreated = backend.mark(handle.job_id, JobState.RUNNING)
    assert recreated is not None
    assert shared.get(idem_key) == handle.job_id
    assert shared._ttl[idem_key] == 10

    again = backend.submit("demo", {"n": 2}, idempotency_key="k-skew", tenant_id="t")
    assert again.job_id == handle.job_id


def test_cleanup_expired_preserves_idempotency_owned_by_newer_job() -> None:
    """Aged terminal cleanup must not delete an idempotency pointer owned by a newer job (#198)."""
    import json

    shared: Any = _SharedRedis()
    backend = RedisJobBackend(shared)
    aged = backend.submit("demo", {}, idempotency_key="shared-scope", tenant_id="t1")
    backend.mark(aged.job_id, JobState.SUCCEEDED)
    raw = shared.get(f"h1:job:{aged.job_id}")
    assert raw is not None
    data = json.loads(raw)
    data["updated_at"] = 1.0
    shared.set(f"h1:job:{aged.job_id}", json.dumps(data))

    live = backend.submit("demo", {"fresh": True}, tenant_id="t1")
    scope = data["idempotency_scope_key"]
    idem_key = f"h1:job:idem:{scope}"
    shared.set(idem_key, live.job_id)

    assert backend.cleanup_expired(older_than_seconds=10) == 1
    assert shared.get(f"h1:job:{aged.job_id}") is None
    assert shared.get(f"h1:job:{live.job_id}") is not None
    assert shared.get(idem_key) == live.job_id


def test_cleanup_expired_drops_idempotency_when_still_owner() -> None:
    import json

    shared: Any = _SharedRedis()
    backend = RedisJobBackend(shared)
    handle = backend.submit("demo", {}, idempotency_key="gone", tenant_id="t1")
    backend.mark(handle.job_id, JobState.SUCCEEDED)
    raw = shared.get(f"h1:job:{handle.job_id}")
    assert raw is not None
    data = json.loads(raw)
    data["updated_at"] = 1.0
    shared.set(f"h1:job:{handle.job_id}", json.dumps(data))
    idem_key = f"h1:job:idem:{data['idempotency_scope_key']}"
    assert shared.get(idem_key) == handle.job_id

    assert backend.cleanup_expired(older_than_seconds=10) == 1
    assert shared.get(f"h1:job:{handle.job_id}") is None
    assert shared.get(idem_key) is None
