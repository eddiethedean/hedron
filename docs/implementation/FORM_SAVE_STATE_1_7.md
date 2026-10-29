# Phase 1.7: dirty-form and confirmed-save integration

**Status:** Proposed and unscheduled; planning only
**Planning revision:** 2026-10-28
**Baseline:** Published `v1.2.0`; rebase against the accepted 1.3 release at scope freeze
**Authority:** [RFC-0100](../rfcs/RFC-0100-INTERACTION-EFFICIENCY-AND-FORM-CONTINUITY.md) / D-121 planning sequence
**Acceptance:** [RELEASE_1_7](../acceptance/RELEASE_1_7.md) · [machine packet](../acceptance/release-gate-1.7.toml)
**Reference research:** [PHP interaction approaches](https://github.com/eddiethedean/hedron/blob/main/research/php-interaction-approaches-2026-10-28.md)

## Outcome

A form can be locally changed, validated by the server, or durably saved; treating those as one condition risks discarded edits and false Saved indicators, especially when the user edits during a pending save or loses the response.

A settings form is edited, validated, and guarded against accidental navigation. One save fails validation; a second saves revision A while a newer edit B remains dirty. A scripted lost response is reconciled with the server's revision. Explicit reset, canceled confirmation, session expiry, and a write-only credential change all preserve the existing ownership rules.

## Existing seams and dependencies

Extend the 1.1 #917/#918 unsaved-guard and validation contracts, `DirtyScope`, native form values, existing save/reset signals, action state, conflict outcomes, navigation/dialog policies, and bounded identity transfer. Freeze explicit uncertain-save behavior as part of this phase. W0 must establish which integration already works before adding behavior.

Phase 1.3 supplies the managed browser evidence protocol. Phase numbers express preferred release order; isolated inventory, design, and prototypes may proceed using current AppScenario/Playwright tests. Release predecessor `v1.6.0` and required contract evidence remain unsatisfied until recorded; a prototype is not release evidence. W0 names actual maintainers and freezes an explicit host matrix, including FastAPI, Flask/Django, HDJ, Edron, mounted paths, and no-JavaScript dispositions where applicable. Unsupported projections must be visible rather than silently skipped.

## Required scope

- Distinguish local dirty revision, validated revision, submitted revision, and application-confirmed committed revision. Server validation/synchronization alone never clears the unsaved indicator.
- Connect native input baselines and opt-in dirty scope flags to existing navigation/action guards, Dialog confirmation/focus return, and explicit reset. Do not duplicate unsaved domain values in Alpine.
- Handle edits made during a pending save: a successful response may acknowledge only the submitted revision; a later edit remains dirty. Reject stale/cross-entity acknowledgments and keep scopes armed after validation, denial, conflict, and failed saves.
- Represent response loss after dispatch as an uncertain save when commit cannot be determined. Reconcile through an authorized read/version check; do not blindly replay a mutation or label it successful or rolled back.
- Expose coherent Unsaved/Saving/Saved/Validation failed/Conflict/Save status unknown presentation through existing lifecycle/surface contracts. Connectivity hints are presentation signals, not proof of server reachability or commit.
- Preserve ordinary HTML form and navigation behavior; document browser-unload warnings as best-effort. Keep secret inputs write-only and account/entity/session changes governed by server reset policy.

## Work packages

### W0 — Freeze revisions and outcomes

Audit shipped 1.1 guards, commit/reset behavior, FormIssue, DirtyScope, ActionState, and application outcome projection. Freeze the revision/acknowledgment state machine, native-control event inventory, guard bypass/reset rules, unknown-save reconciliation contract, and redaction budgets.

### W1 — Integrate dirty state and guards

Connect native controls to bounded dirty metadata and existing guard/dialog mechanisms. Retain action/navigation fallback and exactly one focus/announcement owner.

### W2 — Add confirmed save and reconciliation

Correlate acknowledgments with the submitted scope/entity/revision and server-confirmed application outcome. Preserve newer edits, handle validation/conflict/unknown states, and support an explicit authorized reconciliation read.

### W3 — Prove the settings flow

Exercise controlled save latency, response loss, auth/session changes, secrets, reset, nested forms/scopes, history/back/forward, no-JS, and repeated replacement. Verify browser cleanup and artifact redaction.

## Feature gates

| Gate | Required evidence |
|---|---|
| `REVISION-170` | Separate dirty/validated/submitted/committed revisions; acknowledge only the submitted revision; newer edits stay dirty; validation, denial, conflict, and stale results cannot clear guards. |
| `GUARD-170` | Existing unsaved guards integrated with native controls, reset and navigation confirmation/focus return; scoped bypass rules; best-effort unload behavior; cleanup and no duplicate listeners. |
| `RECONCILE-170` | Lost-response unknown state, authorized read/version reconciliation, no automatic mutation replay, correct application-confirmed Saved outcome, and explicit conflict recovery. |

The [acceptance packet](../acceptance/RELEASE_1_7.md) also requires scope/contract freeze, lifecycle, security, accessibility, performance, compatibility, docs, packaging, and release evidence. Every machine row remains Planned. No `check_170.py` or feature implementation is claimed by this document.

## Failure and resource evidence

Cover: Edit while saving; save A returns after save B; validation without persistence; committed save with lost response; reset while pending; entity replacement with reused IDs; checkbox/select/repeated fields; write-only secrets; two scopes in one page; browser history; logout/session expiry; canceled leave confirmation.

Freeze native-control corpus, maximum scope/field/revision metadata, serialized trace limits, event-processing costs, and repeated-navigation listener budgets before implementation. Measure presentation responsiveness without copying form values. Zero secret values in retained artifacts and zero owned listeners after scope removal are invariant checks.

Application authorization/persistence remain authoritative. Scope/entity/operation/revision correlation prevents another form, principal, or stale response from clearing state. Never persist credentials or arbitrary unsaved values to localStorage, snapshots, URLs, or traces; reconciliation reads remain authorized and bounded.

Exercise Chromium, Firefox, and WebKit for admitted behavior, strict CSP, repeated/nested/OOB replacement, missing assets, and the declared HTTP fallback. Preserve one request executor and one presentation owner under the [HTMX/Alpine boundary](../api/HTMX_ALPINE_BOUNDARY_1_0.md). Candidate public policies are additive Beta until evidence selects a narrower maturity; omitted-policy defaults and existing stable symbols remain compatible.

## Prerelease checkpoints

| Checkpoint | Exit |
|---|---|
| `1.7a0` | Accepted detailed contract; FREEZE-170; exact APIs, matrices, numeric budgets, and executable evidence plan |
| `1.7a1` | Required reference flow, failure/recovery, HTTP fallback, and feature gates demonstrated in Chromium |
| `1.7b1` | Complete declared host/browser corpus, security/a11y/resource hardening, and current-default compatibility |
| `1.7rc1` | Clean package installs, docs, immutable gate evidence, migration/rollback, and all non-release rows Verified |

## Non-goals and rollback

Durable draft storage, offline mutation queues, inferred database commits, automatic mutation replay, generic client/server object synchronization, DOM morph admission, or a second navigation runtime.

Opt out to the existing 1.1 native form/guard and explicit server-confirmed action flow. Do not clear dirty state merely to disable an enhancement; an uncertain dispatched save requires reconciliation or explicit user disposition.

Broader identity/state retention remains with phase 1.11. This phase delivers native form continuity and confirmed-save semantics without admitting general morphing.

Scope changes need a recorded amendment and matching roadmap/acceptance updates. Stage 1 entry is blocked on the detailed freeze, not granted by this planning packet. A release claim requires an explicit accepted release disposition and all Required rows Verified; skipped browser tests are incomplete evidence.
