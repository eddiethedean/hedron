# Model demos and inference workflows

Build reviewable model demos, schedule inference over durable jobs, collect governed
feedback, and compose permissioned workflows (introduced in **0.18**; living train **0.59.x**).

Capability readiness is **Supported** (fail-closed); API compatibility remains **`beta`**.
Pin `hedron>=0.58.0,<0.60`.

API contract: [Inference](../api/INFERENCE.md)

!!! example "Runnable interactive sample"

    [`examples/model-demo-0.18`](https://github.com/eddiethedean/hedron/tree/main/examples/model-demo-0.18)
    is a complete local classifier workflow: submit text through a CSRF-protected form,
    run an explicitly registered action, render its scores, and inspect policy/workflow
    metadata. Its classifier is deterministic and synthetic so the example needs no API
    key or model download.

```bash
uv run uvicorn app:app --app-dir examples/model-demo-0.18 --reload
```

## Minimal demo

```python
from hedron import Hedron, Text
from hedron_core import ActionRegistry, ModelDemo, RegisteredAction

app = Hedron(title="Demo", explorer="off", security="standard", session_secret="dev")
registry = ActionRegistry()
registry.register_action(
    RegisteredAction(
        action_id="classify",
        input_schema={"text": "string"},
        output_schema={"label": "string"},
        resource_policy="cpu",
        handler=lambda text: {"label": f"pred:{text}"},
    )
)
iface = ModelDemo(registry=registry).build_from_action("classify")

@app.page("/")
def home() -> Text:
    return Text(f"Demo {iface.interface_id} from {iface.source_id}")
```

Bare callables are rejected — register an action or `RegisteredCallableAdapter` first.

## Inference admission

```python
from hedron_core import ConcurrencyGroup, InferencePolicy, InferencePriority
from hedron_core.jobs import InMemoryJobBackend, set_job_backend

set_job_backend(InMemoryJobBackend())
policy = InferencePolicy(groups={"cpu": ConcurrencyGroup(name="cpu", limit=2, fair=True)})
status = policy.admit(
    job_type="classify",
    payload={"text": "meow"},
    group="cpu",
    priority=InferencePriority.NORMAL,
    auth_subject="alice",
    tenant_id="app",
)
# When finished:
policy.release("cpu")
# Cancel maps to JobBackend when the request was accepted:
policy.request_cancel(status.request_id, auth_subject="alice", tenant_id="app")
```

Prefer durable backends in production. `InProcessInferenceQueue` is development-only.

## Governed feedback

```python
from hedron_core import FeedbackPolicy, InMemoryFeedbackSink, PredictionFeedback

feedback = PredictionFeedback(
    policy=FeedbackPolicy(
        collection_notice="Ratings are optional and require consent.",
        tenant_id="app",
        allow_export=True,
    ),
    sink=InMemoryFeedbackSink(),
)
feedback.enable(consented=True)
feedback.submit(rating=5, consented=True, principal="user-1")
```

## Workflow run

```python
from hedron_core import (
    InferenceWorkflow,
    WorkflowNode,
    WorkflowNodeKind,
    WorkflowPermission,
    WorkflowPort,
)

wf = InferenceWorkflow(workflow_id="classify-flow")
wf.grant("ops", WorkflowPermission.EDIT, WorkflowPermission.RUN, WorkflowPermission.PUBLISH)
wf.add_node(
    WorkflowNode(
        node_id="model",
        kind=WorkflowNodeKind.MODEL,
        label="Classify",
        action_id="classify",
        ports=(WorkflowPort("in", "in", "text", "in"), WorkflowPort("out", "out", "label", "out")),
    ),
    principal="ops",
)
result = wf.run(principal="ops", registry=registry, inputs={"model": {"in": "meow"}})
assert result.status in {"completed", "partial", "failed", "cancelled"}
```

## Gradio (optional Beta client interop)

```bash
pip install "hedron[gradio]>=0.58.0,<0.60"
# For live remote calls also install gradio_client
```

Keep `GradioClientAdapter(enabled=False)` until you intentionally open discovery.
See [Gradio migration](gradio-migration.md).

## Honesty

- Feedback is never silently enabled and never treated as ground truth.
- Graph JSON cannot execute host code or auto-publish HTTP/MCP endpoints.
- Gradio interop is Supported for declared allowlisted destinations on the Beta `0.2.x`
  satellite. Vendor extensions and automatic UI composition remain Experimental.
