# hedron-gradio

Experimental Gradio client interoperability for Hedron.

**Package maturity:** Experimental Alpha (`0.1.x`) · pin `>=0.1.0,<0.2`  
**Flagship extra:** `hedron[gradio]` · **Import:** `hedron_gradio`  
Provides endpoint discovery, typed predict / job / stream helpers, and Hugging Face
vendor-node adapters — **without** embedding Gradio’s UI runtime in core.

Disabled by default; absence adds no core dependency or startup cost.

## Install

```bash
pip install "hedron[gradio]>=0.26.0,<0.27"
# or
pip install "hedron-gradio>=0.1.0,<0.2"
```

For **live** Gradio endpoints, also install `gradio_client`. The package imports
without `gradio` or `gradio_client`; with declared endpoints and no client library,
helpers return stub-friendly status payloads.

## When to use

- Calling remote Gradio apps / HF Spaces from Hedron workflows
- Typed predict / job / stream helpers without pulling Gradio UI into core

This is **not** production parity with Gradio’s full UI. Prefer Hedron-native
inference / jobs surfaces when you control the model server —
[Model demos](../guides/model-demos.md).

## Quick start

```python
from hedron_gradio import GradioClientAdapter, GradioEndpoint, hf_space_node

adapter = GradioClientAdapter(
    base_url="https://example.gradio.live",
    enabled=True,
    endpoints=(GradioEndpoint(name="predict", api_name="/predict", parameters={}),),
)

endpoints = adapter.discover()
result = adapter.predict("predict", {"text": "hi"})

node = hf_space_node("n1", "owner/space")
```

With `enabled=False` (the default), `discover()` returns empty.

## Surfaces

| Symbol | Role |
|---|---|
| `GradioClientAdapter` | Discovery, predict, jobs, streams, file transfer |
| `GradioEndpoint` | Declared endpoint metadata |
| `GradioRemoteError` | Remote failure signal |
| `HuggingFaceVendorNode` / `hf_space_node` | HF Space vendor helpers |

Adapter methods include `discover()`, `predict()`, `submit_job()`, `job_status()`,
`cancel_job()`, `stream_results()`, `upload_file()`, `download_artifact()`, and
`check_version_compat()`.

## Errors and failure modes

| Condition | Behavior |
|---|---|
| `enabled=False` | Empty discovery — no remote calls |
| Missing `gradio_client` for live calls | Stub / unavailable path — install client for live |
| Remote Gradio failure | `GradioRemoteError` |
| Expecting Gradio UI embedding | Out of scope — client interop only |

## Related docs

- Guide: [Gradio migration](../guides/gradio-migration.md)
- [Model demos / inference](../guides/model-demos.md) · [Inference API](../api/INFERENCE.md)
- [What’s ready](../guides/whats-ready.md)

## Links

- [PyPI](https://pypi.org/project/hedron-gradio/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-gradio/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-gradio)
