# Production-quality maturity

How Hedron plans to raise **adopter trust** for the Supported surface — beyond the ops
checklist in [Production readiness](production-readiness.md).

**Living published train:** pin `hedron>=0.20.0,<0.21`. Capability maturity SSOT:
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

- Expand the compatibility-protected (`stable`) API tier for Supported CRUD/HTMX/jobs
- Finish human AT (0.21) and CSRF composition (0.22)
- Resolve live SSE/WebSocket: prove ops evidence **or** keep polling as the only production story
- Harden a reference production archetype and quarantine Alpha/landmine extras

Explicitly **not** the goal: calendar `1.0`, commercial SLA, WCAG/VPAT product claims, or
promoting every Alpha extra.

## Priority stack

| Priority | Move | Status |
|---|---|---|
| P0 | Complete **0.21** human AT sessions + remediate | Engineering-complete / sessions outstanding |
| P0 | Ship **0.22** CSRF / SecurityPolicy composition | Planned |
| P1 | Expand `stable` API tier (**0.23**) | Planned (D-053) |
| P1 | Live-transport disposition (**0.24**) — prove gates or polling-only docs | Planned (D-053) |
| P2 | Production archetype + load budgets + extras quarantine (**0.25**) | Planned (D-053) |
| P3 | External security review + SBOM/evidence on every train tag | Process |
| P3 | Optional written `1.0` DoD **without a date** | Documented in D-053; no phase scheduled |

Public phase table: [Roadmap](roadmap.md). Maintainer detail:
[`docs/ROADMAP.md`](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md).

## What to do today

1. Ship with pins and the [production readiness](production-readiness.md) checklist.
2. Prefer [polling](live-interaction.md) over `hedron.experimental` live helpers.
3. Treat Alpha extras (charts, notebook, MCP, Gradio) and specialty stubs as pin-and-expect-churn.
4. Track trust-program progress on this page and the [public roadmap](roadmap.md).

## What we will not do

- Market experimental live transports or Alpha extras as production defaults
- Claim WCAG / legal / VPAT certification from automation or one AT packet
- Invent a commercial SLA without support staffing
- Chase SPA/React or Streamlit widget parity as a maturity path

Also: [Evaluate](evaluate.md) · [Enterprise diligence](enterprise-diligence.md) ·
[STABILITY](../api/STABILITY.md).
