# What’s new in Hedron 0.26

**Published** as `v0.26.0`. Historical pin for this train: `hedron>=0.26.0,<0.27`.
Living tip: pin `hedron>=0.28.2,<0.29` — see [What’s new in 0.27](whats-new-0.27.md).

Hedron 0.26 strengthens the documented CRUD/admin path without promoting experimental
live transports. It validates upgrades from 0.25.2, makes the supported surface
machine-checkable, verifies secured Explorer behavior, and exercises the documented
multi-worker deployment pattern. Polling remains the production live-status path;
SSE, WebSocket, streaming, and preload stay experimental.

## 0.26.1 patch

The 0.26.1 patch fixes Explorer links under a reverse-proxy mount path, corrects
generated-project pins and optional install guidance, and strengthens
release/documentation verification. It adds tested OIDC and model-demo workflows,
checksummed release assets, and an exact-PyPI scaffold smoke before a GitHub Release is
created. It does not remove a Supported API. See the [release notes](release-notes.md)
for the complete adopter-facing list.

## What changes for application teams

- **Capability inventory** — Supported / Experimental / excluded surfaces for the
  three packages are machine-checked
  ([production-grade-inventory-026.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/production-grade-inventory-026.toml)).
- **Upgrade fixtures** — golden tests from `v0.25.2` facade identities, diagnostics,
  manifests, and HTMX interaction shapes.
- **Explorer** — secured mode requires auth; development mode is refused in production;
  Explorer is never required at runtime.
- **Ops** — reference-app multi-worker + Redis + reverse-proxy archetype remains the
  production kitchen sink; min-deps / offline-wheel smoke is gated.
- **Security review evidence** — redacted report and disposition ledger under
  `docs/acceptance/security-review-026/`.

No Supported CRUD/admin API removal is listed for 0.26.0. Existing 0.25.2 applications
should follow the historical 0.26 upgrade steps (now superseded by
[Upgrade to 0.27](upgrade.md)), update the lockfile, run Hedron diagnostics,
and repeat their application/browser tests.

## Non-goals (unchanged)

- No SSE/WS/streaming/preload promotion
- No claim that every Beta symbol is stable
- No public-by-default Explorer
- No `1.0` / SLA / certification

## Maintainer evidence

The release decision is D-054 / RFC-0057. Contract:
[STABILITY.md](../api/STABILITY.md) · [STABLE_FACADE.md](../api/STABLE_FACADE.md).
Acceptance packet:
[RELEASE_0_26](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_26.md).
