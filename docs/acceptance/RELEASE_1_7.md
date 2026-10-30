# Hedron `v1.7.0` dirty-form and confirmed-save integration acceptance plan

**Status:** Proposed and unscheduled; every gate Planned
**Authority:** [RFC-0100](../rfcs/RFC-0100-INTERACTION-EFFICIENCY-AND-FORM-CONTINUITY.md) / D-121 proposed planning sequence
**Implementation:** [FORM_SAVE_STATE_1_7](../implementation/FORM_SAVE_STATE_1_7.md)
**Machine packet:** [release-gate-1.7.toml](release-gate-1.7.toml)
**Required release predecessor:** `v1.6.0` (not yet satisfied)

This planning packet does not claim an implementation, checker, runtime behavior, final public API, or calendar commitment. Stage 1 requires FREEZE-170. Exact commands and immutable evidence paths must be selected at that freeze; planned CI-job labels below do not configure or imply existing feature jobs. Preserve phase 1.3's testing scope and the stable application inventory.

## Required reference flow

A settings form is edited, validated, and guarded against accidental navigation. One save fails validation; a second saves revision A while a newer edit B remains dirty. A scripted lost response is reconciled with the server's revision. Explicit reset, canceled confirmation, session expiry, and a write-only credential change all preserve the existing ownership rules.

## Required gates

| Gate | Owner role | Required evidence |
|---|---|---|
| `FREEZE-170` | architecture | Accepted detailed RFC/phase contract; current-source inventory, named maintainers, exact additive APIs and diagnostics, required/deferred scope, host/maturity matrix, schemas, numeric limits, measured baselines, and exact executable commands/artifact paths. |
| `CONTRACT-170` | architecture | Existing HTMX/Alpine/element authorities and canonical handles reused; one transport/presentation owner; no duplicate state runtime; compatible omitted-policy defaults and documented invalid combinations. |
| `REVISION-170` | runtime | Separate dirty/validated/submitted/committed revisions; acknowledge only the submitted revision; newer edits stay dirty; validation, denial, conflict, and stale results cannot clear guards. |
| `GUARD-170` | browser-platform | Existing unsaved guards integrated with native controls, reset and navigation confirmation/focus return; scoped bypass rules; best-effort unload behavior; cleanup and no duplicate listeners. |
| `RECONCILE-170` | application-contract | Lost-response unknown state, authorized read/version reconciliation, no automatic mutation replay, correct application-confirmed Saved outcome, and explicit conflict recovery. |
| `LIFECYCLE-170` | browser-platform | Repeated/nested/OOB replacement, removed targets, stale generations, asset failure, interruption, and teardown; exactly-once initialization/cleanup and zero retained owned resources after removal. |
| `A11Y-170` | accessibility | Keyboard/native fallback, focus and announcement ownership, semantic busy/error states, reduced motion, zoom/reflow, and the declared no-JavaScript flow; no blanket accessibility-conformance claim. |
| `SECURITY-170` | security | Application authorization/persistence remain authoritative. Scope/entity/operation/revision correlation prevents another form, principal, or stale response from clearing state. Never persist credentials or arbitrary unsaved values to localStorage, snapshots, URLs, or traces; reconciliation reads remain authorized and bounded. |
| `PERF-170` | performance | Freeze native-control corpus, maximum scope/field/revision metadata, serialized trace limits, event-processing costs, and repeated-navigation listener budgets before implementation. Measure presentation responsiveness without copying form values. Zero secret values in retained artifacts and zero owned listeners after scope removal are invariant checks. |
| `COMPAT-170` | compatibility | Stable inventory and current-default behavior preserved; explicit FastAPI/Flask/Django/HDJ/Edron/mount dispositions, strict CSP, three-browser evidence, unsupported combinations and Beta migration guidance. |
| `DOCS-170` | docs | Packaged reference flow and examples, policy defaults/limits, failure/recovery, HTTP fallback, privacy, diagnostics, API maturity, and exercised opt-out/rollback instructions. |
| `PKG-170` | packaging | Clean wheel/sdist base/extra installs, optional-import isolation, compatible pins and asset plans, typing, provenance/notices, and package/version evidence for every changed distribution. |
| `RELEASE-170` | release | Every other Required row Verified; immutable artifact-bound evidence, predecessor/support/maturity decisions, migration/rollback, and explicit release approval; no skipped Required row. |

## Adversarial and failure corpus

Edit while saving; save A returns after save B; validation without persistence; committed save with lost response; reset while pending; entity replacement with reused IDs; checkbox/select/repeated fields; write-only secrets; two scopes in one page; browser history; logout/session expiry; canceled leave confirmation.

Use controlled dependencies and actual browser request/lifecycle facts through the existing AppScenario/Playwright facilities and the admitted 1.3 harness. Initial development can use current facilities, but release evidence must meet the frozen protocol and complete host/browser matrix. A screenshot or synthetic pure state test alone cannot satisfy browser behavior.

## Maturity, stop conditions, and rollback

Candidate policy APIs begin as additive Beta. Do not silently change defaults, promote SSE/WebSockets/morphing, bypass route dependencies, introduce response-supplied executable assets, or move application persistence/authorization into browser state. An unsupported host or browser row needs an explicit scope/maturity decision; skipping it cannot verify a Required gate.

Stop implementation or narrow the candidate if authority, native values, stale-result handling, required fallbacks, secret redaction, or resource cleanup cannot be preserved. Numeric limits and performance thresholds must be frozen from recorded baselines before implementation; passing a newly invented post-hoc budget is not acceptance.

Opt out to the existing 1.1 native form/guard and explicit server-confirmed action flow. Do not clear dirty state merely to disable an enhancement; an uncertain dispatched save requires reconciliation or explicit user disposition.

The planning machine packet is intentionally not registered as a releasable phase in executable release tooling. Implementation must add the real checker, artifact/evidence binding, and tooling selection as reviewed work before any cut. Release requires all other Required gates Verified plus an explicit release decision; a planning edit cannot satisfy these conditions.
