# Observability acceptance

These requirements own the diagnostic and operating visibility portions of roadmap gates 0.7B and
0.8. Evidence follows [the release evidence policy](EVIDENCE.md).

| ID | Requirement | Required evidence | State |
|---|---|---|---|
| OBS-001 | Logs and traces use stable route/component/job/cache identifiers and redact secret values before storage/export. | Adversarial redaction corpus across log, trace, Explorer, and error paths. | Planned |
| OBS-002 | Timing separates dependency/I/O, render, serialization, cache wait/load, browser abort, timeout, server cancellation, and completed-but-discarded work. | Structured event schema tests and Explorer trace snapshots. | Planned |
| OBS-003 | Cache and job backend failures expose actionable owner/capability context without payload leakage. | Degradation matrix using external conformance implementations. | Planned |
| OBS-004 | Standard-library logging is sufficient by default; any tracing/export integration is optional and lazy. | Clean core/adapter imports without telemetry packages plus optional integration tests. | Planned |
| OBS-005 | Health/readiness and audit events are bounded, rate-aware, and safe under repeated failures. | Load/failure tests with memory and payload bounds. | Planned |

## Exit

Operators can distinguish latency, cancellation, cache/job degradation, and configuration failures
without enabling Explorer or exposing application data. Optional telemetry products are integrations,
not required runtime dependencies.
