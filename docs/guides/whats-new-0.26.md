# What’s new in Hedron 0.26

**Published** as `v0.26.0`. Pin `hedron>=0.26.0,<0.27`.

Phase **0.26** graduates `hedron-core`, `hedron`, and `hedron-explorer` to
**production-grade for the declared Supported CRUD/admin surface** (D-054 /
RFC-0057). Baseline: Published `v0.25.2`. Polling remains the Supported live-status
story; SSE/WS/streaming/preload stay experimental.

## For adopters

- **Production-grade inventory** — Supported / Experimental / excluded surfaces for the
  three packages are machine-checked
  ([production-grade-inventory-026.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/production-grade-inventory-026.toml)).
- **Upgrade fixtures** — golden tests from `v0.25.2` facade identities, diagnostics,
  manifests, and HTMX interaction shapes.
- **Explorer** — secured mode requires auth; development mode is refused in production;
  Explorer is never required at runtime.
- **Ops** — reference-app multi-worker + Redis + reverse-proxy archetype remains the
  production kitchen sink; min-deps / offline-wheel smoke is gated.
- **Security review packet** — redacted REPORT + disposition ledger under
  `docs/acceptance/security-review-026/`.

## Non-goals (unchanged)

- No SSE/WS/streaming/preload promotion
- No claim that every Beta symbol is stable
- No public-by-default Explorer
- No `1.0` / SLA / certification

Contract: [STABILITY.md](../api/STABILITY.md) · [STABLE_FACADE.md](../api/STABLE_FACADE.md).
Acceptance: [RELEASE_0_26](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_26.md).
