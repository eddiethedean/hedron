# Hedron `v1.5.0` viewport and on-demand loading acceptance plan

**Status:** Proposed and unscheduled; every gate Planned
**Authority:** [RFC-0100](../rfcs/RFC-0100-INTERACTION-EFFICIENCY-AND-FORM-CONTINUITY.md) / D-121 proposed planning sequence
**Implementation:** [DEFERRED_LOADING_1_5](../implementation/DEFERRED_LOADING_1_5.md)
**Machine packet:** [release-gate-1.5.toml](release-gate-1.5.toml)
**Required release predecessor:** `v1.4.0` (not yet satisfied)

This planning packet does not claim an implementation, checker, runtime behavior, final public API, or calendar commitment. Stage 1 requires FREEZE-150. Exact commands and immutable evidence paths must be selected at that freeze; planned CI-job labels below do not configure or imply existing feature jobs. Preserve phase 1.3's testing scope and the stable application inventory.

## Required reference flow

A dashboard shows its summary immediately and a bounded placeholder for an expensive report. The report performs no query before viewport or explicit activation, loads once, recovers from a scripted failure, and remains accessible through an ordinary report URL without JavaScript.

## Required gates

| Gate | Owner role | Required evidence |
|---|---|---|
| `FREEZE-150` | architecture | Accepted detailed RFC/phase contract; current-source inventory, named maintainers, exact additive APIs and diagnostics, required/deferred scope, host/maturity matrix, schemas, numeric limits, measured baselines, and exact executable commands/artifact paths. |
| `CONTRACT-150` | architecture | Existing HTMX/Alpine/element authorities and canonical handles reused; one transport/presentation owner; no duplicate state runtime; compatible omitted-policy defaults and documented invalid combinations. |
| `INITIATION-150` | browser-platform | Immediate/viewport/user activation, bounded intersection options, one-shot fetch, explicit retry, duplicate suppression, and disposed observers after removal. |
| `PREPARATION-150` | runtime | Zero deferred handler/query/preparation calls before activation; normal dependency/authorization behavior on activation; no fragment-created executable asset. |
| `LIFECYCLE-150` | browser-platform | Repeated/nested/OOB replacement, removed targets, stale generations, asset failure, interruption, and teardown; exactly-once initialization/cleanup and zero retained owned resources after removal. |
| `A11Y-150` | accessibility | Keyboard/native fallback, focus and announcement ownership, semantic busy/error states, reduced motion, zoom/reflow, and the declared no-JavaScript flow; no blanket accessibility-conformance claim. |
| `SECURITY-150` | security | Activation performs the normal authorized view request with bounded parameters and target checks. Do not serialize private report data into placeholders, intersection metadata, or traces; deny stale cross-principal results. |
| `PERF-150` | performance | Measure initial TTFB, LCP, layout shift, query count, request count, total bytes, activation-to-visible completion, and eventual total work. Freeze representative corpora and numeric limits at W0. The deferred report must issue zero queries and requests before eligibility; activation permits one in-flight fetch per identity. Separate reduced work from work shifted later. |
| `COMPAT-150` | compatibility | Stable inventory and current-default behavior preserved; explicit FastAPI/Flask/Django/HDJ/Edron/mount dispositions, strict CSP, three-browser evidence, unsupported combinations and Beta migration guidance. |
| `DOCS-150` | docs | Packaged reference flow and examples, policy defaults/limits, failure/recovery, HTTP fallback, privacy, diagnostics, API maturity, and exercised opt-out/rollback instructions. |
| `PKG-150` | packaging | Clean wheel/sdist base/extra installs, optional-import isolation, compatible pins and asset plans, typing, provenance/notices, and package/version evidence for every changed distribution. |
| `RELEASE-150` | release | Every other Required row Verified; immutable artifact-bound evidence, predecessor/support/maturity decisions, migration/rollback, and explicit release approval; no skipped Required row. |

## Adversarial and failure corpus

Intersection events after removal; simultaneous click and intersection; repeated insertion of the same host; nested scroll containers; failed first load; auth expiry before activation; stale response after navigation; deferred specialist content whose asset was not admitted.

Use controlled dependencies and actual browser request/lifecycle facts through the existing AppScenario/Playwright facilities and the admitted 1.3 harness. Initial development can use current facilities, but release evidence must meet the frozen protocol and complete host/browser matrix. A screenshot or synthetic pure state test alone cannot satisfy browser behavior.

## Maturity, stop conditions, and rollback

Candidate policy APIs begin as additive Beta. Do not silently change defaults, promote SSE/WebSockets/morphing, bypass route dependencies, introduce response-supplied executable assets, or move application persistence/authorization into browser state. An unsupported host or browser row needs an explicit scope/maturity decision; skipping it cannot verify a Required gate.

Stop implementation or narrow the candidate if authority, native values, stale-result handling, required fallbacks, secret redaction, or resource cleanup cannot be preserved. Numeric limits and performance thresholds must be frozen from recorded baselines before implementation; passing a newly invented post-hoc budget is not acceptance.

Omitting the policy restores current immediate Lazy behavior. Ordinary report URLs and page fallbacks work when visibility enhancement is unavailable; cleanup must be verified when switching modes.

The planning machine packet is intentionally not registered as a releasable phase in executable release tooling. Implementation must add the real checker, artifact/evidence binding, and tooling selection as reviewed work before any cut. Release requires all other Required gates Verified plus an explicit release decision; a planning edit cannot satisfy these conditions.
