# Gradio migration inventory

**Evidence:** `MIGRATE-018` · **RFC:**
[RFC-0049](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0049-GRADIO-ADAPTER.md) ·
**Cross-check:**
[GRADIO_FEATURE_CROSSCHECK.md](https://github.com/eddiethedean/hedron/blob/main/docs/GRADIO_FEATURE_CROSSCHECK.md)

This inventory maps Gradio outcomes to Hedron without claiming automatic conversion. Install the
optional Alpha package only when needed:

```bash
pip install "hedron[gradio]"
```

Absence of `hedron-gradio` adds no core dependency, route, asset, or startup cost.

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
