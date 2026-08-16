"""Regression tests for the fourth top-20 severity bug-fix pass."""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest
from starlette.requests import Request
from starlette.responses import Response

from hedron.builtins import AutoForm, action_attrs
from hedron.builtins.chat import ChatInput
from hedron.security.csrf import ensure_csrf_cookie, extract_csrf_from_form
from hedron.security.policy import SecurityPolicy
from hedron_charts.optional_adapters import GraphVizAdapter
from hedron_core.diagnostics import HedronError
from hedron_core.field import Field
from hedron_core.interaction import (
    FragmentRegion,
    FragmentRegionError,
    InteractionPolicy,
    InteractionResult,
    select_htmx_auth_target,
)
from hedron_core.job_status_store import RedisStatusStore
from hedron_core.jobs import InMemoryJobBackend, JobState
from hedron_core.jobs_celery import CeleryJobBackend
from hedron_core.jobs_rq import RQJobBackend
from hedron_core.models import FormModel
from hedron_core.rendering import render
from hedron_data.columns import Column
from hedron_data.sources import DataQuery
from hedron_data.spreadsheet import export_rows_xlsx
from hedron_data.table import DataTable
from hedron_jinja.source import generic_safety_escape_diagnostics, parse_hdj_source


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
        self._in_multi = False

    def watch(self, key: str) -> None:
        self._watched[key] = self._client._data.get(key)

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
            current = self._client._data.get(watched_key)
            if current != watched_value:
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


def test_redis_status_store_cancel_requires_auth() -> None:
    store = RedisStatusStore(_FakeRedis())  # type: ignore[arg-type]
    handle, _created = store.submit("demo", {}, auth_subject="alice")
    assert store.request_cancel(handle.job_id) is False
    assert store.request_cancel(handle.job_id, auth_subject="bob") is False
    assert store.request_cancel(handle.job_id, auth_subject="alice") is True
    status = store.get(handle.job_id)
    assert status is not None
    assert status.cancel_requested is True


def test_redis_status_store_mark_honors_cancel() -> None:
    store = RedisStatusStore(_FakeRedis())  # type: ignore[arg-type]
    handle, _created = store.submit("demo", {}, auth_subject="alice")
    assert store.request_cancel(handle.job_id, auth_subject="alice") is True
    marked = store.mark(handle.job_id, JobState.RUNNING)
    assert marked is not None
    assert marked.state is JobState.CANCELLED


def test_redis_status_store_idempotency_nx() -> None:
    client = _FakeRedis()
    store = RedisStatusStore(client)  # type: ignore[arg-type]
    first, first_created = store.submit("demo", {"n": 1}, idempotency_key="k", auth_subject="a")
    second, second_created = store.submit("demo", {"n": 2}, idempotency_key="k", auth_subject="a")
    assert first_created is True
    assert second_created is False
    assert first.job_id == second.job_id
    bodies = [k for k in client._data if ":idem:" not in k]
    assert len(bodies) == 1


def test_redis_status_store_mark_refreshes_idempotency_key() -> None:
    """#210: mark/CAS must refresh or recreate the idempotency pointer TTL."""
    client = _FakeRedis()
    store = RedisStatusStore(client, ttl_seconds=10)  # type: ignore[arg-type]
    handle, created = store.submit("demo", {"n": 1}, idempotency_key="k-skew", auth_subject="a")
    assert created is True
    idem_keys = [k for k in client._data if ":idem:" in k]
    assert len(idem_keys) == 1
    idem_key = idem_keys[0]

    client.delete(idem_key)
    assert client.get(idem_key) is None
    assert client.get(f"h1:job:{handle.job_id}") is not None

    marked = store.mark(handle.job_id, JobState.RUNNING)
    assert marked is not None
    assert marked.state is JobState.RUNNING
    assert client.get(idem_key) == handle.job_id

    again, again_created = store.submit(
        "demo", {"n": 2}, idempotency_key="k-skew", auth_subject="a"
    )
    assert again_created is False
    assert again.job_id == handle.job_id


