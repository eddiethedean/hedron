# Phase 1.5: viewport and on-demand loading

**Status:** Proposed and unscheduled; planning only
**Planning revision:** 2026-10-28
**Baseline:** Published `v1.2.0`; rebase against the accepted 1.3 release at scope freeze
**Authority:** [RFC-0100](../rfcs/RFC-0100-INTERACTION-EFFICIENCY-AND-FORM-CONTINUITY.md) / D-121 planning sequence
**Acceptance:** [RELEASE_1_5](../acceptance/RELEASE_1_5.md) · [machine packet](../acceptance/release-gate-1.5.toml)
**Reference research:** [PHP interaction approaches](https://github.com/eddiethedean/hedron/blob/main/research/php-interaction-approaches-2026-10-28.md)

## Outcome

The current Lazy helper loads immediately after insertion. Expensive reports below the fold can therefore spend server and browser resources before the user needs them.

A dashboard shows its summary immediately and a bounded placeholder for an expensive report. The report performs no query before viewport or explicit activation, loads once, recovers from a scripted failure, and remains accessible through an ordinary report URL without JavaScript.

## Existing seams and dependencies

Extend `Lazy`, `InfiniteScroll`, loading/error templates, registered view handles, `AsyncRegion`, `PrepareContext`, and the immutable document feature/asset plan. Reuse visibility lifecycle facts from 1.4 when shared; do not create an independent observer owner.

Phase 1.3 supplies the managed browser evidence protocol. Phase numbers express preferred release order; isolated inventory, design, and prototypes may proceed using current AppScenario/Playwright tests. Release predecessor `v1.4.0` and required contract evidence remain unsatisfied until recorded; a prototype is not release evidence. W0 names actual maintainers and freezes an explicit host matrix, including FastAPI, Flask/Django, HDJ, Edron, mounted paths, and no-JavaScript dispositions where applicable. Unsupported projections must be visible rather than silently skipped.

## Required scope

- Add explicit immediate, viewport, and user-activated loading initiation. Preserve the existing Lazy load behavior when the new policy is omitted.
- Defer expensive route dependencies and preparation until activation, rather than eagerly querying data and merely hiding its HTML. Do not execute a deferred renderer during initial page composition.
- Use stable authorized host/body identity, bounded viewport margin/threshold settings, one-shot activation, explicit retry after failure, and existing placeholder/error/fallback vocabulary.
- Keep keyboard-accessible ordinary links or forms for user activation and a useful no-JavaScript path. Size placeholders to avoid avoidable layout movement and never defer the only essential page content by default.
- Declare required browser/component assets in the original document plan or navigate through an admitted full-page fallback. A fragment cannot install response-supplied executable assets.

## Work packages

### W0 — Freeze initiation and demand contracts

Inventory Lazy, view handles, prepare(), error slots, initial asset demand, and InfiniteScroll. Freeze activation modes, one-shot/retry/cancel states, stable IDs, fallback requirements, numeric observer/layout budgets, and host/browser dispositions.

### W1 — Deliver deferred work

Lower initiation through existing HTMX and lifecycle ownership. Keep route DI and authorization intact; prove initial composition does not invoke deferred data work. Preserve current immediate mode.

### W2 — Complete recovery and access

Integrate placeholders, localized errors, manual activation/retry, duplicate-activation suppression, removal cleanup, and asset-plan denial/fallback. Cover nested scrollers and keyboard access.

### W3 — Prove the report slice

Count handler/dependency/query calls and browser requests before and after activation. Exercise mounted paths, nested/OOB replacement, script/asset failure, no-JS fallback, and the three-browser corpus.

## Feature gates

| Gate | Required evidence |
|---|---|
| `INITIATION-150` | Immediate/viewport/user activation, bounded intersection options, one-shot fetch, explicit retry, duplicate suppression, and disposed observers after removal. |
| `PREPARATION-150` | Zero deferred handler/query/preparation calls before activation; normal dependency/authorization behavior on activation; no fragment-created executable asset. |

The [acceptance packet](../acceptance/RELEASE_1_5.md) also requires scope/contract freeze, lifecycle, security, accessibility, performance, compatibility, docs, packaging, and release evidence. Every machine row remains Planned. No `check_150.py` or feature implementation is claimed by this document.

## Failure and resource evidence

Cover: Intersection events after removal; simultaneous click and intersection; repeated insertion of the same host; nested scroll containers; failed first load; auth expiry before activation; stale response after navigation; deferred specialist content whose asset was not admitted.

Measure initial TTFB, LCP, layout shift, query count, request count, total bytes, activation-to-visible completion, and eventual total work. Freeze representative corpora and numeric limits at W0. The deferred report must issue zero queries and requests before eligibility; activation permits one in-flight fetch per identity. Separate reduced work from work shifted later.

Activation performs the normal authorized view request with bounded parameters and target checks. Do not serialize private report data into placeholders, intersection metadata, or traces; deny stale cross-principal results.

Exercise Chromium, Firefox, and WebKit for admitted behavior, strict CSP, repeated/nested/OOB replacement, missing assets, and the declared HTTP fallback. Preserve one request executor and one presentation owner under the [HTMX/Alpine boundary](../api/HTMX_ALPINE_BOUNDARY_1_0.md). Candidate public policies are additive Beta until evidence selects a narrower maturity; omitted-policy defaults and existing stable symbols remain compatible.

## Prerelease checkpoints

| Checkpoint | Exit |
|---|---|
| `1.5a0` | Accepted detailed contract; FREEZE-150; exact APIs, matrices, numeric budgets, and executable evidence plan |
| `1.5a1` | Required reference flow, failure/recovery, HTTP fallback, and feature gates demonstrated in Chromium |
| `1.5b1` | Complete declared host/browser corpus, security/a11y/resource hardening, and current-default compatibility |
| `1.5rc1` | Clean package installs, docs, immutable gate evidence, migration/rollback, and all non-release rows Verified |

## Non-goals and rollback

General Python suspension, a new component/region hierarchy, whole-page lazy loading by default, speculative authenticated mutations, dynamic fragment script installation, request batching, or new transport authority.

Omitting the policy restores current immediate Lazy behavior. Ordinary report URLs and page fallbacks work when visibility enhancement is unavailable; cleanup must be verified when switching modes.

Typed timing in 1.6 may reuse the same bounded activation/eligibility facts; 1.8 workflows can lazy-load read-only result views without changing job authority.

Scope changes need a recorded amendment and matching roadmap/acceptance updates. Stage 1 entry is blocked on the detailed freeze, not granted by this planning packet. A release claim requires an explicit accepted release disposition and all Required rows Verified; skipped browser tests are incomplete evidence.
