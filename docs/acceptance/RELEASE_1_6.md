# Hedron `v1.6.0` typed input timing and request policies acceptance plan

**Status:** Proposed and unscheduled; every gate Planned
**Authority:** [RFC-0100](../rfcs/RFC-0100-INTERACTION-EFFICIENCY-AND-FORM-CONTINUITY.md) / D-121 proposed planning sequence
**Implementation:** [INPUT_TIMING_1_6](../implementation/INPUT_TIMING_1_6.md)
**Machine packet:** [release-gate-1.6.toml](release-gate-1.6.toml)
**Required release predecessor:** `v1.5.0` (not yet satisfied)

This planning packet does not claim an implementation, checker, runtime behavior, final public API, or calendar commitment. Stage 1 requires FREEZE-160. Exact commands and immutable evidence paths must be selected at that freeze; planned CI-job labels below do not configure or imply existing feature jobs. Preserve phase 1.3's testing scope and the stable application inventory.

## Required reference flow

A searchable collection sends a single final request after a typing pause, skips too-short queries under the declared policy, ignores an older delayed result, and supports an ordinary GET submission. A separate profile field validates on blur; explicit POST save supersedes obsolete validation without invoking a mutation twice.

## Required gates

| Gate | Owner role | Required evidence |
|---|---|---|
| `FREEZE-160` | architecture | Accepted detailed RFC/phase contract; current-source inventory, named maintainers, exact additive APIs and diagnostics, required/deferred scope, host/maturity matrix, schemas, numeric limits, measured baselines, and exact executable commands/artifact paths. |
| `CONTRACT-160` | architecture | Existing HTMX/Alpine/element authorities and canonical handles reused; one transport/presentation owner; no duplicate state runtime; compatible omitted-policy defaults and documented invalid combinations. |
| `LOWERING-160` | runtime | Typed bounded policy compilation, supported events/filters/timing, explicit validation versus mutation roles, deterministic invalid-combination diagnostics, and unchanged omitted-policy behavior. |
| `ORDERING-160` | browser-platform | IME-safe request gating, generation-safe latest results, submit superseding obsolete validation, native value preservation, and no duplicate dispatch or mutation. |
| `LIFECYCLE-160` | browser-platform | Repeated/nested/OOB replacement, removed targets, stale generations, asset failure, interruption, and teardown; exactly-once initialization/cleanup and zero retained owned resources after removal. |
| `A11Y-160` | accessibility | Keyboard/native fallback, focus and announcement ownership, semantic busy/error states, reduced motion, zoom/reflow, and the declared no-JavaScript flow; no blanket accessibility-conformance claim. |
| `SECURITY-160` | security | Filters and timing cannot grant authority or suppress server validation, CSRF, parameter bounds, or target checks. No eval/js: filter strings, parallel fetch path, secret echo, or arbitrary event payload execution. |
| `PERF-160` | performance | Freeze timing tolerances, typing traces, input/queue limits, and a baseline before implementation. Assert the expected request count for each trace, including one final debounced request for a continuous eligible burst and the declared empty-query refresh. Track completion latency and retained listeners; do not turn nominal millisecond timers into cross-platform real-time promises. |
| `COMPAT-160` | compatibility | Stable inventory and current-default behavior preserved; explicit FastAPI/Flask/Django/HDJ/Edron/mount dispositions, strict CSP, three-browser evidence, unsupported combinations and Beta migration guidance. |
| `DOCS-160` | docs | Packaged reference flow and examples, policy defaults/limits, failure/recovery, HTTP fallback, privacy, diagnostics, API maturity, and exercised opt-out/rollback instructions. |
| `PKG-160` | packaging | Clean wheel/sdist base/extra installs, optional-import isolation, compatible pins and asset plans, typing, provenance/notices, and package/version evidence for every changed distribution. |
| `RELEASE-160` | release | Every other Required row Verified; immutable artifact-bound evidence, predecessor/support/maturity decisions, migration/rollback, and explicit release approval; no skipped Required row. |

## Adversarial and failure corpus

Type/delete/type across the minimum threshold; an empty query with an old result displayed; IME start/update/end; composition followed by blur/Enter; save during validation; validation finishing after a newer keystroke; two independent search widgets; aborted browser request whose server handler completes.

Use controlled dependencies and actual browser request/lifecycle facts through the existing AppScenario/Playwright facilities and the admitted 1.3 harness. Initial development can use current facilities, but release evidence must meet the frozen protocol and complete host/browser matrix. A screenshot or synthetic pure state test alone cannot satisfy browser behavior.

## Maturity, stop conditions, and rollback

Candidate policy APIs begin as additive Beta. Do not silently change defaults, promote SSE/WebSockets/morphing, bypass route dependencies, introduce response-supplied executable assets, or move application persistence/authorization into browser state. An unsupported host or browser row needs an explicit scope/maturity decision; skipping it cannot verify a Required gate.

Stop implementation or narrow the candidate if authority, native values, stale-result handling, required fallbacks, secret redaction, or resource cleanup cannot be preserved. Numeric limits and performance thresholds must be frozen from recorded baselines before implementation; passing a newly invented post-hoc budget is not acceptance.

Remove the typed convenience policy and use existing Hx/Interaction declarations or ordinary forms. Validate that old trigger authoring remains compatible throughout 1.x.

The planning machine packet is intentionally not registered as a releasable phase in executable release tooling. Implementation must add the real checker, artifact/evidence binding, and tooling selection as reviewed work before any cut. Release requires all other Required gates Verified plus an explicit release decision; a planning edit cannot satisfy these conditions.
