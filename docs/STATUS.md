# Specification and implementation status

**Roadmap position:** phase 0.10 **published** as `v0.10.0` (packages `0.10.0`, 2026-08-04).
**Date:** 2026-08-04
**Implementation:** `hedron` / `hedron-core` / `hedron-explorer` / `hedron-sample-kit` /
`hedron-data` / `hedron-charts` / `hedron-flask` / `hedron-django` / `hedron-jinja` `0.10.0`
(MIT licensed, D-033)
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`; Alpha — `hedron-charts`, `hedron-sample-kit`.

**Phase focus:** live interaction and navigation (RFC-0032 / D-044 / D-045): official HTMX SSE,
focused streaming, page/session WebSocket channels, Chat/Dialog, media chunk transport contracts,
HDJ head/two-phase streaming, and opt-in navigation preload. Polling and ordinary HTTP remain
Supported fallbacks. Native Flask/Django depth remains assigned to **0.11**; capture UI to 0.15.

## Supported vs Deferred (operator view)

Adopter summary: [What’s ready today](guides/whats-ready.md). Rule of thumb: do not market a
capability as unqualified **Supported** when its owning gate row is **Deferred** — say
**API Supported / ops evidence incomplete** instead.

| ID | Topic | Disposition | Notes |
|---|---|---|---|
| — | Typed pages, HTMX fragments, CSRF profiles, CLI | Verified (0.10 gate) | FastAPI flagship |
| — | Live transport **APIs** (SSE, stream, WS helpers) | Verified API surface | FastAPI only |
| `BROWSER-10-001` | Full three-engine live browser matrix | **Deferred** → `0.10.x` | Beyond asset/HTMX smoke |
| `PERF-10-001` | Load/proxy backpressure evidence | **Deferred** → `0.10.x` | SSE/WS ops proof |
| `EXPLORER-10-001` | Explorer live traces | **Deferred** → `0.10.x` | |
| `EXAMPLES-10-001` | First-party live sample | Verified learning path | [`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction) (poll + stream) |
| — | Flask/Django adapter matrix | Supported routing/HTMX | QuerySet DataSource + Hedron Django forms → **0.11** |
| — | Official HTMX SSE on Flask/Django | Deferred | Use polling |

## Phase 0.10 evidence

- Closure index: [release-gate-0.10.toml](acceptance/release-gate-0.10.toml)
  (`Verified` or owned `Deferred`).
- Acceptance: [RELEASE_0_10.md](acceptance/RELEASE_0_10.md) and
  [RFC-0032](rfcs/RFC-0032-LIVE-TRANSPORT.md).
- Stability: [api/STABILITY.md](api/STABILITY.md).
- Compatibility / deprecation: [COMPATIBILITY.md](COMPATIBILITY.md).
- Upgrade: [guides/upgrade.md](guides/upgrade.md).
- Supply chain: `scripts/build_evidence_bundle.py` and `scripts/verify_pkg_10.py`.
- Cut procedure: [RELEASE.md](RELEASE.md) (next cut: **0.11**). Historical cuts:
  [`docs/archive/RELEASE_HISTORY_0.1-0.10.md`](https://github.com/eddiethedean/hedron/blob/main/docs/archive/RELEASE_HISTORY_0.1-0.10.md).

## Next capability phase

**0.11** — native Flask/Django depth (forms/QuerySet/CSP reconciliation as scoped in the
roadmap). Track progress in [ROADMAP.md](ROADMAP.md) and the public
[roadmap guide](guides/roadmap.md).
