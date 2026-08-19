# What's new in Hedron 0.34

**Published** as `v0.34.0`. Historical pin: `hedron>=0.34.0,<0.35`.
For new apps, use `hedron>=0.51.0,<0.52`; see [What’s new in 0.51](whats-new-0.51.md).

Phase 0.34 graduates **`hedron-gradio` `0.2.0` Beta** for production-grade remote Gradio and
bounded Hugging Face Space client interoperability. Default presentation refresh remains deferred
to the 0.35 fleet audit (`PRESENT-034` Deferred).

## Highlights

- **`GradioRemoteConfig`** — explicit destination allowlist, SSRF/private-host defenses, TLS and timeout defaults
- **Bounded artifacts** — upload/download size limits, extension allowlist, retention cleanup
- **Scoped jobs** — tenant/subject scope keys, deadlines, cancel, Hedron polling-friendly status payloads
- **HF vendor helpers** — Space base URL construction, cold-start/quota fixture translation with redaction
- **Posit Connect 2025.06.0** — native GUID path Supported (in addition to 2026.07.0); `pkg_resources` shim for 2025.06 FastAPI workers
- **Posit Workbench 2025.05.1** — `hedron-workbench`, `hedron-posit`, and `fastapi-workbench` Supported (in addition to 2026.07.0)
- **Production-grade inventory** — Supported vs Experimental vs Excluded surfaces in `production-grade-inventory-034.toml`

## Historical 0.34 install

```bash
python -m pip install -U "hedron[gradio]>=0.34.0,<0.35"
# or
python -m pip install -U "hedron-gradio>=0.2.0,<0.3"
```

## Migration from Alpha `0.1.x`

- Pin `hedron-gradio>=0.2.0,<0.3`
- Pass `GradioRemoteConfig.from_base_url(...)` or explicit `remote_config=` when enabling the adapter
- Review [Gradio migration guide](gradio-migration.md) for allowlist and non-parity notes

## See also

[RFC-0067](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0067-PRODUCTION-GRADE-GRADIO.md) ·
[RELEASE_0_34](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_34.md) ·
[#90](https://github.com/eddiethedean/hedron/issues/90)
