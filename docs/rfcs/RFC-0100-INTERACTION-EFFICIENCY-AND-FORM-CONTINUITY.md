# RFC-0100: Interaction efficiency and form continuity

**Status:** Proposed; phase planning only, detailed contract acceptance pending
**Planning revision:** 2026-10-28
**Targets:** Hedron 1.4–1.7; preserve 1.3 first-class UI testing
**Baseline:** Published `v1.2.0` and the stable 1.x interaction inventory; rebase on the accepted 1.3 release at each phase freeze
**Planning decision:** D-121 (Proposed)
**Research:** [PHP interaction approaches](https://github.com/eddiethedean/hedron/blob/main/research/php-interaction-approaches-2026-10-28.md)

## Problem and outcome

Hedron already provides server-rendered components, addressable views, actions, fragment/OOB
updates, local presentation, and operation lifecycle policies. The high-priority opportunities
identified by the PHP interaction research are reducing requests for unseen content and making
input, validation, save, and navigation behavior compose reliably. They extend the existing
architecture rather than require another browser application runtime.

Create four independently reviewable feature phases after the existing 1.3 testing foundation:

| Phase | Required outcome | Implementation | Acceptance |
|---|---|---|---|
| **1.4** | Opt-in visibility-aware polling with bounded recovery | [Visibility polling](../implementation/VISIBILITY_POLLING_1_4.md) | [Plan](../acceptance/RELEASE_1_4.md) · [packet](../acceptance/release-gate-1.4.toml) |
| **1.5** | Viewport/user-activated loading that actually defers expensive work | [Deferred loading](../implementation/DEFERRED_LOADING_1_5.md) | [Plan](../acceptance/RELEASE_1_5.md) · [packet](../acceptance/release-gate-1.5.toml) |
| **1.6** | Typed input/request timing over current HTMX and generation policies | [Input timing](../implementation/INPUT_TIMING_1_6.md) | [Plan](../acceptance/RELEASE_1_6.md) · [packet](../acceptance/release-gate-1.6.toml) |
| **1.7** | Dirty-form, navigation-guard, and confirmed-save revision integration | [Form/save state](../implementation/FORM_SAVE_STATE_1_7.md) | [Plan](../acceptance/RELEASE_1_7.md) · [packet](../acceptance/release-gate-1.7.toml) |

The former 1.4–1.9 themes move to 1.8–1.13 without losing scope: durable workflows, inclusive and
international UX, visualization/media, general state retention, controlled ecosystem expansion,
and measured build scalability. Their existing evidence obligations remain. Numbering expresses
preferred release order; only consumed contracts are design dependencies. Current Playwright
and AppScenario facilities can support early inventories and prototypes while 1.3 is pending.

## Existing contracts remain authoritative

- Use canonical `@app.page`, `@app.view`, `@app.action`, handles, `Interaction`, and outcome lowering.
- Reuse `Poll`, `PollPolicy`, `Lazy`, `InfiniteScroll`, `AsyncRegion`, Hx/trigger/sync, `Control`,
  `ActionPolicy`, operation generations, native controls, `DirtyScope`, and 1.1 guards/save/reset.
- Preserve the [HTMX/Alpine boundary](../api/HTMX_ALPINE_BOUNDARY_1_0.md): server truth and
  authorization; HTMX as the single application request executor; one declared presentation
  owner; the existing lifecycle coordinator for handoff and cleanup.
- Keep ordinary HTTP/native fallbacks, strict CSP, declared targets, initial document asset plans,
  dependency injection, CSRF, principal/tenant checks, and redaction. Deferred fragments cannot
  introduce executable assets that were not admitted by the document plan.
- New policies are opt-in and additive Beta candidates. Omitting them retains current defaults.
  A policy can suppress or delay an enhanced request, but never grant permission, bypass endpoint
  validation, or prove a mutation was canceled on the server.

The 1.1 feature packet already owns unsaved guards and structured validation. Phase 1.7 must
inventory and extend their actual shipped behavior, not rename or reimplement that baseline.
General morphing remains deferred; this proposal does not override `MORPH-048`.

## Phase-specific design decisions to freeze

### 1.4: polling eligibility and recovery

Freeze eligibility states and precedence for hidden tabs, offscreen targets, keep-alive, failure
backoff, authentication expiry, terminal jobs, and removed hosts. Specify at most one in-flight
observation per target and one coalesced refresh on return; never enqueue missed ticks. Bound
jitter, backoff, observer/timer counts, and server-throttle handling. Share lifecycle ownership
instead of adding an independent network scheduler. Keep observation retry separate from mutation
replay. Performance evidence records actual request counts, not merely emitted attributes.

### 1.5: initiation and deferred work

Freeze immediate, viewport, and explicit activation; initial asset demands; stable host/body IDs;
one-shot/retry behavior; intersection bounds; and accessible fallback. The initial page must not
perform deferred report queries or preparation. Do not confuse postponing DOM insertion with
postponing server work. Essential content stays usable, placeholders avoid unnecessary layout
movement, and a specialist whose assets were not admitted uses an explicit fallback.

### 1.6: typed timing and ordering

Freeze allowed events, debounce/throttle bounds, minimum-length and changed-value gates, IME
composition behavior, explicit submission, and cross-field validation/submit precedence. Compile
to existing HTMX/lifecycle machinery without eval or a parallel fetch path. A browser abort cannot
replace generation checking. Define clearing a query and threshold crossings so old results do
not remain misleadingly visible. Native controls remain submitted-value owners.

### 1.7: dirty, validated, submitted, and committed revisions

Freeze the form-scope/entity/operation/revision identity and how an application confirms durable
commit. Validation alone cannot clear dirty state. A successful acknowledgment for submitted
revision A must leave a later edit B dirty. Define explicit reset, canceled navigation confirmation,
secret operations, session expiry, and account/entity changes using existing guard policy.

If a response is lost after dispatch, use an explicit uncertain state when commit cannot be
determined. Reconcile through an authorized read/version check. Never infer successful persistence,
automatic rollback, or safe replay from transport failure. Local presentation retains bounded
flags/revisions, not duplicate unsaved domain objects, credentials, or durable draft storage.

## Ownership and cross-package projections

`hedron-core` owns portable policy/state/identity contracts and shared lifecycle rules. `hedron`
owns FastAPI request integration and authoring projections. Existing browser asset/lifecycle owners
implement visibility, event, and presentation lowering. Flask/Django adapters, HDJ, and Edron
project native contracts without independent scheduling, validation, or save authorities. Optional
elements preserve their own declared DOM boundaries. Applications own persistence, authorization,
business retries, version checks, and the meaning of a committed save.

Each W0 records real maintainers and an explicit host/package/browser matrix. Role labels in draft
packets are planning placeholders, not named maintainers. Missing support receives a visible
disposition and fallback; skipping evidence is not completion. Phase 1.3 remains a testing/tooling
phase with no added production-runtime scope.

## Shared evidence and compatibility

Each phase proceeds through scope freeze, a useful packaged reference flow, hardening, and an
explicit release decision. All new machine rows remain Planned and Stage 1 entry false until the
detailed owning contracts, APIs, schemas, measured budgets, and exact commands/artifacts are
accepted. No feature checker, API spelling, package release, issue closure, or availability claim
is created by this planning change. Register real checkers and artifact binding in release tooling
only during implementation; planning packets must not make a version releasable.

Use controlled latency and actual browser request/lifecycle facts for Chromium, Firefox, and
WebKit. Include strict CSP, declared host/mount projections, no-JavaScript/native fallback,
authentication expiry, stale generations, nested/OOB replacement, repeated removal/reinsertion,
cleanup, secrets, accessibility, current defaults, clean installs, typing, and rollback. Extend the
existing tests and 1.3 harness; do not create a second runner or fake DOM.

Freeze numeric limits before implementation against representative workloads: a long-open polling
dashboard, an expensive deferred report, search/blur-validation traces, and a settings form with
save races. Measure request/query counts, initial and interaction latency, TTFB/LCP/layout shift,
CPU, bytes, preparation, and retained resources where relevant. An optimization may move work
later rather than eliminate it; record both initial and eventual costs. Existing stable behavior
and omitted-policy defaults remain the compatibility baseline.

## Deferred scope

Medium-priority URL-state conveniences, richer upload/preview UX, delayed-spinner authoring,
preparation-cost tooling, batching, broad navigation continuity, and morphing are research inputs,
not implicit Required scope here. Essential focus, busy, error, and fallback behavior still belongs
in each admitted high-priority feature. Durable draft/offline mutation queues, Livewire-style
snapshot synchronization, new stores/virtual DOMs, live-transport promotion, and a required Node
toolchain remain outside this proposal.

## Acceptance

The RFC is accepted in detail only after its open contract questions and each phase's freeze are
resolved. Planning the sequence does not satisfy those freezes. Required scope can change only
through a recorded amendment with matching roadmap, implementation, and packet updates. Keep
published release facts, package versions, support matrices, and current release notes unchanged
until verified implementation and release evidence authorize new claims.