def test_celery_enqueue_failure_marks_failed() -> None:
    celery = MagicMock()
    celery.send_task.side_effect = RuntimeError("broker down")
    backend = CeleryJobBackend(celery, redis_client=_FakeRedis())  # type: ignore[arg-type]
    with pytest.raises(RuntimeError, match="broker"):
        backend.submit("demo", {})
    keys = [k for k in backend._store._client._data if ":idem:" not in k]  # type: ignore[attr-defined]
    assert len(keys) == 1
    job_id = keys[0].removeprefix("h1:job:")
    status = backend.get(job_id)
    assert status is not None
    assert status.state is JobState.FAILED


def test_rq_unknown_type_and_cross_worker_cancel() -> None:
    queue = MagicMock()
    queue.connection = object()
    backend = RQJobBackend(queue, redis_client=_FakeRedis(), task_registry={})  # type: ignore[arg-type]
    with pytest.raises(KeyError, match="Unknown RQ"):
        backend.submit("missing", {})

    def _task(payload: dict[str, object]) -> None:
        del payload

    backend = RQJobBackend(
        queue,
        redis_client=_FakeRedis(),  # type: ignore[arg-type]
        task_registry={"demo": _task},
    )
    handle = backend.submit("demo", {})
    # Simulate another worker: local RQ job map empty; fetch via shared connection.
    backend._rq_jobs.clear()
    fetched = MagicMock()
    fake_job = MagicMock()
    fake_job.fetch.return_value = fetched
    with patch.dict("sys.modules", {"rq": MagicMock(), "rq.job": MagicMock(Job=fake_job)}):
        assert backend.request_cancel(handle.job_id) is True
    fetched.cancel.assert_called_once()
    status = backend.get(handle.job_id)
    assert status is not None
    assert status.cancel_requested is True


def test_select_htmx_auth_target_prefers_client_and_rejects_mismatch() -> None:
    assert select_htmx_auth_target(client_target="#main", region_id=None) == "#main"
    assert select_htmx_auth_target(client_target=None, region_id="main") == "#main"
    assert select_htmx_auth_target(client_target="#main", region_id="main") == "#main"
    with pytest.raises(FragmentRegionError):
        select_htmx_auth_target(client_target="#evil", region_id="main")


def test_flask_django_auth_cache_overwrites_public() -> None:
    from hedron.responses import _apply_auth_cache_headers as fastapi_apply
    from hedron_django.responses import _apply_auth_cache_headers as django_apply
    from hedron_flask.responses import _apply_auth_cache_headers as flask_apply

    headers = {"Cache-Control": "public, max-age=3600"}
    flask_apply(headers, authenticated=True)
    assert headers["Cache-Control"] == "private, no-store"
    headers = {"Cache-Control": "public, max-age=3600"}
    django_apply(headers, authenticated=True)
    assert headers["Cache-Control"] == "private, no-store"

    for apply_cache_headers in (fastapi_apply, flask_apply, django_apply):
        headers = {"Cache-Control": "max-age=60"}
        apply_cache_headers(headers, authenticated=False)
        assert headers["Cache-Control"] == "private, no-store"


def test_hdj_rejects_autoescape_off() -> None:
    source = (
        '---hdj\nversion = 1\nkind = "fragment"\nprofile = "standard"\n---\n'
        "{% autoescape off %}{{ x }}{% endautoescape %}\n"
    )
    parsed = parse_hdj_source("frag.hdj", source)
    diags = generic_safety_escape_diagnostics(parsed)
    assert diags


def test_projection_allowlist_membership() -> None:
    q = DataQuery(
        projection=("password",),
        allowlisted_projection_fields=frozenset({"id"}),
    )
    with pytest.raises(ValueError, match="Projection field"):
        q.validated()


