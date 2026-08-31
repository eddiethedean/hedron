---
status: shipped
---

# Distributed tracing

!!! note "Stability"

    Classifications live in [STABILITY.md](STABILITY.md). Optional tracing is a
    **Supported** optional capability via `hedron[otel]` / `hedron.tracing` on the
    current train. The stable platform package is `hedron`; this optional API retains its
    documented level. Disabled by
    default; exporter absence must not change component semantics.

**Status:** Available on 1.0 (introduced in `0.13.0`)

## Install

```bash
pip install "hedron[otel]>=1.0.1,<1.1"
```

## Configure

```python
from hedron.tracing import configure_tracing, span

configure_tracing(enabled=True, sample_rate=1.0, service_name="my-app")

with span("handler.render", route="/"):
    ...
```

### `configure_tracing`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `enabled` | `bool` | `True` | Master switch |
| `sample_rate` | `float` | `1.0` | Fraction of spans to record (`0.0`–`1.0`) |
| `service_name` | `str` | `"hedron"` | Service name attribute |

**Returns:** `TraceConfig` (also stored as process global).

### `span` / `start_span`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | required | Span name |
| `**attributes` | any | — | Span attributes (secret-redacted) |

**Returns:** context manager (`span`) or span object (`start_span`). When disabled /
unsampled, yields `TracingDisabled` (no-op).

## Public symbols

| Symbol | Role |
|---|---|
| `configure_tracing` | Opt-in process config |
| `get_trace_config` | Read current config |
| `span` / `start_span` | Redacted span helpers |
| `TraceConfig` / `TracingDisabled` | Config + no-op span when off |

## Errors / failure modes

| Situation | Behavior |
|---|---|
| `hedron[otel]` not installed | Spans are no-ops (`TracingDisabled`) |
| `configure_tracing(enabled=False)` | Spans are no-ops |
| Exporter / SDK failure | Fail soft — component semantics unchanged |
| Secrets in span attributes | Redacted before export |

## Related

- [Observability](../guides/observability.md)
- [What’s ready](../guides/whats-ready.md)
- Autodoc members on [AUTODOC.md](AUTODOC.md)
