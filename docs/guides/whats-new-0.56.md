# What’s new in 0.56

Published in-tree **0.56.0** (PyPI still **0.54.0** while deferred). Pin
`hedron>=0.54.0,<0.55` from PyPI until a newer wheel lands; checkout tip is
`0.56.0`.

## 0.56.0

Security control plane and adversarial assurance (RFC-0083 / D-097 / D-098;
[#550](https://github.com/eddiethedean/hedron/issues/550)–[#557](https://github.com/eddiethedean/hedron/issues/557)):

- Evolved `SecurityPolicy` composition with control-plane knobs on existing
  `development` / `standard` / `strict` presets.
- Immutable request `SecurityContext` with explicit-field serialization and
  authority narrowing.
- Provenance-aware `SensitiveLabel` / `SensitiveValue` sink enforcement and
  audited declassification.
- Purpose-specific `compile_trust` for URL, selector, markup, SVG, and browser
  payloads.
- Shared deny-by-default `EgressPolicy` with redirect-hop revalidation.
- Nested monotonic `RequestBudget` ledger and locked performance ceilings.
- Short-lived `SignedIntent` + `SecurityKeyring` composed with CSRF and 0.55
  replay.
- Portable `hedron-security-1` conformance profile differentials
  (FastAPI/Flask/Django).
- Offline `hedron security-check` posture reports (text / JSON / SARIF).

Shared schema path: `hedron_core.security_plane` (re-exported as
`hedron.security_plane`). New APIs begin `beta`.

See [Release notes](release-notes.md) and [Installation](../getting-started/installation.md).
