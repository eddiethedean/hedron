# hedron-gradio

[![PyPI](https://img.shields.io/pypi/v/hedron-gradio.svg)](https://pypi.org/project/hedron-gradio/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-gradio.svg)](https://pypi.org/project/hedron-gradio/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Experimental Gradio client interoperability for Hedron.

Endpoint discovery, typed predict / job / stream helpers, file and artifact
transport, and Hugging Face vendor-node adapters — without embedding Gradio’s UI
runtime in core. Disabled by default; absence of this package adds no core
dependency or startup cost.

Also available as the flagship extra `hedron[gradio]`.

**Package maturity:** Experimental Alpha (`0.1.x`) · pin `>=0.1.0,<0.2` and expect churn

## Install

```bash
pip install "hedron-gradio>=0.1.0,<0.2"
# or
uv add "hedron-gradio>=0.1.0,<0.2"
# via flagship:
pip install "hedron[gradio]>=0.30.0,<0.31"
```

Requires Python 3.11–3.14.

For **live** Gradio endpoints, also install `gradio_client`. The package imports
without `gradio` or `gradio_client` installed; with declared endpoints and no
client library, helpers return stub-friendly status payloads.

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

## Public API

| Symbol | Role |
|---|---|
| `GradioClientAdapter` | Discovery, predict, jobs, streams, file transfer |
| `GradioEndpoint` | Declared endpoint metadata |
| `GradioRemoteError` | Remote failure signal |
| `HuggingFaceVendorNode` / `hf_space_node` | HF Space vendor helpers |

## Links

- [Package docs](https://hedron.readthedocs.io/en/latest/packages/hedron-gradio/)
- [Gradio migration guide](https://hedron.readthedocs.io/en/latest/guides/gradio-migration/)
- [What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-gradio/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-gradio)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- [`hedron`](https://pypi.org/project/hedron/)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
