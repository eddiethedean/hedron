# RFC-0056: Production-quality maturity program

**Status:** Accepted
**Phase:** Program umbrella for 0.21–0.25 (D-053); Living published train is **0.26**
(`v0.25.0`; prior packets **0.23** stable-tier / **0.24** live disposition)
**Stability:** `beta` (process / roadmap); does not by itself promote package maturity or
API levels
**Evidence:** Priority ownership in ROADMAP §0.21–§0.25; release gates
`release-gate-0.21.toml` … `release-gate-0.25.toml` as each packet is refined
**Related:** D-038, D-051, D-052, D-053; RFC-0029; [STABILITY.md](../api/STABILITY.md);
[guides/production-quality.md](../guides/production-quality.md);
[guides/whats-ready.md](../guides/whats-ready.md)

## Summary

Define how Hedron raises **production-level quality** as adopter trust in the Supported
surface: finish already-owned trust gaps, expand the minimal `stable` API tier, resolve the
permanent “experimental live transports” fog, harden a production archetype, and quarantine
Alpha/landmine extras — without scheduling a calendar `1.0`, inventing an SLA, or claiming
WCAG/VPAT certification.

## Motivation and background

Hedron 0.20 already ships Beta packages that are **production-capable** for pinned CRUD/admin
(typed pages, HTMX fragments, CSRF profiles, adapters, polling jobs, DataEditor, production
startup gates). Ecosystem trust gaps remain:

- Most public APIs are compatibility `beta`; only a minimal `stable` tier exists.
- Live SSE/WebSocket stay experimental pending deferred browser/load ops gates.
- Human AT sessions (0.21) remain outstanding; CSRF composition (0.22) is **Published**.
- Alpha extras and specialty stubs create over-install foot-guns.

D-038 forbids using a version number as an arbitrary freeze terminus. This RFC attaches
maturity work to **capability phases and evidence**, not a marketing date.

## Proposed design

### North star

Treat “production-level quality” as **adopter trust for the Supported surface**. Explicitly:

| Is | Is not |
|---|---|
| Expand compatibility-protected contracts for Supported CRUD/HTMX/jobs | Promote every Alpha extra to Supported |
| Close or honestly re-home Deferred ops rows | Market experimental live transports as production defaults |
| Human AT + CSRF composition evidence | Commercial SLA or WCAG/VPAT product claims |
| Production archetype + landmine quarantine | SPA/React or Streamlit widget parity |

Vocabulary remains: Supported ≠ API `stable` ≠ commercial warranty
([how to read](../getting-started/how-to-read.md)).

### Priority stack (normative ownership)

| Priority | Move | Owner |
|---|---|---|
| P0 | Finish 0.21 human AT sessions + remediate | D-052 / ROADMAP §0.21 |
| P0 | Ship 0.22 CSRF / SecurityPolicy composition | D-051 / ROADMAP §0.22 (**Published** `v0.22.0`; gates Verified) |
| P1 | Expand `stable` tier for Supported CRUD/HTMX/jobs core | ROADMAP §0.23 / D-053 (**Published** `v0.23.0`; gates Verified) |
| P1 | Live transports: prove ops gates **or** formally polling-only for production docs | ROADMAP §0.24 / D-053 (**Published** `v0.24.0`; disposition `polling_only`) |
| P2 | Reference-app production archetype + load budgets; extras quarantine; charts path | ROADMAP §0.25 / D-053 (**Published** `v0.25.0`; gates Verified) |
| P3 | External security review + SBOM/evidence on every train tag | Process (RELEASE + diligence) |
| P3 | Optional written `1.0` DoD **without a date** | D-053 appendix; does not schedule a phase |

### Optional `1.0` definition of done (no calendar)

A future major may be declared only when **all** hold (still no ship date):

1. `stable` tier covers the Supported CRUD/admin happy path catalogued for §0.23.
2. Human AT gates for 0.21 are Verified and Published.
3. Live transports are either Supported with closed browser/load evidence **or** formally
   documented as non-production with polling as the only Supported production story.
4. Compatibility, migration, and release-gate honesty remain in force (RFC-0029 / D-038).

Declaring this DoD does **not** create a roadmap phase named `1.0` and does not freeze
unrelated experimental work.

### Non-goals

- Chasing SPA/React parity or Streamlit widget completeness as a maturity path.
- Marketing experimental live transports or Alpha extras as production defaults.
- Inventing a commercial SLA claim without support staffing.
- Claiming WCAG certification from Playwright/axe or one AT packet.
- Expanding surface area faster than evidence (preserve release-gate culture).

## Compatibility impact

Additive roadmap/decision/docs only until each owning phase implements promotions or
disposition changes. API `stable` promotions in 0.23 follow the existing deprecation and
intervening-minor rules in [COMPATIBILITY.md](../COMPATIBILITY.md) and STABILITY.md.

## Evidence and acceptance

- Program acceptance: D-053 recorded; this RFC Accepted; public guide published.
- Per-phase acceptance: zero Deferred among each phase’s owned gate rows at that phase’s cut
  (`release-gate-0.21.toml` … `release-gate-0.25.toml`).
- Adopter maturity claims continue to live only on [What’s ready](../guides/whats-ready.md).

## Open questions

None for program acceptance.

**0.23 Published (`v0.23.0`):** locked narrow CRUD/admin promotion allowlist in
ROADMAP §0.23 + [STABLE_FACADE.md](../api/STABLE_FACADE.md); gates Verified via
`check_stable_tier_023.py` / `check_stable_facade.py` / `check_stability_inventory.py` /
`ci_checks.sh test` / `verify_pkg_23.py` (see `release-gate-0.23.toml`).

**0.24 Published (`v0.24.0`):** Accepted disposition **`polling_only`** in
ROADMAP §0.24 + [LIVE_DISPOSITION.md](../api/LIVE_DISPOSITION.md); prior Deferred live-ops
IDs superseded via waive ledgers; gates Verified via
`check_live_disposition_024.py` / `check_browser_024.py` /
`check_perf_024.py` / `check_docs_024.py` / `ci_checks.sh test` / `verify_pkg_24.py`
(see `release-gate-0.24.toml`).

**0.25 Published (`v0.25.0`):** locked Verified criteria + distinct gate
commands in ROADMAP §0.25 + [PRODUCTION_ARCHETYPE.md](../api/PRODUCTION_ARCHETYPE.md);
extras XOR twin [`extras-quarantine-025.toml`](../acceptance/extras-quarantine-025.toml)
(`quarantine` Accepted); checkers
`check_archetype_025.py` / `check_budget_025.py` / `check_extras_025.py` /
`check_charts_025.py` / `check_supply_025.py` / `ci_checks.sh test` / `verify_pkg_25.py`
(see `release-gate-0.25.toml`). Gates Verified — archetype is the documented production
deploy pattern; human AT sessions remain Planned / not Supported.
