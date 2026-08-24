# Phase 0.63 execution plan

**Status:** Implementation baseline landed / release evidence pending
**Authority:** [RFC-0090](../rfcs/RFC-0090-REACTIVE-INTERACTION-PLATFORM.md)
**Implementation detail:** [INTERACTION_TOOLING_063](INTERACTION_TOOLING_063.md)
**Acceptance:** [RELEASE_0_63](../acceptance/RELEASE_0_63.md)
**Target:** `v0.63.0`

This is the implementation sequence for the complete Phase 0.63 scope. A milestone is complete
only when its code, tests, fallback behavior, documentation, and named gate evidence land together.
The Required theme contract is the critical path; Progressive presentation extensions cannot delay
or weaken it.

## Current implementation status

The implementation baseline now includes the shared theme-resolution authority, compatibility
aliases, derived interactive tokens, registry-derived component and element contracts, deterministic
CSS/JSON/report exports, stylesheet inspection, bounded state-matrix output, portable interaction
trace encoding/decoding/profiling, build-manifest provenance, and CLI/Explorer/conformance
integration. Focused tests, the repository documentation and quality checks, and the full external
test suite pass for this baseline.

Release readiness is not claimed by this implementation status. Browser and accessibility matrices,
visual/provider adoption, adversarial package and retention evidence, fleet/reference-app evidence,
and the final E15 release packet remain planned until their named artifacts are produced.

## Operating rules

1. Keep one styling and metadata authority. `hedron-core` owns theme resolution, provenance,
   validation, compatibility aliases, and schemas; adapters, Explorer, CLI, and packages consume
   those facts rather than reimplementing them.
2. Treat the published 0.62 behavior as the compatibility baseline. Every behavior change
   gets a before/after fixture, feature-off or fallback evidence, and a rollback path before its
   default is changed.
3. Land vertical slices. Each slice includes implementation, focused tests, security and
   accessibility evidence where applicable, documentation, and the release gates it advances.
4. Never satisfy a theme issue with application CSS, undocumented `--hedron-default-*` aliases,
   arbitrary selectors, inline-style escape hatches, unstable child-DOM coupling, or a second
   client/runtime authority.
5. Keep inspection, conformance, profiling, and migration tooling non-executing. Tools may report
   uncertainty or unsupported cases; they may not infer correctness from syntax alone.
6. Do not bump versions, regenerate public assets, close GitHub issues, or claim release readiness
   until the cut milestone authorizes the change and the evidence packet is complete.
7. Every Required/Progressive/Experimental disposition is recorded in the machine-readable
   inventory before implementation begins. A passing prototype does not change maturity.

## Entry lock: Stage 0

Before implementation branches open, retain a reproducible entry packet with:

- [ ] Issue mirror for open #676–#689, their acceptance criteria, owning work package, and
  Required/Progressive disposition.
- [ ] Canonical component inventory covering default stylesheet declarations, public tokens,
  variants, accessibility modes, parts, slots, state hooks, fallbacks, and package owners.
- [ ] Theme authority decision: resolution, provenance, compatibility aliases, CSS/JSON export,
  inspection, and conformance all read the same resolved representation.
- [ ] 0.62 baseline for default/custom themes, stylesheet bytes, asset count, representative
  render time, state-matrix cardinality, CLI/Explorer timings, and package identity.
- [ ] Browser and accessibility matrix, including Chromium/Firefox/WebKit, 320/390/1440px,
  zoom/reflow, RTL, print, forced-colors, high-contrast, reduced-motion, and reduced-transparency.
- [ ] Budget lock for token and manifest growth, CSS/JSON/bundle size, matrix cardinality,
  analysis time/memory, trace/profile retention, export size, and CI overhead.
- [ ] Diagnostic catalog and suppression policy, including source provenance and compatibility
  lifetime for `HED-THEME-*`, `HED-CHECK-*`, `HED-PROFILE-*`, `HED-METADATA-*`, and
  `HED-MIGRATE-*` findings.
- [ ] Reference custom-theme fixture that exercises built-ins without application-authored CSS.
- [ ] Explicit decision to omit or retain the Experimental React-island recipe.

Stage 0 is complete only when `CONTRACT-063` can validate the packet and every open design question
has an owner, disposition, and destination. Do not create empty evidence files merely to satisfy
the planned artifact names.

## Milestones

