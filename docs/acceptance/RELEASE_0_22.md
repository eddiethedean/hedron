# Hedron `v0.22` CSRF and SecurityPolicy composition acceptance

Phase 0.22 ships pluggable CSRF strategies, composable `SecurityPolicy` header
merge/override, and `CsrfField` plus first-class HTMX kwargs on `Form` so apps that
own sessions and CSP can keep Hedron’s form/HTMX integration without Starlette cookie
sessions or an all-or-nothing header off-switch.
Evidence is indexed by [`release-gate-0.22.toml`](release-gate-0.22.toml).
**Zero Deferred:** every 0.22-owned gate row must be Verified at cut.

Owning decision: [D-051](../DECISIONS.md) (split from 0.20). RFC baselines:
[RFC-0012](../rfcs/RFC-0012-SECURITY.md) (security),
[RFC-0019](../rfcs/RFC-0019-TESTING.md) (composition evidence),
[RFC-0024](../rfcs/RFC-0024-DEVELOPER-EXPERIENCE.md) (`CsrfField` / Form HTMX).
Contract: [CSRF composition](../api/CSRF_COMPOSITION.md).
Linked issues (history): [#36](https://github.com/eddiethedean/hedron/issues/36),
[#37](https://github.com/eddiethedean/hedron/issues/37),
[#38](https://github.com/eddiethedean/hedron/issues/38).

## Spec packet

- [x] ROADMAP §0.22 scope accepted; D-051 recorded; packet refined with named gate IDs.
- [x] Gate checker loads the 0.22 manifest.
- [x] Contract sketch published ([CSRF_COMPOSITION.md](../api/CSRF_COMPOSITION.md)).
- [x] `CSRF-022` / `HEADERS-022` / `FORM-022` Verified.
- [x] `REGRESS-022` / `PKG-022` at cut (train `0.22.0`).

## Exit

- [x] Every 0.22-owned release-gate row is `Verified`.
- [x] Security guide, CSRF composition contract, and What’s ready agree on Supported claims
  for strategies / header merge / `CsrfField`.
