# Jobs and asynchronous work acceptance

These requirements own roadmap gate 0.7E. Evidence follows
[the release evidence policy](EVIDENCE.md).

| ID | Requirement | Required evidence | State |
|---|---|---|---|
| JOB-001 | `JobBackend` defines submission, stable job identity, state transitions, result/error metadata, and capability reporting without owning an application queue service. | Protocol tests against an in-memory test double and at least one external conformance implementation. | Verified |
| JOB-002 | Submission supports explicit idempotency and authorization/tenant scope; identifiers reveal no secrets. | Replay, cross-tenant, forged-ID, and redaction corpus. | Verified |
| JOB-003 | Retry, terminal failure, retention/expiry, cleanup, and cancellation-request semantics are explicit. | State-machine and backend-degradation tests. | Verified |
| JOB-004 | A 202 interaction returns an addressable status resource, `Retry-After`, and an accessible bounded-polling component with useful non-HTMX behavior. | HTTP/browser/a11y tests across supported adapters. | Verified |
| JOB-005 | Small host-framework background work is visibly distinct from durable work and cannot be accidentally promoted to a durable guarantee. | API/diagnostic tests and documentation examples. | Verified |
| JOB-006 | Optional SSE, if selected, preserves the same job contract and passes offline/CSP/auth/reconnect tests; otherwise polling remains sufficient. | Phase 0.10 SSE evidence (`SSE-10-001` / `JOB-006`); polling remains Supported. | Verified |

## Exit

Jobs remain application-operated infrastructure with a stable Hedron interaction contract. Polling
is the required baseline; no live transport is necessary to complete 0.7.
