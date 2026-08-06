# Inference, model demos, and workflows

**Status:** Shipped on the **0.18.0** train · RFCs 0045–0050 · Evidence
[release-gate-0.18.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/release-gate-0.18.toml)

Adopter guide: [Model demos](../guides/model-demos.md) · Gradio Alpha:
[Gradio migration](../guides/gradio-migration.md) · Narrative:
[What's new in 0.18](../guides/whats-new-0.18.md)

These contracts live primarily in `hedron_core` (re-exported where noted). They compose
durable [`JobBackend`](JOBS.md) jobs; they do **not** embed a second application runtime
or auto-publish arbitrary callables as HTTP/MCP endpoints.

## InferenceInterface / ModelDemo (RFC-0045)

| Type | Role |
|---|---|
| `ActionRegistry` | Explicit registry of `RegisteredAction` / `RegisteredCallableAdapter` |
| `RegisteredAction` | Typed action with schemas, policies, optional `handler` |
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

## ExampleSet and presentation (RFC-0046)

| Type | Role |
|---|---|
| `ExampleSet` / `ExampleItem` | Versioned samples with provenance and cached results |
| `PredictionLabel` | Ranked class scores (built-in component) |
| `ParameterViewer` | Schema-aware parameter display with secret redaction |
| `Dialogue` | Multi-speaker transcript presentation |
| `PredictionFeedback` | Consentful feedback with pluggable `FeedbackSink` |

`PredictionFeedback` defaults to disabled. Call `enable(consented=True)` before submit.
When `FeedbackPolicy.authorization_required` is true (default), pass `principal=` on
`submit` / `export` / `delete`. Retention purges expired records on those operations.
`abuse_controls` enforces text length and rate/store limits. Feedback is never ground truth.

## InferencePolicy (RFC-0047)

| Type | Role |
|---|---|
| `ConcurrencyGroup` | Named capacity (`limit`, optional `fair` scheduling) |
| `BatchWindow` | `max_size` + `max_wait_ms` batching |
| `InferencePolicy` | Admit / queue / cancel / drain over `JobBackend` |
| `InProcessInferenceQueue` | Development-only; requires `development_in_process=True` |

`request_cancel(request_id, backend=...)` cancels queued work, maps accepted requests to
job ids, calls `JobBackend.request_cancel`, and releases inflight capacity. Unknown ids
return `False`.

## InteractionRecorder (RFC-0048)

Import from `hedron`. Records redacted Python/HTTP snippets only for endpoints declared
via `declare_public(...)`. The `public=` argument cannot force-record a non-allowlisted
path. Nested mappings and lists of mappings are redacted recursively.

## InferenceWorkflow (RFC-0050)

| Type | Role |
|---|---|
| `InferenceWorkflow` | Versioned DAG with READ/RUN/EDIT/PUBLISH permissions |
| `WorkflowNode` / `WorkflowPort` | Stable node/port identities |
| `WorkflowRunResult` | Aggregate run status + per-node provenance |

Graph JSON cannot embed host code, host paths, or auto-create HTTP/MCP endpoints.
`connect()` rolls back cyclic edges. `from_json` applies the same node guards as
`add_node`. Execution:

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

## Gradio adapter (RFC-0049, Experimental)

Optional `hedron[gradio]` / `hedron_gradio.GradioClientAdapter` — disabled by default.
See [Gradio migration](../guides/gradio-migration.md).

## See also

- [Jobs](JOBS.md) — durable backends and polling
- [Built-ins](BUILT_INS.md) — presentation widgets
- [Stability](STABILITY.md)
