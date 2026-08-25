# Phase 0.64 execution plan

**Status:** Planned implementation sequence
**Authority:** [RFC-0091](../rfcs/RFC-0091-HTMX-HEDRON-EXTENSION.md) plus the published 0.61–0.63 contracts
**Implementation detail:** [HTMX_HEDRON_EXTENSION_064](HTMX_HEDRON_EXTENSION_064.md)
**Acceptance:** [RELEASE_0_64](../acceptance/RELEASE_0_64.md)
**Target:** `v0.64.0`

This is the implementation plan for the refined Phase 0.64 scope. The phase has two coordinated
tracks: bounded presentation contracts and an opt-in HTMX lifecycle projection. A work package is
complete only when its implementation, compatibility behavior, tests, documentation, and named
evidence land together.

Issue #86 is not part of this plan; it remains owned by Phase 0.21. The 22 phase-owned
enhancements (18 implemented and closed, 4 open for deferred follow-up) are listed in the
[roadmap inventory](../ROADMAP.md#phase-064-enhancement-inventory).

## Objectives and invariants

0.64 must:

- complete the finite theme and component presentation contracts that remain after 0.63;
- provide a safe style authoring surface for application-defined components without arbitrary CSS;
- expose one registry-derived vocabulary for tokens, parts, states, slots, bundles, and fallbacks;
- deliver the locally served, explicitly declared `htmx-ext-hedron` asset from RFC-0091;
- keep HTMX as request/swap authority and Hedron as server, authorization, mutation, and HTML authority;
- preserve native HTML, ordinary HTMX, and full-page/full-fragment behavior when the extension is absent;
- keep all browser facts bounded, versioned, redacted, deterministic, and inspectable; and
- ship no client store, hydration layer, virtual DOM, response-script execution, or Node requirement.

The following rules apply to every work package:

1. `hedron-core` remains the authority for schemas, resolution, provenance, validation, and public
   metadata. Adapters, Explorer, CLI, browser code, and package projections consume those facts.
2. Every issue receives a machine-readable disposition: Required, Progressive, Experimental, or
   Excluded. No issue is silently deferred because a prototype exists.
3. Every behavior change has a feature-off or fallback fixture, a compatibility note, and a rollback
   path before its default changes.
4. No raw selectors, arbitrary values, URLs, scripts, undocumented aliases, child-DOM coupling, or
   second styling/runtime authority may enter a Required path.
5. Generated CSS, design-token JSON, manifests, bundles, traces, diagnostics, and browser reports
   must be reproducible from the same source facts.
6. A phase claim is not complete from unit tests alone: browser, package, accessibility, security,
   performance, and clean-install evidence must be attached to the named gate.

## Issue work packages

| Package | Issues | Milestones | Result |
|---|---|---|---|
| WP-01 Theme truth and evidence | #680, #681, #682, #686, #687 | E0–E2 | Derived interactive states, standalone conformance, CSS/token export, inspection diagnostics, and one stable parts/state manifest. |
| WP-02 Semantic scales and composition | #677, #678, #683, #690, #692, #697 | E2–E4 | Identity marks, global hooks, typed slots, typography/geometry scales, and named motion with reduced-motion behavior. |
| WP-03 Responsive and inclusive controls | #679, #695, #696, #698 | E3–E5 | Viewport/container conditions, RTL/writing modes, native-control appearance, and forced-colors/high-contrast fallbacks. |
| WP-04 Component verticals and visual evidence | #684, #685, #688, #689, #693, #694 | E2–E6 | Component bundles, parts/state recipes, data/table chrome, visualization presentation, glass surfaces, and portable state-matrix evidence. |
| WP-05 Safe custom-component styling | #699 | E2–E7 | Scoped style DSL with bounded values/tokens, deterministic cascade layers, metadata, rejection corpus, and digest-stable bundles. |
| WP-06 HTMX asset and contract | RFC-0091 | E0–E8 | Explicit extension id, local pinned asset, markers, events, response facts, declaration, CSP/load-order rules, and opt-out behavior. |
| WP-07 HTMX lifecycle and UX | RFC-0091 | E5–E10 | State projection, accessibility presentation, stale/concurrency handling, lifecycle registry, cleanup, and browser traces. |
| WP-08 Fleet, packaging, and release | All Required outcomes | E9–E13 | First-party adoption, package parity, browser/resource evidence, docs, upgrade/rollback, gate packet, and release rehearsal. |

Issue bodies remain normative for detailed acceptance criteria. An issue may span multiple pull
requests, but the final gate packet must link each issue to its implementation, disposition, and
verified evidence.

## Stage 0 entry lock

No implementation milestone begins until the following packet is reviewed and committed:

- [ ] Issue disposition matrix for all 22 issues, with owner, work package, gate, maturity, fallback,
      compatibility impact, and destination if not Required.
- [ ] Canonical inventory of theme tokens, semantic roles, parts, states, slots, component bundles,
      browser hosts, package owners, and existing fallback behavior.
- [ ] Authority decision proving theme resolution, provenance, export, inspection, conformance,
      manifests, bundles, and browser projection consume one resolved representation.
- [ ] 0.63 baseline for output bytes, bundle count, render cost, state-matrix size, diagnostics,
      package identity, browser behavior, and no-extension behavior.
- [ ] Contract locks for theme scales, direction, responsive conditions, native controls, parts/
      states/slots, scoped DSL, extension markers, events, response facts, and registry lifecycle.
- [ ] Security and privacy review covering selectors, values, URLs, response HTML, trace metadata,
      package assets, cache keys, tenant data, and retained registrations.
- [ ] Browser/accessibility matrix covering Chromium, Firefox, WebKit, keyboard/focus, 320/390/1440px,
      zoom/reflow, RTL/bidi, print, forced-colors, high contrast, reduced motion/transparency, and
      JavaScript absent.
- [ ] Budgets for token/manifest growth, CSS/JSON/bundle size, extension overhead, event count,
      retained registrations, analysis time/memory, trace retention, and CI duration.
- [ ] Diagnostic catalog and suppression policy with source provenance and compatibility lifetime.
- [ ] Required machine-readable artifacts from `RELEASE_0_64.md` have owners and schemas; no empty
      placeholder evidence files are created.

Stage 0 is complete only when every open design question has an owner and disposition and the
`CONTRACT-064` entry lock validates the packet.

## Milestones

| ID | Milestone | Depends on | Primary outputs | Gates |
|---|---|---|---|---|
| E0 | Entry lock and baseline | Stage 0 decisions | Issue matrix, authority map, schemas, budgets, browser matrix, 0.63 baseline | `CONTRACT-064` |
| E1 | Theme authority and manifest | E0 | Resolved theme ABI, provenance, derived states, parts/state/slot manifest, package identity rules | `THEME-064`, `MANIFEST-064` |
| E2 | Semantic scales and exports | E1 | Typography, spacing, geometry, identity, global hooks, motion, CSS/token export, deterministic bundles | `TYPOGEOM-064`, `MOTION-064` |
| E3 | Responsive and direction policy | E1–E2 | Viewport/container conditions, RTL/writing modes, nested scopes, print and no-JS behavior | `RESPONSIVE-064` |
| E4 | Native and rich component surfaces | E1–E3 | Controls, data/table chrome, visualization roles, glass fallback, parts/state recipes, state matrix | `CONTROLS-064`, `VISUAL-064` |
| E5 | Safe custom style DSL | E1–E4 | Scoped authoring API, allowlists, cascade layers, source metadata, rejection/adversarial corpus | `CUSTOM-064`, advances `CSP-064` |
| E6 | Extension asset and declaration | E0–E5 | Local asset, digest/license record, page planning, load order, declaration, opt-out byte proof | `ASSET-064`, `CSP-064` |
| E7 | Lifecycle projection | E6 | State markers, operation/generation correlation, terminal outcomes, bounded response facts | `STATE-064`, `RACE-064` |
| E8 | Accessibility and concurrency UX | E7 | Busy/disabled states, announcements, focus, reduced motion, stale/superseded behavior, fallback paths | `A11Y-064`, `MOTION-064`, `RACE-064` |
| E9 | Registry, traces, and integration | E7–E8 | Explicit module registry, teardown rules, Explorer/browser traces, simulator and package metadata | `LIFE-064`, `TRACE-064`, `INTEGRATE-064` |
| E10 | Vertical slices and fleet adoption | E4, E9 | Forms, refreshable views, polling jobs, navigation, charts/maps/grids/elements, reference app | `BROWSER-064`, advances `MANIFEST-064` |
| E11 | Hardening and compatibility | E5, E8–E10 | Security, privacy, accessibility, browser, performance, memory, upgrade, and feature-absent evidence | `SECURITY-064` if added, `PERF-064`, `UPGRADE-064` |
| E12 | Documentation and package rehearsal | E10–E11 | API docs, examples, changelog, clean wheels, package parity, production-like smoke | `DOCS-064`, `PKG-064` |
| E13 | Release decision and handoff | E0–E12 | Final gate report, issue audit, rollback record, release notes, authorized cut packet | All Required gates Verified |

Critical path: `E0 → E1 → E2 → E3/E4 → E5 → E6 → E7 → E8 → E9/E10 → E11 → E12 → E13`.
E2–E4 may run in parallel after the manifest lock; E6 can begin its asset packaging work after E0,
but the extension contract cannot be frozen until the presentation authority and fallback rules are
locked. E11 cannot begin release triage until Required/Progressive dispositions are stable.

## Dependency and implementation rules

- E1 precedes all theme, export, bundle, inspection, visual, and browser work. No consumer may
  reimplement token resolution or derive state independently.
- Parts, states, slots, and bundles must be registry-derived before generated metadata or the
  browser registry claims public identity.
- Viewport and container conditions are presentation-only: they may not change DOM order, focus
  order, routes, authorization, effects, or mutation semantics.
- RTL and writing-mode support uses logical properties and explicit mirroring metadata; it never
  reverses user data or numeric content unexpectedly.
- Native controls retain native semantics and usable fallbacks when custom appearance is unsupported.
- #679 viewport conditions and #695 container conditions remain separate capabilities with shared
  validation and no duplicated responsive authority.
- #693 part/state recipes consume #687 metadata; #699 custom styling consumes the same public
  vocabulary and cannot bypass it with descendant selectors.
- Visualizations, glass, and motion retain solid, semantic, print, forced-colors, reduced-motion,
  and reduced-transparency fallbacks wherever their disposition is Progressive or Experimental.
- The HTMX extension may project server facts but cannot infer authorization or mutation success
  from client attributes, response scripts, or untrusted HTML.
- The lifecycle registry is explicit, selector-scoped, idempotent, teardown-aware, and incapable
  of executing response-provided code.
- Every gate uses exact-limit and one-over-limit tests for declared budgets, malformed-input tests,
  feature-absent tests, and a deterministic repeat run where output is serialized.
- A failed Required gate requires a recorded amendment, owner, compatibility impact, destination,
  and release decision; it cannot be silently relabeled.

## Pull-request sequence

1. **Entry lock:** issue mirrors/dispositions, inventories, authority map, schemas, budgets, and
   `CONTRACT-064` verifier.
2. **Theme truth:** resolver/provenance/derived-state locks, parts/state/slot manifest, and the
   first custom-theme fixture without application CSS.
3. **Semantic surface:** identity, global hooks, typography, spacing, geometry, slots, motion, and
   deterministic CSS/token/bundle exports.
4. **Responsive and controls:** viewport/container conditions, direction policy, native controls,
   data/table chrome, visualization roles, glass fallback, and visual state matrix.
5. **Custom authoring:** scoped DSL, allowlists, layer placement, metadata, digest stability, and
   rejection corpus.
6. **Extension contract:** local asset, declaration, markers, events, response facts, CSP/load order,
   and feature-absent byte proof.
7. **Browser behavior:** state projection, accessibility UX, stale/concurrency behavior, focus,
   navigation, fragment cleanup, and lifecycle registry.
8. **Trace and fleet:** Explorer/browser trace parity, simulator, first-party consumers, package
   metadata, clean install, reference app, and package matrix.
9. **Hardening:** security/privacy corpus, accessibility matrix, browser matrix, performance/memory,
   upgrade/rollback, docs, and release evidence.
10. **Cut:** issue/disposition audit, gate report, release notes, version authorization, and only then
    tag/package/GitHub Release publication.

Each PR names its work package, milestone, issue(s), gates advanced, compatibility effect,
security/accessibility evidence, budget impact, and rollback. Marker-only tests are insufficient for
styling, accessibility, export parity, lifecycle cleanup, or browser fallback claims.

## Verification sequence

The Stage 0 packet freezes exact commands and artifact names. The rehearsal must include:

1. Focused unit, contract, conformance, manifest, export, DSL, trace, lifecycle, and package tests.
2. Repeatability checks for CSS/JSON exports, manifests, bundles, state matrices, traces, diagnostics,
   and generated metadata.
3. Security corpus for unsafe values/selectors/URLs, response scripts, malformed metadata, secrets,
   tenant data, cache/retention boundaries, duplicate registration, and teardown races.
4. Browser matrix across Chromium, Firefox, and WebKit with feature-on/off, no JavaScript, keyboard,
   focus-visible, 320/390/1440px, zoom, RTL/bidi, print, forced-colors, high contrast, reduced
   motion/transparency, stale responses, OOB swaps, history, and fragment removal.
5. Package/host matrix for FastAPI, Flask, Django, `hedron-elements`, charts, maps, Explorer,
   conformance, clean wheels, locally served assets, and no-Node core consumption.
6. Repository checks, once the 0.64 gate artifacts and checker are landed:

   ```text
   UV_CACHE_DIR=/tmp/uv-cache bash scripts/ci_checks.sh test --python 3.12
   UV_CACHE_DIR=/tmp/uv-cache bash scripts/ci_checks.sh quality --python 3.12 --skip-wheels
   UV_CACHE_DIR=/tmp/uv-cache bash scripts/ci_checks.sh docs --python 3.12
   UV_CACHE_DIR=/tmp/uv-cache bash scripts/ci_checks.sh browser --python 3.12
   UV_CACHE_DIR=/tmp/uv-cache bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.64.0
   UV_CACHE_DIR=/tmp/uv-cache uv build --all-packages
   uv run python scripts/check_release_gate.py 0.64.0
   ```

A gate is not Verified by a command that omits its declared artifact, environment, feature-off path,
or repeatability check.

## Stop conditions

Return to Stage 0 if:

- a Required component still needs application CSS, an undocumented alias, or a child selector;
- more than one resolver, registry, manifest, trace, metadata, conformance, or responsive authority
  is proposed;
- a public part/state/slot lacks semantics, accessibility, ownership, or stability rules;
- runtime CSS, exported CSS/JSON, bundles, and metadata disagree;
- responsive conditions alter behavior or authorization rather than presentation;
- the DSL or lifecycle registry can execute arbitrary selectors, values, URLs, or response code;
- the extension becomes required for correctness or the asset-absent path regresses;
- a Progressive/Experimental surface has no documented fallback and evidence boundary;
- any path requires React, Node, npm, JSX, hydration, a persistent client store, or live transport
  for a Supported claim;
- a budget is exceeded without measured amendment and release-owner approval; or
- a Required gate is being waived, downgraded, or closed from narrative alone.

## Release handoff

E13 produces one reviewable packet containing:

- the issue disposition matrix with backlinks and final maturity;
- contract locks, schemas, inventories, compatibility fixtures, and artifact hashes;
- resolved-theme, manifest, export, bundle, state-matrix, DSL, trace, and lifecycle evidence;
- security, privacy, accessibility, browser, performance, retention, and package matrices;
- feature-absent and rollback evidence for both presentation contracts and the HTMX asset;
- reference-app and first-party consumer adoption report;
- clean-wheel/no-Node smoke, upgrade rehearsal, documentation, and release notes; and
- explicit authorization for version metadata, tag, package publication, GitHub Release, and issue
  closure.

Issues close only after the final packet links corresponding Verified evidence. If the phase is not
cut, the handoff records remaining gates, owners, destination, and compatibility impact without
implying public availability.
