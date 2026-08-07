---
status: shipped
---

# Security audit sink

!!! note "Stability"

    Classifications live in [STABILITY.md](STABILITY.md). The audit sink is a
    **Supported** optional capability. Package maturity remains **Beta** — pin versions.
    Sinks must never break request handling — emit failures are swallowed and logged.

**Status:** Shipped in `0.13.0`

Framework-boundary events (CSRF reject, HTMX target reject, Explorer deny, production
gate failure) can be forwarded to an application sink for SIEM / structured logs.

## Imports

```python
from hedron_core.audit import (
    SecurityAuditEventType,
    StructuredLogAuditSink,
    set_security_audit_sink,
)
```

## Public symbols

| Symbol | Role |
|---|---|
| `SecurityAuditEvent` / `SecurityAuditEventType` | Event payload |
| `SecurityAuditSink` | Protocol with `emit(event)` |
| `StructuredLogAuditSink` | Default: redacted structured logging |
| `set_security_audit_sink` / `get_security_audit_sink` | Process-local configuration |
| `emit_security_audit` | Framework / app emit helper |

## Example

```python
from hedron_core.audit import StructuredLogAuditSink, set_security_audit_sink

set_security_audit_sink(StructuredLogAuditSink())
# or your own sink implementing emit(SecurityAuditEvent)
```

Event types: `csrf_rejected`, `htmx_target_rejected`, `explorer_denied`,
`production_gate_failed`. Attributes are secret-redacted before logging.

## Errors / failure modes

| Situation | Behavior |
|---|---|
| No sink configured | Emits are no-ops (safe default) |
| Sink `emit` raises | Swallowed and logged — request handling continues |
| Unknown event type | Application sinks should ignore or log; framework only emits known types |
| Secrets in attributes | Redacted before structured logging |

## Related

- [Threat model](../guides/threat-model.md) · [Security](../guides/security.md)
- [What’s ready](../guides/whats-ready.md)
