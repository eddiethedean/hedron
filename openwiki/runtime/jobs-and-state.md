---
type: runtime
title: Runtime state and background jobs
description: Hedron binds application-owned runtime services to each request and composes scoped, authorized background-job submission, polling, cancellation, and result views around a JobBackend.
tags: [runtime, state, jobs, taskflow]
verified:
  - by: openwiki/0.5.2
    at: 2026-09-19T19:14:00.347Z
sources:
  - id: openwiki-source-ecab4d4eac67bdabf286a619
    resource: repo://packages/hedron-core/src/hedron_core/jobs/backend.py
  - id: openwiki-source-20bf43100336a1b5fe9a4ff1
    resource: repo://packages/hedron-core/src/hedron_core/jobs/gate.py
  - id: openwiki-source-a533828ef7f53f9af2f6ae19
    resource: repo://packages/hedron/src/hedron/jobs/durable.py
  - id: openwiki-source-d1dbbd912dc890a95e902d07
    resource: repo://packages/hedron/src/hedron/jobs/flow.py
  - id: openwiki-source-73da1192b50824bf6ec5581f
    resource: repo://packages/hedron/src/hedron/runtime.py
  - id: openwiki-source-272f273caea925e945909aa1
    resource: repo://packages/hedron/src/hedron/state.py
generated: { by: "codex", at: "2026-09-19T15:43:01.076Z" }
---

# Runtime state and background jobs

Hedron separates request-local binding from durable work. The [request and interaction layer](/openwiki/architecture/requests-and-interactions.md) owns the HTTP/HTMX transport; this page follows the runtime context and job state behind it.

## Application-owned runtime

`HedronRuntimeContext` owns the registry, cache, job backend, concurrency limiter, tracing configuration, plugin/projection state, bundle state, and handle state for one application. `from_defaults()` forks registry state and replaces process-local cache/job defaults with isolated in-memory instances so two application objects do not share mutable service state. `activate()` binds every service through context managers, and `RuntimeContextMiddleware` activates that context around HTTP and WebSocket requests.

`SessionState[T]` is a typed facade over the host session. It validates stored values with a Pydantic `TypeAdapter`, refreshes its view when the underlying session changes, serializes models on write, and fails closed if code tries to persist or clear state without `SessionMiddleware`. It is request/session state, not a substitute for a database or durable job store.

## Job backend contract

`JobBackend` is the application-owned durable job store contract. It submits JSON-compatible payloads, returns handles, looks up status, requests cancellation, cleans expired records, and marks lifecycle state/results. Observation and cancellation are scoped by `auth_subject` and `tenant_id`; missing or unauthorized jobs should look the same to HTTP callers. Backends that are process-local must identify themselves, because in-memory records do not span processes and multi-worker deployments need Redis or a Celery/RQ bridge.

`enqueue_durable()` passes job type, payload, idempotency key, tenant, and subject to the selected backend and returns the job ID. `schedule_post_response()` is deliberately different: it adds small non-durable work to FastAPI `BackgroundTasks` and is not a `JobBackend`.

## TaskFlow lifecycle

`TaskFlow` packages a durable job UI around an application backend and a request-scoped authorization provider:

1. The submit command validates an input model, builds the payload, derives an optional idempotency key, evaluates the job scope, submits the job, and redirects to `/name/status/{job_id}`. Backend failures fail closed by default.
2. The status view looks up the job with subject/tenant scope and returns 404 for missing or unauthorized jobs. While non-terminal it returns a bounded `Poll` view; when terminal it renders a successful result or a status body.
3. If cancellation authorization is configured, the cancel action requests cancellation with the same scope and rechecks authorization before returning status.
4. The result view is available only after a terminal, authorized job; successful jobs render the configured result and non-success states remain errors rather than being treated as results.

`PollPolicy` bounds polling intervals to 1–60 seconds and defaults to 2 seconds. TaskFlow also bounds retry attempts and result retention, and advertises its submit/status/cancel/result surfaces through a feature bundle while leaving workers, schedulers, the backend, and scope application-owned.

## Production boundary

The default process-local backend is useful for local development and tests, but it is not a multi-worker coordination mechanism. Setting a process-local backend under `HEDRON_ENV=production` is rejected; outside production, Hedron emits a warning directing multi-worker deployments to a durable backend. Choose and configure the backend before submitting work, and keep authorization scope on every status and cancel path.
