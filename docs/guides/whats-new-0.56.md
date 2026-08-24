# What’s new in 0.56

Published **0.56.0** on PyPI. This is a historical train; the current published
train is **0.63.x** — see [What’s new in 0.62](whats-new-0.61.md). Pin
`hedron>=0.63.0,<0.64` from PyPI for current applications.

## 0.56.1

Historical in-tree quality patch (superseded by living tip 0.57.0). Install from PyPI with
`hedron>=0.63.0,<0.64`.

- Workspace Python quality upgrade: typing debt burn-down across routing, data, charts,
  maps, and adapters; safer best-effort exception logging; ASYNC/PTH/DTZ/RET ruff rules;
  maintainability refactors without public API breaks.
- `fastapi-workbench` ships a `py.typed` marker.

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
