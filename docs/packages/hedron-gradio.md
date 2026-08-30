# hedron-gradio

Production-grade Gradio client interoperability for Hedron.

**Package maturity:** Beta · **Repository package version:** `0.2.3` · pin `>=0.2.3,<0.3`
**Flagship extra:** `hedron[gradio]` · **Import:** `hedron_gradio`
Requires `hedron-core>=1.0.0,<2.0`.
Provides allowlisted remote endpoint discovery, predict / job / stream helpers with explicit
schemas, bounded
file transport, and Hugging Face vendor-node adapters — **without** embedding Gradio’s UI runtime
in core.

Disabled by default; absence adds no core dependency or startup cost.

## Install

```bash
pip install "hedron[gradio]>=1.0.0,<1.1"
# or
pip install "hedron-gradio>=0.2.3,<0.3"
```

For **live** Gradio endpoints, also install `gradio_client`. The package imports without
`gradio` or `gradio_client`; with declared endpoints and no client library, helpers return
stub-friendly status payloads.

## When to use

- Calling remote Gradio apps / HF Spaces from Hedron workflows with explicit allowlists
- Predict / job / stream helpers with explicit schemas without pulling Gradio UI into core

This is **not** production parity with Gradio’s full UI. Prefer Hedron-native inference / jobs
surfaces when you control the model server — [Model demos](../guides/model-demos.md).

## Quick start

```python
from hedron_gradio import GradioClientAdapter, GradioEndpoint, GradioRemoteConfig

config = GradioRemoteConfig.from_base_url("https://demo.example.invalid")
adapter = GradioClientAdapter(
    base_url=config.base_url,
    enabled=True,
    remote_config=config,
    endpoints=(GradioEndpoint(name="predict", api_name="/predict", parameters={}),),
)

endpoints = adapter.discover()
result = adapter.predict("predict", {"text": "hi"})
```

With `enabled=False` (the default), `discover()` returns empty.

## Surfaces

| Symbol | Role |
|---|---|
| `GradioRemoteConfig` | Allowlisted destination policy |
| `GradioClientAdapter` | Discovery, predict, jobs, streams, file transfer |
| `GradioEndpoint` | Declared endpoint metadata |
| `GradioRemoteError` | Remote failure signal |
| `HuggingFaceVendorNode` / `hf_space_node` | HF Space vendor helpers |

## Errors and failure modes

| Condition | Behavior |
|---|---|
| `enabled=False` | Empty discovery — no remote calls |
| Undeclared / private host | `GradioRemoteError` (fail closed) |
| Missing `gradio_client` for live calls | Stub / unavailable path |
| Expecting Gradio UI embedding | Out of scope — client interop only |

## Related docs

- Guide: [Gradio migration](../guides/gradio-migration.md)
- [What's new in 0.34](../guides/whats-new-0.34.md)
- [Model demos / inference](../guides/model-demos.md)

## Links

- [PyPI](https://pypi.org/project/hedron-gradio/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-gradio/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-gradio)
