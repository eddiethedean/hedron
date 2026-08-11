# Production-quality maturity

How Hedron plans to raise **adopter trust** for the Supported surface — beyond the ops
checklist in [Production readiness](production-readiness.md).

**Living published train:** pin `hedron>=0.28.0,<0.29`. Capability maturity snapshot:
[What’s ready today](whats-ready.md). Program decision: **D-053**; RFC:
[RFC-0056](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0056-PRODUCTION-QUALITY.md)
(maintainer corpus on GitHub).

!!! note "Supported ≠ finished"

    Hedron is already **production-capable** for pinned CRUD/admin (pages, fragments, CSRF,
    adapters, polling jobs, DataEditor, production startup gates). This page tracks the
    **trust program** that closes remaining caveats — not a claim that Beta packages are
    unfinished for that narrow job.

## North star

Raise production-level quality as **trust in the Supported surface**:

- Expand the compatibility-protected (`stable`) API tier for a **narrow curated**
  Supported CRUD/HTMX/jobs facade ([STABLE_FACADE](../api/STABLE_FACADE.md) /
  [STABILITY expanded tier](../api/STABILITY.md#expanded-stable-tier-023)) — not every
  Supported row
- Finish human AT sessions (0.21 remaining P0) — CSRF composition (0.22) is **Published**
- Resolve live SSE/WebSocket: **0.24 Accepted `polling_only`** — polling is the Supported
  production story; live helpers remain experimental
  ([LIVE_DISPOSITION](../api/LIVE_DISPOSITION.md))
- Harden a reference production archetype and isolate high-risk experimental extras
  ([PRODUCTION_ARCHETYPE](../api/PRODUCTION_ARCHETYPE.md) — **Published** /
  Verified on 0.25)

Explicitly **not** the goal: calendar `1.0`, commercial SLA, WCAG/VPAT product claims, or
automatically promoting Alpha packages and experimental features without package-specific evidence.

## Priority stack

| Priority | Move | Status |
|---|---|---|
| P0 | Complete **0.21** human AT sessions + remediate | Engineering-complete / sessions outstanding |
| P0 | Ship **0.22** CSRF / SecurityPolicy composition | **Published** (`v0.22.0`) |
| P1 | Expand `stable` API tier (**0.23**) | **Published** (`v0.23.0`; D-053) — locked allowlist in ROADMAP §0.23 / [STABLE_FACADE](../api/STABLE_FACADE.md) |
| P1 | Live-transport disposition (**0.24**) — `polling_only` | **Published** (`v0.24.0`; D-053) — [LIVE_DISPOSITION](../api/LIVE_DISPOSITION.md) |
| P2 | Production archetype + load budgets + extras quarantine (**0.25**) | **Published** / Verified (`v0.25.0`; D-053) — [PRODUCTION_ARCHETYPE](../api/PRODUCTION_ARCHETYPE.md) |
| P3 | External security review + SBOM/evidence on every train tag | Process |
| P3 | Optional written `1.0` DoD **without a date** | Documented in D-053; no phase scheduled |

## Package-quality phases

The original D-053 trust program ends with the published 0.25 packet. Phase 0.26
extends its evidence discipline to the flagship/core/Explorer group; later roadmap
phases apply the same discipline to the remaining package fleet:

| Phase | Package group |
|---|---|
| 0.26 | `hedron-core`, `hedron`, and Explorer — **Published / Verified** |
| 0.27 | Data, Flask/Django adapters, HDJ, and curated extras — **Published / Verified** (D-055 / RFC-0058) |
| 0.28 | Charts and optional native acceleration |
| 0.29 | Conformance, sample plugin, simulation/notebook tooling, and Node/Java evaluators |
| 0.30 | Deny-by-default MCP projection |
| 0.31 | Gradio/Hugging Face client interoperability |
| 0.32 | Whole-fleet resolver, upgrade, supply-chain, and maturity closure |

Each phase requires an owning RFC/decision and Verified package-specific gates before a maturity
label changes. “Production-grade” applies only to the declared Supported surface: notebook remains
local development tooling, native remains optional, and experimental backends/namespaces remain
explicitly outside the claim.

Public phase table: [Roadmap](roadmap.md). Maintainer detail:
[`docs/ROADMAP.md`](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md).

## What to do today

1. Ship with pins and the [production readiness](production-readiness.md) checklist.
2. Prefer [polling](live-interaction.md) over `hedron.experimental` live helpers.
3. Treat Alpha extras (notebook, MCP, Gradio) and specialty stubs as pin-and-expect-churn.
4. Track trust-program progress on this page and the [public roadmap](roadmap.md).

## What we will not do

- Market experimental live transports or Alpha extras as production defaults
- Claim WCAG / legal / VPAT certification from automation or one AT packet
- Invent a commercial SLA without support staffing
- Chase SPA/React or Streamlit widget parity as a maturity path

Also: [Evaluate](evaluate.md) · [Enterprise diligence](enterprise-diligence.md) ·
[STABILITY](../api/STABILITY.md).
