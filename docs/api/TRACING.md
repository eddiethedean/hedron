---
status: shipped
---

# Distributed tracing

!!! note "Stability"

    Classifications live in [STABILITY.md](STABILITY.md). Optional tracing is a
    **Supported** optional capability via `hedron[otel]` / `hedron.tracing` on the
    current train. Package maturity remains **Beta** — pin versions. Disabled by
    default; exporter absence must not change component semantics.

**Status:** Shipped in `0.13.0`

## Install

```bash
pip install "hedron[otel]>=0.21.0,<0.22"
```

## Configure

```python
from hedron.tracing import configure_tracing, span

configure_tracing(enabled=True, sample_rate=1.0, service_name="my-app")

with span("handler.render", route="/"):
    ...
```

## Public symbols

| Symbol | Role |
|---|---|
| `configure_tracing` | Opt-in process config (`enabled`, `sample_rate`, `service_name`) |
| `get_trace_config` | Read current config |
| `span` / `start_span` | Redacted span context managers |
| `TraceConfig` / `TracingDisabled` | Config + no-op span when off |

Attributes are secret-redacted. When OpenTelemetry is missing or fails, spans become
no-ops.

## Errors / failure modes

| Situation | Behavior |
|---|---|
| `hedron[otel]` not installed | Spans are no-ops (`TracingDisabled`) |
| `configure_tracing(enabled=False)` | Spans are no-ops |
| Exporter / SDK failure | Fail soft — component semantics unchanged |
| Secrets in span attributes | Redacted before export |

## Related

- [What’s new in 0.13](../guides/whats-new-0.13.md)
- [What’s ready](../guides/whats-ready.md)
- Autodoc members on [AUTODOC.md](AUTODOC.md)
