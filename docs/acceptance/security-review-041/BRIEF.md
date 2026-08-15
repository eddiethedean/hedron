# Security and privacy review brief — phase 0.41

**Status:** Completed with redacted report and disposition ledger. This scoped review does not claim
the independent whole-platform review owned by 0.42.

## Scope

- Untrusted `CustomEvent` details, graph registration/target/action allowlists, authorization recheck,
  cycle/depth/payload bounds, cancellation, concurrency, and fallback.
- Draft eligibility, subject/authority binding, namespace collision, TTL/ceilings/single-consume,
  logout/submit/discard clearing, storage denial/quota/corruption, downgrade, rollback, and same-origin
  boundaries.
- Explicit rejection of secrets, auth/CSRF material, capabilities, files/blobs, trusted HTML,
  arbitrary URLs, server state, raw responses/errors, and undeclared fields.
- Same-origin navigation interception, URL/query/fragment privacy, history cache, focus/title/scroll,
  preload, View Transitions, CSP, Trusted Types, and reduced-motion handling.
- Trace schema minimization and injection; trace sink failure must not affect application behavior.
- Slow/failing/incompatible element isolation from unrelated navigation, forms, and HTMX regions.

## Adversarial corpus

Malformed/version-skewed events and envelopes; forged subject/authority fingerprints; replay and
double consume; cross-route/app key collision; Unicode/control data; oversized/deep/cyclic graphs;
storage exceptions/quota; malicious URLs; rapid popstate/swap/cancel races; late responses; failed
module/preload/transition/trace sink; and content-bearing telemetry attempts.

## Out of scope

Whole-platform production-grade review/graduation (0.42), cross-origin composition, cross-tab or
durable draft synchronization, offline authority, service-worker routing, and Supported human-AT
claims.

## Tracking

[#96](https://github.com/eddiethedean/hedron/issues/96) · D-069 · RFC-0060 D-069 answers.
