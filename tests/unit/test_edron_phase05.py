"""Edron 0.5 resource, cache, job, and operations contracts."""

from __future__ import annotations

import time

from pydantic import BaseModel
from starlette.testclient import TestClient

import edron as ed
from edron.jobs import job_status_events
from hedron_core.cache import reset_cache_for_tests
from hedron_core.jobs import InMemoryJobBackend, JobState


def test_resource_is_lazy_and_closed_by_native_lifespan() -> None:
    state = {"created": 0, "closed": 0}

    class ResourceHandle:
        def close(self) -> None:
            state["closed"] += 1

    def factory() -> ResourceHandle:
        state["created"] += 1
        return ResourceHandle()

    app = ed.App(title="Resources")
    db_dependency = app.resource(
        "database",
        factory,
        kind="custom",
        config={"provider": "test"},
        secret_refs={"dsn": "DATABASE_URL"},
    )

    @app.page("/", title="Resource")
    class ResourcePage(ed.Page):
        database = db_dependency

        def render(self) -> None:
            self.text(type(self.database).__name__)

    assert state == {"created": 0, "closed": 0}
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "ResourceHandle" in response.text
        assert state == {"created": 1, "closed": 0}
    assert state == {"created": 1, "closed": 1}


def test_async_application_resource_supports_async_setup() -> None:
    state = {"created": 0, "closed": 0}

    class AsyncResource:
        async def close(self) -> None:
            state["closed"] += 1

    async def factory() -> AsyncResource:
        state["created"] += 1
        return AsyncResource()

    app = ed.App(title="Async application resource")
    dependency = app.resource("database", factory)

    @app.page("/", title="Async application resource")
    class ResourcePage(ed.Page):
        database = dependency

        def render(self) -> None:
            self.text(type(self.database).__name__)

    assert state == {"created": 0, "closed": 0}
    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        assert state == {"created": 1, "closed": 0}
    assert state == {"created": 1, "closed": 1}


def test_operations_and_explain_are_bounded_without_resolving_resources() -> None:
    app = ed.App(title="Operations")
    app.resource("warehouse", lambda: object(), config={"dsn": "secret-ref"})

    operations = app.operations()
    assert operations["schema"] == "edron.operations/1"
    assert operations["resources"] == [
        {
            "name": "warehouse",
            "kind": "custom",
            "scope": "application",
            "healthcheck": None,
            "resolved": False,
        }
    ]
    assert operations["backends"]["jobs"]["process_local"] is True
    explanation = app.explain()
    assert explanation["resources"][0]["lazy"] is True
    assert "secret-ref" not in str(explanation)


def test_request_resource_is_created_and_closed_per_request() -> None:
    state = {"created": 0, "closed": 0}

    class RequestResource:
        def close(self) -> None:
            state["closed"] += 1

    def factory() -> RequestResource:
        state["created"] += 1
        return RequestResource()

    app = ed.App(title="Request resource")
    dependency = app.resource("request-db", factory, scope="request")

    @app.page("/", title="Request resource")
    class RequestPage(ed.Page):
        resource = dependency

        def render(self) -> None:
            self.text(type(self.resource).__name__)

    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        assert client.get("/").status_code == 200
    assert state == {"created": 2, "closed": 2}


def test_async_request_resource_supports_async_setup_and_cleanup() -> None:
    state = {"created": 0, "closed": 0}

    class AsyncResource:
        async def close(self) -> None:
            state["closed"] += 1

    async def factory() -> AsyncResource:
        state["created"] += 1
        return AsyncResource()

    app = ed.App(title="Async request resource")
    dependency = app.resource("request-db", factory, scope="request")

    @app.page("/", title="Async request resource")
    class RequestPage(ed.Page):
        resource = dependency

        def render(self) -> None:
            self.text(type(self.resource).__name__)

    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "AsyncResource" in response.text
    assert state == {"created": 1, "closed": 1}


