# Phase 1.6: typed input timing and request policies

**Status:** Proposed and unscheduled; planning only
**Planning revision:** 2026-10-28
**Baseline:** Published `v1.2.0`; rebase against the accepted 1.3 release at scope freeze
**Authority:** [RFC-0100](../rfcs/RFC-0100-INTERACTION-EFFICIENCY-AND-FORM-CONTINUITY.md) / D-121 planning sequence
**Acceptance:** [RELEASE_1_6](../acceptance/RELEASE_1_6.md) · [machine packet](../acceptance/release-gate-1.6.toml)
**Reference research:** [PHP interaction approaches](https://github.com/eddiethedean/hedron/blob/main/research/php-interaction-approaches-2026-10-28.md)

## Outcome

Authors can express debounce and synchronization through HTMX strings, but repeated search/validation patterns are easy to assemble inconsistently and can allow stale responses to replace newer input or results.

A searchable collection sends a single final request after a typing pause, skips too-short queries under the declared policy, ignores an older delayed result, and supports an ordinary GET submission. A separate profile field validates on blur; explicit POST save supersedes obsolete validation without invoking a mutation twice.

## Existing seams and dependencies

Compose `HtmxAttrs.trigger`/`sync`/native validation, canonical `Interaction`, registered action/view handles, typed `Control` metadata, `ActionPolicy`, and operation generations. Inventory current trigger grammar and strict-CSP handling before adding public spellings.

Phase 1.3 supplies the managed browser evidence protocol. Phase numbers express preferred release order; isolated inventory, design, and prototypes may proceed using current AppScenario/Playwright tests. Release predecessor `v1.5.0` and required contract evidence remain unsatisfied until recorded; a prototype is not release evidence. W0 names actual maintainers and freezes an explicit host matrix, including FastAPI, Flask/Django, HDJ, Edron, mounted paths, and no-JavaScript dispositions where applicable. Unsupported projections must be visible rather than silently skipped.

## Required scope

- Provide typed, bounded policies for explicit submission, blur/change validation, debounce/throttle, changed-value filtering, and minimum input length. Exact names and combinations are frozen in W0; do not advertise candidate names as shipped.
- Compile one declaration into existing HTMX transport and lifecycle policy. Keep explicit submission as the default; do not infer a mutation from a validation or search declaration.
- Scope cancellation and latest-result rules per registered operation/target. Prioritize explicit submit over obsolete validation, and suppress stale validation/search responses using operation generations.
- Use native controls as submitted-value owners. Do not create an Alpine copy of form/domain data or reconstruct authoritative HTML from JSON.
- Keep request gating separate from server validation: a bypassed debounce/minimum-length rule must still reach the same validated, authorized endpoint. Support IME composition deliberately rather than firing on incomplete composition.

## Work packages

### W0 — Freeze the typed lowering

Reconcile existing triggers, filters, Hx, Control, Interaction, concurrency, and CSP contracts. Freeze supported events/modifiers, finite timing/input bounds, invalid-combination diagnostics, schema/HDJ projections, and per-host fallback.

### W1 — Deliver request-policy compilation

Add additive policy authoring and lower it to existing HTMX events/attrs. Preserve raw validated Hx/trigger compatibility and do not change omitted-policy defaults.

### W2 — Enforce ordering and control ownership

Integrate current generations and synchronization for latest results and submit/validation precedence. Define clearing a query, threshold crossings, composition, disabled controls, and form reset behavior.

### W3 — Prove search and validation

Use controlled latency to show final-result correctness and measured request counts. Cover ordinary GET/POST, CSRF, invalid input, cancellation races, mounted paths, and repeated target replacement.

## Feature gates

| Gate | Required evidence |
|---|---|
| `LOWERING-160` | Typed bounded policy compilation, supported events/filters/timing, explicit validation versus mutation roles, deterministic invalid-combination diagnostics, and unchanged omitted-policy behavior. |
| `ORDERING-160` | IME-safe request gating, generation-safe latest results, submit superseding obsolete validation, native value preservation, and no duplicate dispatch or mutation. |

The [acceptance packet](../acceptance/RELEASE_1_6.md) also requires scope/contract freeze, lifecycle, security, accessibility, performance, compatibility, docs, packaging, and release evidence. Every machine row remains Planned. No `check_160.py` or feature implementation is claimed by this document.

## Failure and resource evidence

Cover: Type/delete/type across the minimum threshold; an empty query with an old result displayed; IME start/update/end; composition followed by blur/Enter; save during validation; validation finishing after a newer keystroke; two independent search widgets; aborted browser request whose server handler completes.

Freeze timing tolerances, typing traces, input/queue limits, and a baseline before implementation. Assert the expected request count for each trace, including one final debounced request for a continuous eligible burst and the declared empty-query refresh. Track completion latency and retained listeners; do not turn nominal millisecond timers into cross-platform real-time promises.

Filters and timing cannot grant authority or suppress server validation, CSRF, parameter bounds, or target checks. No eval/js: filter strings, parallel fetch path, secret echo, or arbitrary event payload execution.

Exercise Chromium, Firefox, and WebKit for admitted behavior, strict CSP, repeated/nested/OOB replacement, missing assets, and the declared HTTP fallback. Preserve one request executor and one presentation owner under the [HTMX/Alpine boundary](../api/HTMX_ALPINE_BOUNDARY_1_0.md). Candidate public policies are additive Beta until evidence selects a narrower maturity; omitted-policy defaults and existing stable symbols remain compatible.

## Prerelease checkpoints

| Checkpoint | Exit |
|---|---|
| `1.6a0` | Accepted detailed contract; FREEZE-160; exact APIs, matrices, numeric budgets, and executable evidence plan |
| `1.6a1` | Required reference flow, failure/recovery, HTTP fallback, and feature gates demonstrated in Chromium |
| `1.6b1` | Complete declared host/browser corpus, security/a11y/resource hardening, and current-default compatibility |
| `1.6rc1` | Clean package installs, docs, immutable gate evidence, migration/rollback, and all non-release rows Verified |

## Non-goals and rollback

Two-way application-object synchronization, a Livewire-style component snapshot protocol, new browser state stores, client-authoritative validation, automatic per-keystroke saves, or blanket changes to current trigger defaults.

Remove the typed convenience policy and use existing Hx/Interaction declarations or ordinary forms. Validate that old trigger authoring remains compatible throughout 1.x.

The 1.7 save-state phase consumes the operation-generation and validation/submit ordering contract; it does not redefine these rules.

Scope changes need a recorded amendment and matching roadmap/acceptance updates. Stage 1 entry is blocked on the detailed freeze, not granted by this planning packet. A release claim requires an explicit accepted release disposition and all Required rows Verified; skipped browser tests are incomplete evidence.
