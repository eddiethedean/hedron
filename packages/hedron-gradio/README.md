# hedron-gradio

Experimental Alpha Gradio client interoperability for Hedron (RFC-0049). Provides
endpoint discovery, typed predict/job/stream helpers, file/artifact transport,
and Hugging Face vendor-node adapters — without embedding Gradio's UI runtime
in core.

Disabled by default; absence of this package adds no core dependency or startup
cost.

```bash
pip install hedron-gradio
```

Optional runtime dependency: install `gradio_client` when calling live Gradio
endpoints. The package imports without `gradio` or `gradio_client` installed.

See [Gradio feature cross-check](https://github.com/eddiethedean/hedron/blob/main/docs/GRADIO_FEATURE_CROSSCHECK.md),
[RFC-0049](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0049-GRADIO-ADAPTER.md),
and the public [Gradio migration guide](https://hedron.readthedocs.io/en/latest/guides/gradio-migration/)
for supported version range and deliberate non-parity.