| ID | Milestone | Depends on | Primary outputs | Gates closed or advanced |
|---|---|---|---|---|
| E0 | Entry lock and baselines | Stage 0 decisions | Inventory, issue map, schemas, budgets, baseline report, package/browser matrix | `CONTRACT-063` |
| E1 | Canonical theme resolution | E0 | Public-token consumption, compatibility aliases, provenance, custom-theme fixture | `THEME-063`, advances `SECURITY-063` |
| E2 | Derived states and responsive presentation | E1 | Palette derivation, link/selection hooks, bounded recipe conditions, mode behavior | `PALETTE-063`, `A11Y-063` |
| E3 | Component contract surface | E1 | Typed identity marks, semantic slots, parts/state hooks, registry manifest | `PARTS-063`, `METADATA-063` |
| E4 | Export and style bundles | E1–E3 | CSS/JSON export, base/component bundles, deterministic dependencies, round-trip fixtures | `EXPORT-063`, `BUNDLE-063`, `PKG-063` |
| E5 | Inspection and theme conformance | E1–E4 | Dev inspector, fallback diagnostics, standalone CI check, exceptions, contrast reports | `INSPECT-063`, `THEME-CHECK-063`, `CONFORMANCE-063` |
| E6 | State matrix and visual extensions | E3, E5 | Portable state-matrix command, visualization roles, Progressive surface presets | `MATRIX-063`, `VISUAL-063`, advances `PERF-063` |
| E7 | Portable trace conformance | E0 | Encoder/decoder, golden fixtures, redaction, truncation, unknown-version behavior | `TRACE-063` |
| E8 | Interaction profiler | E7 | Explorer timeline, headless export, timing provenance, filters, bounded retention | `PROFILER-063`, `PROFILE-SAFE-063` |
| E9 | Static analysis and check catalog | E0, E7 | Non-executing analyzers, stable findings, source maps, suppressions, adversarial corpus | `CHECK-063`, `CHECK-SAFE-063` |
| E10 | Explanations and migration | E9, E3 | Source-linked lifecycle explanations, React dispositions, worked native/manual/non-fit cases | `SOURCE-063`, `MIGRATE-063` |
| E11 | Metadata and package identity | E3, E4, E7 | TypeScript/custom-element metadata, wheel/npm identity, maturity/fallback facts | `IDENTITY-063`, advances `METADATA-063` |
| E12 | Interoperability decision | E10 | Omit record or isolated Experimental island with CSP/SSR/cleanup proof | `INTEROP-063` |
| E13 | CI, fleet, and reference adoption | E4–E12 | Package matrix, JSON/SARIF/headless outputs, reference-app journey, docs | `DOCS-063`, `CONFORMANCE-063`, advances `PKG-063` |
| E14 | Adversarial closure | E5–E13 | Security, a11y, limits, browser, multi-worker, malformed-input, and upgrade evidence | `SECURITY-063`, `A11Y-063`, `PERF-063`, `UPGRADE-063` |
| E15 | Release rehearsal and cut | E0–E14 | Final gate report, clean packages, release notes, rollback, version cut authorization | All Required gates Verified |

The critical path is `E0 → E1 → E2/E3 → E4 → E5 → E6 → E13 → E14 → E15`. E7 can begin after
E0 and run in parallel with E1–E6; E8–E10 consume its stable trace. E12 may be completed early,
but no Experimental island can block the Required release.

## Issue work packages

