# Inference, model demos, and workflows

**Status:** Available on 1.0 (introduced on the **0.18.0** train) · RFCs 0045–0050 · Evidence
[release-gate-0.18.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/release-gate-0.18.toml)

Adopter guide: [Model demos](../guides/model-demos.md) · Gradio Beta client interop:
[Gradio migration](../guides/gradio-migration.md) · Narrative:
[What's new in 0.18](../guides/whats-new-0.18.md)

These contracts live primarily in `hedron_core` (re-exported from `hedron` where noted).
They compose durable [`JobBackend`](JOBS.md) jobs; they do **not** embed a second
application runtime or auto-publish arbitrary callables as HTTP/MCP endpoints.

## InferenceInterface / ModelDemo (RFC-0045)

| Type | Role |
|---|---|
| `ActionRegistry` | Explicit registry of `RegisteredAction` / `RegisteredCallableAdapter` |
| `RegisteredAction` | Action with schemas, policies, optional `handler` |
| `ModelDemo` | Builds reviewable `InferenceInterface` only from the registry |
| `InferenceInterface` | Input/result surface metadata (never implies a public route) |

Bare callables fail closed (`ModelDemo.build_from_callable` raises). Authorized demos
require an explicit `resource_policy`. Building a demo never flips `http_exposed` /
`mcp_exposed` on.

```python
from hedron_core import ActionRegistry, ModelDemo, RegisteredAction

registry = ActionRegistry()
registry.register_action(
    RegisteredAction(
        action_id="classify",
        input_schema={"text": "string"},
        output_schema={"label": "string"},
        resource_policy="gpu",
        handler=lambda text: {"label": "cat"},
    )
)
demo = ModelDemo(registry=registry)
iface = demo.build_from_action("classify")
```

### Errors

| Condition | Behavior |
|---|---|
| Bare callable / missing registry action | Raises (`InferenceError` / fail-closed build) |
| Missing `resource_policy` when required | Build rejected |
| Accidental HTTP/MCP exposure at build | Never enabled by `ModelDemo` |

## ExampleSet and presentation (RFC-0046)

| Type | Role |
|---|---|
| `ExampleSet` / `ExampleItem` | Versioned samples with provenance and cached results |
| `PredictionLabel` | Ranked class scores ([component](../components/prediction-label.md)) |
| `ParameterViewer` | Schema-aware parameter display with secret redaction ([component](../components/parameter-viewer.md)) |
| `Dialogue` | Multi-speaker transcript ([component](../components/dialogue.md)) |
| `PredictionFeedback` | Consentful feedback with pluggable `FeedbackSink` |

`PredictionFeedback` defaults to disabled. Call `enable(consented=True)` before submit.
When `FeedbackPolicy.authorization_required` is true (default), pass `principal=` on
`submit` / `export` / `delete`. Retention purges expired records on those operations.
`abuse_controls` enforces text length and rate/store limits. Feedback is never ground truth.

## InferencePolicy (RFC-0047)

Admission and scheduling layered on a durable `JobBackend`.

### Fields (`InferencePolicy`)

| Field | Type | Meaning |
|---|---|---|
| `groups` | `Mapping[str, ConcurrencyGroup]` | Named capacity pools |
| `max_queue` | `int` | Reject when queued depth reaches this (default `100`) |
| `default_eta_per_item` | `float` | ETA heuristic seconds per queued item |
| `batch` | `BatchWindow \| None` | Optional batching window |
| `development_in_process` | `bool` | Required `True` before using `InProcessInferenceQueue` |

### `ConcurrencyGroup` / `BatchWindow`

| Type | Fields |
|---|---|
| `ConcurrencyGroup` | `name: str`, `limit: int` (≥ 1), `fair: bool = True` |
| `BatchWindow` | `max_size: int`, `max_wait_ms: int = 50`, `shape_key: str = "default"` |

### Methods

| Method | Returns | Role |
|---|---|---|
| `register_group(group)` | `None` | Register / replace a concurrency group (`HED-INFER-0002` if `limit < 1`) |
| `admit(*, job_type, payload, group, priority=NORMAL, tenant_id=None, auth_subject=None, correlation_id="", shape_key="default", backend=None)` | `InferenceQueueStatus` | Accept immediately, queue, or reject on overload |
| `request_cancel(request_id, *, auth_subject=None, tenant_id=None, backend=None)` | `bool` | Drop queued work or cancel accepted `job_id` via `JobBackend` when the caller matches the request scope (`job_authorized_http`) |
| `is_cancelled(request_id)` | `bool` | Cooperative cancel flag for workers / workflows |
| `drain_ready(*, backend=None)` | `list[tuple[QueuedInference, JobHandle]]` | Promote queued work when capacity frees |
| `release(group, *, count=1)` | `None` | Free inflight slots after terminal work |
| `queue_status()` | `list[InferenceQueueStatus]` | Snapshot of queued / accepted requests |
| `diagnostics_for(request_id)` | `InferenceDiagnostics \| None` | Per-request timing / group diagnostics |
| `form_batch(items, *, now=None)` | batched groups | Shape-aware batching helper |
| `stream_progress(values, *, request_id, on_chunk=None)` | `list` | Progress helper that honors cancel |

`InferenceAdmission`: `accepted`, `queued`, `rejected` (overload).
`InferencePriority`: `low`, `normal`, `high`.

```python
from hedron_core import ConcurrencyGroup, InferencePolicy
from hedron_core.jobs import InMemoryJobBackend, set_job_backend

backend = InMemoryJobBackend()
set_job_backend(backend)
policy = InferencePolicy(max_queue=50)
policy.register_group(ConcurrencyGroup(name="gpu", limit=2, fair=True))
status = policy.admit(
    job_type="classify",
    payload={"text": "meow"},
    group="gpu",
    auth_subject="alice",
    backend=backend,
)
# status.request_id, status.job_id, status.admission
```

### Errors

| Condition | Code / behavior |
|---|---|
| Unknown / invalid concurrency group | `InferenceError` (`HED-INFER-0002`) |
| Queue full | Admission `rejected` (no raise) |
| Unknown `request_id` on cancel | Returns `False` |
| Unauthorized cancel (mismatched or omitted caller credentials) | Returns `False` (no queue/backend mutation) |
| In-process queue without `development_in_process=True` | Fail closed |

## InteractionRecorder (RFC-0048)

Import from `hedron`. Records redacted Python/HTTP snippets only for endpoints declared
via `declare_public(...)`.

| Type / API | Role |
|---|---|
| `InteractionRecorder` | Allowlisted recorder |
| `RecordedExchange` / `RecordingSnippet` | Captured exchange + snippet types |
| `declare_public(...)` | Explicit allowlist; `public=` cannot force a non-allowlisted path |

Nested mappings and lists of mappings are redacted recursively.

## InferenceWorkflow (RFC-0050)

| Type | Role |
|---|---|
| `InferenceWorkflow` | Versioned DAG with READ/RUN/EDIT/PUBLISH permissions |
| `WorkflowNode` / `WorkflowPort` | Stable node/port identities |
| `WorkflowRunResult` | Aggregate run status + per-node provenance |

Graph JSON cannot embed host code, host paths, or auto-create HTTP/MCP endpoints.
`connect()` rolls back cyclic edges. `from_json` applies the same node guards as
`add_node`.

```python
result = workflow.run(
    principal="alice",
    registry=registry,
    inputs={"in": {"out": "meow"}},
)
```

ACTION/MODEL nodes invoke registered handlers only. Cancellation honors
`InferencePolicy.is_cancelled` when `request_id` is supplied. Partial failure skips
downstream nodes.

Structured editor: `workflow.editor_view(mode="table"|"list"|"outline")`.

### Errors

| Condition | Behavior |
|---|---|
| Cyclic `connect` | Edge rolled back; error raised |
| Hostile `from_json` / host paths | Rejected by node guards |
| Unauthorized principal | Permission check fails closed |
| Downstream after partial failure | Skipped; reflected in `WorkflowRunResult` |

## Gradio adapter (RFC-0049, Experimental)

Optional `hedron[gradio]` / `hedron_gradio.GradioClientAdapter` — disabled by default.
See [Gradio migration](../guides/gradio-migration.md).

## See also

- [Jobs](JOBS.md) — durable backends and polling
- [Celery / RQ + Redis](../guides/jobs-celery-rq.md)
- [Built-ins index](BUILT_INS.md) — presentation widgets → component pages
- [Stability](STABILITY.md)
