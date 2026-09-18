# Phase 1.1: open enhancement completion and complementary application features

**Status:** Implemented and Verified in `v1.1.0`
**Baseline:** Stable `v1.0.17`; implemented source `v1.1.0`
**Authority:** [RFC-0098](../rfcs/RFC-0098-OPEN-ENHANCEMENT-COMPLETION.md)
**Acceptance:** [RELEASE_1_1](../acceptance/RELEASE_1_1.md) ·
[release-gate-1.1.toml](../acceptance/release-gate-1.1.toml)

## Required issue inventory

Snapshot: all open issues in `eddiethedean/hedron`, queried 2026-09-18. All 20 are enhancement
requests; #889 and #890 are unlabeled. Each row is required implementation scope, including the
acceptance criteria in its owning issue. Exact API names remain subject to scope freeze.

| Issue | Required enhancement | Work package |
|---|---|---|
| [#889](https://github.com/eddiethedean/hedron/issues/889) | External identity and authorization presentation hooks | W2 |
| [#890](https://github.com/eddiethedean/hedron/issues/890) | Provider-neutral server-side pagination and optional fastapi-pagination adapter | W2 |
| [#891](https://github.com/eddiethedean/hedron/issues/891) | Safe interaction errors delivered to trusted reserved sinks | W1 |
| [#892](https://github.com/eddiethedean/hedron/issues/892) | Application-aware sealed production builds | W1 |
| [#893](https://github.com/eddiethedean/hedron/issues/893) | Request-bound Posit URL and redirect facade | W1 |
| [#913](https://github.com/eddiethedean/hedron/issues/913) | Bounded Dialog class, mark, and presentation hooks | W3 |
| [#914](https://github.com/eddiethedean/hedron/issues/914) | Independent ordinary and raised custom-theme shadow mappings | W3 |
| [#915](https://github.com/eddiethedean/hedron/issues/915) | Executable computed-style assertions in the existing conformance matrix | W1/W5 |
| [#916](https://github.com/eddiethedean/hedron/issues/916) | Write-only keep, replace, and explicit clear secret editing | W3 |
| [#917](https://github.com/eddiethedean/hedron/issues/917) | Opt-in unsaved-form guards in navigation/action lifecycles | W3 |
| [#918](https://github.com/eddiethedean/hedron/issues/918) | Structured validation, linked summaries, and accessible focus recovery | W3 |
| [#919](https://github.com/eddiethedean/hedron/issues/919) | Structured field and shared form-group help | W3 |
| [#939](https://github.com/eddiethedean/hedron/issues/939) | Independent horizontal AppShell header/footer insets | W4 |
| [#940](https://github.com/eddiethedean/hedron/issues/940) | Native ghost/icon-only navigation collapse controls and collapsed footer treatment | W4 |
| [#941](https://github.com/eddiethedean/hedron/issues/941) | Theme-managed Brand name/subtitle typography slots | W4 |
| [#942](https://github.com/eddiethedean/hedron/issues/942) | Plain transparent custom Brand marks | W4 |
| [#943](https://github.com/eddiethedean/hedron/issues/943) | Quiet unboxed ProcessFlow, markers, and media placement | W4 |
| [#944](https://github.com/eddiethedean/hedron/issues/944) | Natural and shared-label-track FormGrid alignment | W3 |
| [#945](https://github.com/eddiethedean/hedron/issues/945) | Typed sticky shell surfaces and measured header-aware navigation offsets | W4 |
| [#946](https://github.com/eddiethedean/hedron/issues/946) | Accessible native icon presentation for color-mode switches | W4 |

## Delivery order and complementary scope

### W0 — Freeze scope and contracts

Reconcile each issue against current source and existing fallbacks. Freeze additive APIs, named
maintainers, package ownership, maturity, dependencies, host/browser matrix, measured budgets, and
the reference corpus. Register complementary tasks with explicit acceptance criteria. Preserve
the stable 1.0 inventory and default rendering. Re-query the backlog before freeze; new issues
require a scope amendment rather than silently expanding the release.

### W1 — Safe response, build, deployment, and conformance foundations

Implement #891–#893 and the initial #915 runner over the existing state matrix and Playwright.
Keep rejection status, approved headers, no-store behavior, and trusted sink restrictions intact.
Define build-safe application registration/factory loading without startup side effects. Fingerprint
the resolved application theme/styles/scripts and verify runtime/build drift. Reuse Posit mount
normalization and trust policy for navigation, form actions, assets, Location, and HX-Redirect.

Required complements: share asset provenance between build/runtime verification and conformance
failures; document one exception-handler integration and one redirect helper composition; exercise
root, proxy-prefix, Workbench, Connect, and inactive Posit modes. Missing browser coverage is
incomplete evidence, never a pass. This bounded runner does not absorb the Phase 1.2 managed harness.

### W2 — Identity-aware, bounded server-backed collections

Implement #889/#890 with display-safe principal context, async presentation decisions, generic
resource references, direct in-process sources, page/offset and cursor support, server-side sorting
and filtering, URL synchronization, and an optional fastapi-pagination adapter. Core does not
import AuthMate, ShuETL, Datdex, or fastapi-pagination.

Required complements: demonstrate permission-aware collection controls with loading, empty, denied,
error, and retry states; reset page/cursor coherently when sort/filter/page size changes; restore
URL state through back/forward; suppress stale page responses and prevent cross-principal cache
reuse. Provider uncertainty fails safely. Authorization and resource scoping precede rows/counts.
Provide deterministic provider overrides and safe Explorer previews using the same public hooks.

### W3 — Complete guided settings and credential editing

Implement #913/#914, #916–#919, and #944 as one guided connection-settings flow. Keep plain string
help/errors and existing Dialog/default elevation behavior compatible. Share stable nested/repeated
field identities between instructions, inline errors, linked summaries, and focus recovery. Render
secret configured state without stored plaintext and validate explicit keep/replace/clear operations.

Required complements: bind secret operation metadata to bounded dirty scopes; share authoritative
save/reset signals with guards; retain safe ordinary values and help disclosure state after errors;
redact secrets from HTML, diagnostics, history, and artifacts. Failed, stale, pending, or unauthorized
saves keep the guard armed. Session expiry follows a server-authoritative bypass. Dialog confirmation
returns focus; natural/shared-label tracks work after validation and responsive/HTMX updates.

### W4 — Coherent native shell, branding, and explanatory presentation

Implement #939–#943 and #945/#946 using shared finite policies, semantic tokens, and existing
controllers. Preserve current defaults. Register Brand typography/mark and shell/toggle/ProcessFlow
parts and states in the existing presentation manifest and component-style delivery paths.

Required complements: coordinate horizontal insets, wrapped branding/utilities/banners, sticky header
measurement, rail offsets, collapse controls, and footer geometry in one shell. Recompute offsets
after fonts, viewport changes, and HTMX updates; clean up observers on replacement. Color-mode icons
follow native/server state while applications retain preference persistence. Plain marks and glass
surfaces document light/dark contrast and forced-colors/print fallbacks. Process markers/connectors
stay aligned when descriptions wrap. Avoid application CSS for the native demonstration.

### W5 — Integrated reference application, hardening, and handoff

Package one representative flow: sign in with display-safe identity, browse an authorized paginated
collection, edit a guided connection with write-only credentials, recover from invalid input, guard
unsaved navigation, save successfully, and use the refined shell/color-mode/process presentation.
Build from the application declarations and run it at root and a trusted deployment prefix.

Extend #915 assertions to the admitted form/chrome/brand surfaces. Measure bounding boxes and
computed properties across Folio light/dark, selected custom themes, narrow/normal/wide widths,
RTL, zoom, forced colors, reduced motion, and native/component stylesheets. Use existing render,
AppScenario, and Playwright tests; cover no-JS fallbacks, denial, redaction, stale responses,
cleanup, optional imports, packaging, compatibility, and rollback. Link issue implementation and
evidence before closure. Hand this corpus to Phase 1.2 testing without moving runtime ownership.

## Completion

All 20 issues and the required complements above must pass the matching acceptance rows. No issue
is considered implemented merely because a prop or marker renders. The phase is not blocked on
the later managed testing, durable-job, general internationalization, ecosystem-promotion, or
incremental-build phases. Broader draft storage, identity administration, client state retention,
and build scalability remain in their existing lanes. Scope changes require a recorded decision
and updates to the roadmap and machine packet.
