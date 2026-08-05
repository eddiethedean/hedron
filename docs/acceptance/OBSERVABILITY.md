# Observability acceptance

These requirements own the diagnostic and operating visibility portions of roadmap gates 0.7B and
0.8. Evidence follows [the release evidence policy](EVIDENCE.md).

| ID | Requirement | Required evidence | State |
|---|---|---|---|
| OBS-001 | Logs and traces use stable route/component/job/cache identifiers and redact secret values before storage/export. | Adversarial redaction corpus across log, trace, Explorer, and error paths. | Verified |
| OBS-002 | Timing separates dependency/I/O, render, serialization, cache wait/load, browser abort, timeout, server cancellation, and completed-but-discarded work. | Structured event schema tests and Explorer trace snapshots. | Verified |
| OBS-003 | Cache and job backend failures expose actionable owner/capability context without payload leakage. | Degradation matrix using external conformance implementations. | Verified |
| OBS-004 | Standard-library logging is sufficient by default; any tracing/export integration is optional and lazy. | Clean core/adapter imports without telemetry packages plus optional integration tests. | Verified |
| OBS-005 | Health/readiness and audit events are bounded, rate-aware, and safe under repeated failures. | Load/failure tests with memory and payload bounds. | Verified |
| OBS-013 | Optional first-party distributed tracing with redaction, sampling, stable span ownership, and exporter-failure isolation; disable without semantic change. | `TRACE-013` unit evidence; `hedron[otel]` lazy import. | Verified |
| AUDIT-013 | `SecurityAuditSink` receives CSRF/HTMX/Explorer/production-gate events without secrets. | `AUDIT-013` capture + redaction corpus. | Verified |

## Exit

Operators can distinguish latency, cancellation, cache/job degradation, and configuration failures
without enabling Explorer or exposing application data. Optional telemetry products are integrations,
not required runtime dependencies. Phase 0.13 adds opt-in tracing and security audit sinks on top of
the stdlib floor.