def test_csv_xlsx_export_sanitizes_formulas() -> None:
    import zipfile
    from io import BytesIO

    table = DataTable(
        rows=[{"name": "=cmd|' /C calc'!A0"}],
        columns=[Column(name="name", label="Name")],
    )
    csv_text = table.to_csv()
    data_line = csv_text.splitlines()[1]
    assert data_line.startswith("'=") or data_line.startswith("\"'=")

    raw = export_rows_xlsx([{"a": "=1+2"}], ["a"])
    with zipfile.ZipFile(BytesIO(raw)) as zf:
        sheet = zf.read("xl/worksheets/sheet1.xml").decode("utf-8")
    assert "'=1+2" in sheet


def test_snowflake_rejects_refinements() -> None:
    from hedron_data.snowflake_source import SnowflakeDataSource

    src = SnowflakeDataSource(
        connection_factory=lambda: None,
        statement="SELECT 1 AS id",
        schema=(),
    )
    with pytest.raises(HedronError) as exc:
        src.fetch(DataQuery(sort=(("id", "asc"),)))
    assert exc.value.diagnostic.code == "HED-DATA-0061"


def test_graphviz_supports_and_rejects_active_svg() -> None:
    adapter = GraphVizAdapter()
    assert adapter.supports("digraph G { a -> b }") is True
    assert adapter.supports("paragraph about graph theory") is False

    from hedron_core.visualization import ChartAccessibility

    fake_gv = MagicMock()
    fake_src = MagicMock()
    fake_src.pipe.return_value = b'<svg><a href="javascript:alert(1)">x</a></svg>'
    fake_gv.Source.return_value = fake_src
    with patch.dict("sys.modules", {"graphviz": fake_gv}), pytest.raises(HedronError):
        adapter.compile(
            "digraph G { a -> b }",
            accessibility=ChartAccessibility(title="g"),
        )


def test_csrf_policy_names_and_ensure_cookie_gap() -> None:
    class Demo(FormModel):
        name: str = Field(default="")

    form = AutoForm(Demo, action="/save", csrf_token="tok", csrf_form_field="xsrf")
    html = render(form).html
    assert 'name="xsrf"' in html
    assert (
        action_attrs(
            MagicMock(hx_attrs=lambda: {"hx-post": "/a"}),
            include_csrf=True,
            csrf_token="tok",
            csrf_header_name="X-XSRF",
        )["hx-headers"]
        == '{"X-XSRF": "tok"}'
    )
    chat = ChatInput(
        action="/c", csrf_token="tok", csrf_form_field="xsrf", csrf_header_name="X-XSRF"
    )
    chat_html = render(chat).html
    assert 'name="xsrf"' in chat_html
    assert "X-XSRF" in chat_html
    assert extract_csrf_from_form({"xsrf": "abc"}, field_name="xsrf") == "abc"

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 1),
        "server": ("test", 80),
    }
    request = Request(scope)
    request.state.hedron_csrf_cookie_set = True
    response = Response()
    policy = SecurityPolicy.from_name("standard")
    token = ensure_csrf_cookie(response, policy, request=request)
    assert token
    set_cookie = response.headers.get("set-cookie", "")
    assert policy.csrf_cookie_name in set_cookie


def test_flask_auth_signal_reads_user_id_variants() -> None:
    from flask import session

    from hedron_flask.app import HedronFlask

    hedron = HedronFlask(__name__)
    app = hedron.flask
    assert app is not None
    app.secret_key = "test"
    with app.test_request_context("/"):
        session["_user_id"] = "u1"
        signal = hedron.auth_signal()
        assert signal.authenticated is True
        assert signal.subject_id == "u1"


def test_inmemory_cancel_still_requires_auth() -> None:
    backend = InMemoryJobBackend()
    handle = backend.submit("demo", {}, auth_subject="alice")
    assert backend.request_cancel(handle.job_id) is False
    assert backend.request_cancel(handle.job_id, auth_subject="alice") is True


def test_interaction_result_target_mismatch_raises() -> None:
    policy = InteractionPolicy(declared_regions=(FragmentRegion(id="main", selector="#main"),))
    result = InteractionResult(content="ok", region_id="main", policy=policy)
    with pytest.raises(FragmentRegionError):
        select_htmx_auth_target(client_target="#other", region_id=result.region_id)
