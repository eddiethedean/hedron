# hedron-gradio

[![PyPI](https://img.shields.io/pypi/v/hedron-gradio.svg)](https://pypi.org/project/hedron-gradio/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-gradio.svg)](https://pypi.org/project/hedron-gradio/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Production-grade Gradio client interoperability for Hedron.

Endpoint discovery, allowlisted remote calls, typed predict / job / stream helpers,
bounded file transport, and Hugging Face vendor-node adapters — without embedding
Gradio’s UI runtime in core. Disabled by default; absence of this package adds no core
dependency or startup cost.

Also available as the flagship extra `hedron[gradio]`.

**Package maturity:** Beta · **Train:** `0.2.x` · pin `>=0.2.0,<0.3`

## Install

```bash
pip install "hedron-gradio>=0.2.0,<0.3"
# or
uv add "hedron-gradio>=0.2.0,<0.3"
# via flagship (at 0.34 train cut):
pip install "hedron[gradio]>=0.40.0,<0.41"
```

Requires Python 3.11–3.14.

For **live** Gradio endpoints, also install `gradio_client`. The package imports
without `gradio` or `gradio_client` installed; with declared endpoints and no
client library, helpers return stub-friendly status payloads.

## Quick start

```python
from hedron_gradio import GradioClientAdapter, GradioEndpoint, GradioRemoteConfig

config = GradioRemoteConfig.from_base_url("https://example.gradio.live")
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

## Public API

| Symbol | Role |
|---|---|
| `GradioRemoteConfig` | Allowlisted destination policy |
| `GradioClientAdapter` | Discovery, predict, jobs, streams, file transfer |
| `GradioEndpoint` | Declared endpoint metadata |
| `GradioRemoteError` | Remote failure signal |
| `HuggingFaceVendorNode` / `hf_space_node` | HF Space vendor helpers |

## Links

- [Package docs](https://hedron.readthedocs.io/en/latest/packages/hedron-gradio/)
- [Gradio migration guide](https://hedron.readthedocs.io/en/latest/guides/gradio-migration/)
- [What's new in 0.34](https://hedron.readthedocs.io/en/latest/guides/whats-new-0.34/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-gradio/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-gradio)
- [Issues](https://github.com/eddiethedean/hedron/issues)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