| Package | Issues | Milestones | Implementation result | Evidence |
|---|---|---|---|---|
| WP-01 | [#676](https://github.com/eddiethedean/hedron/issues/676) | E0–E1 | Default component declarations consume canonical public theme values or validated aliases; variants, shape, elevation, focus, and state values reach built-ins. | `THEME-063`, dark custom-theme fixture, stylesheet token audit |
| WP-02 | [#678](https://github.com/eddiethedean/hedron/issues/678), [#679](https://github.com/eddiethedean/hedron/issues/679), [#680](https://github.com/eddiethedean/hedron/issues/680) | E1–E2 | Derived interactive palette, global link/selection hooks, and finite responsive recipe conditions with provenance and safe print/mode behavior. | `PALETTE-063`, contrast/mode/responsive corpus |
| WP-03 | [#677](https://github.com/eddiethedean/hedron/issues/677), [#683](https://github.com/eddiethedean/hedron/issues/683), [#687](https://github.com/eddiethedean/hedron/issues/687) | E1–E3, E11 | Typed marks, semantic slots, stable parts/state hooks, identity semantics, and registry-derived manifest. | `PARTS-063`, `METADATA-063`, generated docs/types |
| WP-04 | [#682](https://github.com/eddiethedean/hedron/issues/682), [#684](https://github.com/eddiethedean/hedron/issues/684) | E3–E4 | Resolved theme exports to CSS/design-token JSON and deterministic base/component bundles without dropping interaction rules. | `EXPORT-063`, `BUNDLE-063`, runtime/export parity |
| WP-05 | [#681](https://github.com/eddiethedean/hedron/issues/681), [#686](https://github.com/eddiethedean/hedron/issues/686) | E4–E5 | Standalone conformance and development inspection expose fallbacks, provenance, variants, parts, modes, contrast, and remediation. | `INSPECT-063`, `THEME-CHECK-063`, production-inertness/security tests |
| WP-06 | [#688](https://github.com/eddiethedean/hedron/issues/688), [#685](https://github.com/eddiethedean/hedron/issues/685), [#689](https://github.com/eddiethedean/hedron/issues/689) | E3–E6 | Provider-neutral state matrix plus accessible visualization roles and bounded Progressive translucent/glass presets. | `MATRIX-063`, `VISUAL-063`, browser/fallback matrix |
| WP-07 | Existing 0.63 tooling scope | E7–E13 | Trace, profiler, static checks, explanations, migration dispositions, metadata projections, and package conformance consume the theme/component facts without a second authority. | `TRACE-063`, `PROFILER-063`, `CHECK-063`, `SOURCE-063`, `MIGRATE-063`, `IDENTITY-063`, `CONFORMANCE-063` |

Issue bodies remain normative for detailed acceptance criteria. A work package may span multiple
pull requests, but no issue closes until its package evidence is linked from the final gate report.

## Dependency rules

- E0 is the only first milestone. No implementation may freeze a private token, selector, manifest,
  diagnostic, or metadata shape before the entry lock.
- E1 must precede any derived palette, component contract, export, bundle, inspector, conformance,
  or state-matrix implementation. All of them consume one resolved theme representation.
- E2 may not introduce arbitrary CSS, unbounded breakpoints, state-dependent behavior, or a second
  responsive authority. Responsive conditions are presentation-only and preserve DOM/focus order.
- E3 must be registry-derived before E4 emits bundles or E11 emits metadata. Handwritten manifests
  are temporary probes only and cannot become release artifacts.
- E4 must prove runtime/CSS/JSON parity before E5 treats fallback diagnostics as authoritative.
- E5 owns conformance logic; Explorer and CLI call it rather than reimplementing coverage or contrast.
- E6 is Progressive where marked. Missing visualization or translucent/glass support must degrade
  to ordinary semantic HTML, solid surfaces, and tabular/non-color fallbacks.
- E7 freezes the trace envelope before profiler, static-check, migration, or browser adapters claim
  cross-tool parity. No consumer may reinterpret 0.61/0.62 identity or outcome fields.
- E8–E10 never execute application callbacks, import private application state, or silently rewrite
  source. Unsupported and uncertain migration cases are explicit output.
- E11 cannot claim Supported metadata when the packaged runtime, maturity, fallback, or component
  ids differ from the registry.
- E13 adopts only the Required package/host matrix. Other hosts receive a documented disposition.
- E14 tests exact-limit, one-over-limit, repeated-operation, multi-worker, and feature-absent paths;
  a green happy-path test is not closure.
- E15 cannot convert a failed Required gate to Progressive or Deferred without a recorded amendment,
  owner, destination, compatibility impact, and release decision.

## Pull-request sequence

1. **Contract lock:** issue mirrors, component inventory, theme authority, dispositions, schemas,
   diagnostics, budgets, browser matrix, and entry verifier.
2. **Resolution foundation:** canonical token consumers, compatibility aliases, provenance, and the
   #676 custom-theme vertical slice.
3. **Semantic state foundation:** #680 derivation, #678 link/selection hooks, and #679 responsive
   conditions with mode/print/forced-colors fixtures.
4. **Public component contract:** #677 identity marks, #683 slots, #687 parts/state hooks, and
   registry projections for Python, TypeScript, docs, and conformance.
5. **Export and packaging:** #682 CSS/JSON export, #684 bundles, deterministic dependency ordering,
   clean-host asset registration, and runtime/export parity.
6. **Evidence tooling:** #686 inspector and #681 conformance, including fallback, contrast,
   intentional-exception, source-coupling, and production-inertness diagnostics.
7. **Visual evidence:** #688 state matrix, then #685 visualization roles and #689 Progressive
   surface presets with provider-neutral browser integration.
8. **Trace:** canonical encoder/decoder and cross-consumer fixtures; no profiler/check consumer
   proceeds on an unstable envelope.
9. **Profiler and checks:** Explorer timeline, headless output, static analyzers, check catalog,
   suppressions, and source-linked explanations.
10. **Interop and metadata:** migration analyzer, omit/Experimental decision, TypeScript metadata,
    package identity, maturity, and fallback projections.
11. **Fleet and hardening:** package/host adoption, reference app, full matrix, security/a11y/perf,
    upgrade, clean-wheel, and rollback evidence.
12. **Release cut:** gate report, issue audit, docs synchronization, release notes, and authorized
    version/tag/package changes.

Each implementation PR names its work package, milestone, issue(s), gates advanced, public
compatibility effect, security/a11y evidence, budget impact, and rollback. Marker-only tests are not
sufficient for styling, layout, color, accessibility, export parity, or browser-fallback claims.

## Verification sequence

The exact commands and artifact hashes are locked by Stage 0. The release rehearsal must include,
at minimum:

1. Focused unit and conformance suites for theme resolution, provenance, parts/slots, exports,
   bundles, diagnostics, trace, profiler, checks, migration, and package identity.
2. Deterministic repeat runs for CSS/JSON exports, state-matrix manifests, diagnostics, traces,
   SARIF/headless output, and generated metadata.
3. Security corpus: unsafe CSS/selectors/URLs, secrets, tenant data, malformed input, cyclic
   metadata, callback execution attempts, path traversal, and cache/retention boundaries.
4. Browser matrix: Chromium/Firefox/WebKit, feature-on/off, no JavaScript, 320/390/1440px, zoom,
   RTL, print, forced-colors, high-contrast, reduced-motion, reduced-transparency, keyboard, and
   focus-visible behavior.
5. Package/host matrix: FastAPI, Flask, Django, Posit, static hosting, `hedron-elements`,
   `hedron-charts`, Explorer, conformance, clean wheels, and no-Node core consumption.
6. Repository checks:

   ```text
   UV_CACHE_DIR=/tmp/uv-cache bash scripts/ci_checks.sh docs --python 3.12
   UV_CACHE_DIR=/tmp/uv-cache bash scripts/ci_checks.sh quality --python 3.12 --skip-wheels
   UV_CACHE_DIR=/tmp/uv-cache bash scripts/ci_checks.sh browser --python 3.12
   ```

   Credentialed and packaging suites are added according to the repository CI workflow. A gate is
   not Verified by a command that omits its declared artifact, environment, or feature-off path.

## Stop conditions

Stop implementation and return to Stage 0 if:

- a default component still needs application CSS or an undocumented alias for a Required theme
  value;
- more than one resolver, registry, manifest, trace, metadata, conformance, or responsive authority
  is proposed;
- a public slot/part/state hook cannot declare semantics, accessibility, ownership, and stability;
- derived values lose provenance, exports drift from runtime CSS, or bundles omit required state;
- responsive conditions can alter behavior, DOM/focus order, routes, effects, or authorization;
- inspection, conformance, profiling, or migration executes callbacks or persists private content;
- a Progressive visualization/glass feature has no solid, semantic, print, forced-colors, or
  reduced-transparency fallback;
- a tool requires React, Node, npm, JSX, hydration, a persistent client store, or live transport
  for a Supported path;
- a budget is exceeded without a measured amendment and release-owner approval; or
- a Required gate is being waived, silently downgraded, or closed from narrative alone.

## Release handoff

E15 produces one reviewable release packet containing:

- gate status with commands, environments, artifact hashes, and issue backlinks;
- resolved-theme, component-manifest, export, bundle, state-matrix, trace, metadata, and migration
  schemas plus compatibility fixtures;
- custom-theme stylesheet audit and before/after baseline report;
- security, privacy, accessibility, browser, performance, retention, and package matrices;
- Progressive disposition records for #684, #685, and #689 and the React-island omit/Experimental
  decision;
- reference-app and first-party package adoption report;
- upgrade and rollback rehearsal, clean-wheel/no-Node smoke, and release notes; and
- explicit authorization for version metadata, tag, package publication, and GitHub issue closure.

Issues close only after the final packet links the corresponding Verified evidence. If the phase is
not cut, the handoff records the exact remaining gates, owners, destination phase, and compatibility
impact; it does not imply availability from implementation progress alone.