def test_cache_uses_native_ttl_mutable_isolation_and_bounded_entries() -> None:
    reset_cache_for_tests()
    calls = {"count": 0}

    @ed.cache_data(ttl=0.01, scope="public", max_entries=1)
    def load(value: str) -> list[str]:
        calls["count"] += 1
        return [value]

    first = load("a")
    first.append("mutated")
    assert load("a") == ["a"]
    assert calls["count"] == 1
    assert load("b") == ["b"]
    assert load("a") == ["a"]
    assert calls["count"] == 3
    time.sleep(0.02)
    assert load("a") == ["a"]
    assert calls["count"] == 4
    load.invalidate("a")
    assert load("a") == ["a"]
    assert calls["count"] == 5


def test_job_flow_honors_explicit_backend_poll_policy_and_sse_terminal_state() -> None:
    backend = InMemoryJobBackend()

    class Input:
        pass

    flow = ed.JobFlow(
        name="report",
        input_model=Input,
        job_type="report",
        payload=lambda value: {"value": "ok"},
        idempotency_key=lambda value: "report:ok",
        backend=backend,
        scope=lambda: ed.JobScope(auth_subject="alice", tenant_id="acme"),
        result=lambda value: ed.Page,
        poll_interval_ms=1500,
        retry_attempts=2,
    )
    bundle = flow.to_bundle()
    assert bundle.logical_id == "hedron:taskflow:report"
    assert flow.backend is backend
    assert flow.poll_interval_ms == 1500
    assert flow.retry_attempts == 2
    assert flow.result_ttl_seconds == 86400
    assert bundle.projections[0].data["retry_attempts"] == 2
    assert bundle.projections[0].data["idempotency"] is True

    handle = backend.submit("report", {"value": "ok"}, auth_subject="alice", tenant_id="acme")
    status = backend.mark(handle.job_id, JobState.SUCCEEDED, result={"ok": True})
    assert status is not None
    events = job_status_events(
        status,
        message_html="<p>done</p>",
    )
    assert events[-1].event == "hedron-close"


def test_page_job_renders_cached_submit_surface_without_reregistering_routes() -> None:
    class Request(BaseModel):
        year: int

    app = ed.App(title="Reports")
    flow = ed.JobFlow(
        name="annual-report",
        input_model=Request,
        job_type="report",
        payload=lambda value: {"year": value.year},
        backend=InMemoryJobBackend(),
        scope=lambda: ed.JobScope(auth_subject="alice", tenant_id="acme"),
        result=lambda value: None,
    )
    app.include(flow)
    assert app.include(flow) is app.include(flow)
    assert flow.submit_command is not None

    @app.page("/reports", title="Reports")
    class ReportsPage(ed.Page):
        def render(self) -> None:
            self.job(flow, submit_label="Build report", show_cancel=True)

    with TestClient(app) as client:
        first = client.get("/reports")
        second = client.get("/reports")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.text.count("Build report") == 1
    assert 'data-hedron-job-cancel="true"' in first.text


def test_page_job_cancel_option_composes_cancel_form_on_status_surface() -> None:
    class Request(BaseModel):
        year: int

    backend = InMemoryJobBackend()
    app = ed.App(title="Reports")
    flow = ed.JobFlow(
        name="annual-report-cancel",
        input_model=Request,
        job_type="report",
        payload=lambda value: {"year": value.year},
        backend=backend,
        scope=lambda: ed.JobScope(auth_subject="alice", tenant_id="acme"),
        authorize_cancel=ed.dependency(lambda: None),
        result=lambda value: None,
    )
    app.include(flow)

    @app.page("/reports-cancel", title="Reports")
    class ReportsPage(ed.Page):
        def render(self) -> None:
            self.job(flow, show_cancel=True)

    handle = backend.submit("report", {"year": 2026}, auth_subject="alice", tenant_id="acme")
    with TestClient(app) as client:
        client.get("/reports-cancel")
        response = client.get(f"/annual-report-cancel/status/{handle.job_id}")

    assert response.status_code == 200
    assert ">Cancel</button>" in response.text
