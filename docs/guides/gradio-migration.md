# Gradio migration inventory

**Evidence:** `MIGRATE-018` · **RFC:**
[RFC-0049](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0049-GRADIO-ADAPTER.md) ·
**Cross-check:**
[GRADIO_FEATURE_CROSSCHECK.md](https://github.com/eddiethedean/hedron/blob/main/docs/GRADIO_FEATURE_CROSSCHECK.md)

This inventory maps Gradio outcomes to Hedron without claiming automatic conversion. Install the
optional Alpha package only when needed:

```bash
pip install "hedron[gradio]>=0.28.1,<0.29"
# Live remote discovery/predict also needs:
pip install gradio-client
```

Absence of `hedron-gradio` adds no core dependency, route, asset, or startup cost.

**Supported Gradio client range (checked):** major **6**, minor **17–22** (through **6.22.x**).
Other majors/minors raise `GradioRemoteError`.

## Capability map

| Gradio surface | Hedron destination | Notes |
|---|---|---|
| `Interface(fn, …)` | `InferenceInterface` / `ModelDemo` | Explicit registered action or callable adapter only (RFC-0045). |
| Examples / Dataset | `ExampleSet` | Provenance, authz, cache invalidation (RFC-0046). |
| Flagging | `PredictionFeedback` | Consent mandatory; never ground truth. |
| Queue / batch / concurrency | `InferencePolicy` over `JobBackend` | In-process queue is development-only. |
| API recorder | `InteractionRecorder` | Public endpoints only; secrets redacted. |
| Remote Gradio apps | `hedron_gradio.GradioClientAdapter` | Experimental Alpha protocol client. |
| `Workflow` canvas | `InferenceWorkflow` + structured editor | No canvas required; JSON cannot run host code. |
| HF Space / OAuth / ZeroGPU | Vendor nodes in `hedron-gradio` | Not portable core contracts. |

## FastAPI coexistence

Mount or reverse-proxy a Gradio app **beside** Hedron; do not embed Gradio’s UI runtime in
`hedron-core`. Typical pattern: Hedron owns HTML/HTMX routes; `GradioClientAdapter` calls a
separate Gradio process/URL for remote predict/jobs. Auth tokens stay on the adapter
(`auth_token=`) and are never inlined into workflow JSON. File upload/download require
`enabled=True` and still refuse when the adapter is disabled.

## Minimal adapter usage

```python
from hedron_gradio import GradioClientAdapter, GradioEndpoint

# Preload endpoints for tests / offline; or enable live discover with gradio_client.
adapter = GradioClientAdapter(
    "http://127.0.0.1:7860",
    enabled=True,
    endpoints=(
        GradioEndpoint(
            name="predict",
            api_name="/predict",
            parameters={"text": {"type": "string"}},
            supports_stream=False,
        ),
    ),
)
print(adapter.discover())
print(adapter.predict("predict", {"text": "hello"}))
job_id = adapter.submit_job("predict", {"text": "queued"})
print(adapter.job_status(job_id))
```

Live discovery (no preloaded endpoints) uses `gradio_client.Client` view/API metadata after a
version check. Keep adapters **disabled by default** in production until intentionally opened.

HF vendor nodes emit InferenceWorkflow-compatible JSON (`node_id`, `label`, `ports`):

```python
from hedron_gradio import hf_space_node

node = hf_space_node("demo-space", "org/demo").to_workflow_node()
assert node["node_id"] == "demo-space"
```

See also [Model demos](model-demos.md) and
[`examples/model-demo-0.18`](https://github.com/eddiethedean/hedron/tree/main/examples/model-demo-0.18).

## Deliberate non-parity (do not expect automatic conversion)

- Mutable process globals as application state
- Default-public UI event → client API publication
- Raw HTML/JavaScript injection and browser-side Python snippets
- Current-directory file exposure as an implicit public root
- Temporary public share tunnels as a first-party feature
- Deployed host-code-editing / “vibe” modes that rewrite running app files
- Embedding Gradio’s UI runtime inside `hedron-core`
- Treating prediction feedback as labeled ground truth
- Real model downloads or Hub credentials in CI evidence

Use `hedron_gradio.migration.diagnose(...)` for reviewable findings when migrating an app
description. Diagnostics never rewrite source or publish endpoints.
