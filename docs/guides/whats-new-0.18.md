# What’s new in 0.18

Phase **0.18** adds model demos and inference workflows — fail-closed demo composition,
governed feedback, inference scheduling over `JobBackend`, an interaction recorder, typed
workflows, and optional Gradio interop. See
[release gate](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/release-gate-0.18.toml).

## Highlights

- **`InferenceInterface` / `ModelDemo`:** reviewable demos only from explicitly registered
  actions or callable adapters (RFC-0045). Bare callables fail closed.
- **`ExampleSet`, `PredictionLabel`, `ParameterViewer`, `Dialogue`, `PredictionFeedback`:**
  provenance, accessible presentation, and explicit-consent feedback sinks (RFC-0046).
- **`InferencePolicy`:** admission, fair queues, concurrency groups, batch windows, ETA, and
  cancelable generator streaming over durable `JobBackend` (RFC-0047). In-process queues are
  development-only.
- **`ModelDemoScenario`:** synthetic scenario kit — no real models in CI.
- **`InteractionRecorder`:** redacted Python/HTTP snippets for explicitly public endpoints
  (RFC-0048).
- **`InferenceWorkflow`:** versioned permissioned DAGs with structured list/outline/table editor;
  graph JSON cannot execute host code or auto-publish HTTP/MCP (RFC-0050).
- **`hedron-gradio` (Experimental / Alpha):** Gradio client discovery/jobs/streaming plus HF
  vendor nodes; disabled-by-default discover (RFC-0049).

## Honesty

- Feedback is never silently enabled and never treated as ground truth.
- Gradio interoperability is **not** Supported production parity; pin Alpha and expect churn.
- No default-public UI→API publication, share tunnels, or cwd file exposure.

## Upgrade notes

Pin `hedron>=0.20.0,<0.21`. Install `hedron[gradio]` only when needed.
See [Gradio migration](gradio-migration.md).
