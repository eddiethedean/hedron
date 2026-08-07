# Model demos and inference workflows

Build reviewable model demos, schedule inference over durable jobs, collect governed
feedback, and compose permissioned workflows on the **0.18** train.

Capability readiness is **Supported** (fail-closed); API compatibility remains **`beta`**.
Pin `hedron>=0.18.0,<0.19`.

API contract: [Inference](../api/INFERENCE.md)

!!! warning "Evidence example is a stub"

    [`examples/model-demo-0.18`](https://github.com/eddiethedean/hedron/tree/main/examples/model-demo-0.18)
    is a **maintainer exit scenario** with a minimal HTTP surface (text dump / synthetic
    scores) — not a Gradio-like interactive classify UI. Prefer the snippets below and
    [recipes](../examples/recipes/index.md) when learning.

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
)
# When finished:
policy.release("cpu")
# Cancel maps to JobBackend when the request was accepted:
policy.request_cancel(status.request_id)
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

## Gradio (optional Alpha)

```bash
pip install "hedron[gradio]>=0.1.0,<0.2"
# For live remote calls also install gradio_client
```

Keep `GradioClientAdapter(enabled=False)` until you intentionally open discovery.
See [Gradio migration](gradio-migration.md).

## Honesty

- Feedback is never silently enabled and never treated as ground truth.
- Graph JSON cannot execute host code or auto-publish HTTP/MCP endpoints.
- Gradio interop is Experimental — pin Alpha and expect churn.
