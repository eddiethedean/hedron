# What’s new in Hedron 0.27

**Published** as `v0.27.0`. Pin `hedron>=0.27.0,<0.28`.

Hedron 0.27 graduates `hedron-data`, `hedron-flask`, `hedron-django`, `hedron-jinja`,
and `hedron-extras` to production-grade for their declared Supported inventories
(D-055 / RFC-0058). It validates upgrades from Published `v0.26.0`, freezes a
machine-readable satellite inventory, and exercises host-only plus portable
PAGE/FRAGMENT evidence. Polling remains the production live-status path; SSE,
WebSocket, streaming, and preload stay experimental.

## Highlights

- **Satellite graduation** — production-grade labels for data, Flask, Django, HDJ, and
  curated extras Supported inventories
  ([production-grade-inventory-027.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/production-grade-inventory-027.toml)).
- **Upgrade fixtures** — golden tests from `v0.26.0` data/adapter/HDJ/extras public
  contracts.
- **Host evidence** — Flask/Django/data/HDJ/extras smokes and portable PAGE/FRAGMENT
  parity without promoting experimental live transports.
- **Diagnostics** — `hedron check` scopes Django / Plotly-Altair notices to detected
  adapters and chart extras (`#54`); `--all-compat` remains for the global summary.
- **HTMX PAGE order** — inject the HTMX core runtime before bundled extensions so
  deferred `head-support` / `sse` scripts can register (`#55`).
- **OOB shell safety** — warn when the same id appears in both `select_oob` and
  `OobUpdate`; prefer one mechanism and default `OobUpdate` `innerHTML` swaps (`#57`).
- **Shared static mounts** — Flask and Django adapters mount `/hedron-static` and inject
  shared PAGE assets like FastAPI.

## What changes for application teams

- **Pin the 0.27 train** — coordinate `hedron`, adapters, and graduated extras on
  `>=0.27.0,<0.28`.
- **Charts / sample kit** — use the `>=0.1.7,<0.2` satellite floor
  (`hedron[charts]>=0.27.0,<0.28`).
- **Static assets** — keep `/hedron-static/` reachable behind reverse proxies on every
  host adapter.
- **Explorer** — still never required at runtime; development mode remains refused in
  production.
- **Ops** — multi-worker + Redis + reverse-proxy archetype remains the production kitchen
  sink.

No Supported CRUD/admin API removal is listed for 0.27.0. Existing 0.26 applications
should follow [Upgrade to 0.28](upgrade.md), update the lockfile, run Hedron diagnostics,
and repeat their application/browser tests.

## Non-goals (unchanged)

- No SSE/WS/streaming/preload promotion
- No claim that every Beta symbol is stable
- No public-by-default Explorer
- No graduation of charts / native / MCP / Gradio / conformance tooling in this phase
- No `1.0` / SLA / certification

## Maintainer evidence

The release decision is D-055 / RFC-0058. Contract:
[STABILITY.md](../api/STABILITY.md) · [STABLE_FACADE.md](../api/STABLE_FACADE.md).
Acceptance packet:
[RELEASE_0_27](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_27.md).
Security review: `docs/acceptance/security-review-027/`.
