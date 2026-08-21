# Hedron `v0.59` progressive styling authoring acceptance

**Status:** Conditionally Stage 0 Refined; Stage 1 blocked  
**Required predecessor:** Published and Verified in-tree `v0.58.0` (not yet satisfied)  
**Planning baseline:** Published/Verified in-tree `v0.57.0` plus D-101/D-102 0.58 contracts  
**Target:** Hedron `v0.59.0`  
**Decision/RFC:** D-103 / D-104 / [RFC-0086](../rfcs/RFC-0086-PROGRESSIVE-STYLING-AUTHORING.md)  
**Implementation plan:** [PROGRESSIVE_STYLING_059](../implementation/PROGRESSIVE_STYLING_059.md)  
**Tracking:** [styling-tracking-059.toml](styling-tracking-059.toml)

D-104 freezes exact public signatures, schemas, diagnostics, budgets, local workstream ownership,
starter adoption, and evidence commands against shipped `v0.57.0` plus D-102's frozen 0.58
contracts. Because runtime `v0.58.0` does not exist, Stage 1 is blocked until its Published/Verified
cut and a recorded no-drift predecessor audit (or accepted D-104 amendment). The refine creates no
runtime API or release claim.

## Outcome

A beginner can choose a built-in look or create a coherent, accessible light/dark application
design from a small trusted brand input; reuse named semantic style recipes; apply explicit local
scope defaults; inspect, preview, diff, and check the lowering; and eject one decision or the whole
design to current `Theme`, appearance-prop, and scoped-CSS APIs.

The result uses the existing theme registry, appearance markers, component contracts, CSS compiler,
asset build, cascade, and CSP policy. Existing explicit styling remains first-class.

## Planned gate matrix

| Gate | State | Required proof |
|---|---|---|
| `CONTRACT-059` | Planned | Exact symbols, schemas, vocabulary, precedence, diagnostics, maturity, dispositions |
| `LOWER-059` | Planned | Design→Theme/props/markers/build differential; no second styling runtime |
| `BRAND-059` | Planned | Deterministic coordinated light/dark compilation, failure/remediation, provenance |
| `THEME-059` | Planned | Typed groups, Theme bridge, registration, inheritance, existing-theme compatibility |
| `RECIPE-059` | Planned | Family compatibility, inheritance, explicit precedence, no wrapper/JS/runtime lookup |
| `SCOPE-059` | Planned | Explicit boundaries, nesting, semantic/DOM-order safety, fragment behavior |
| `TOOLING-059` | Planned | One static redacted manifest for explain/preview/diff/check |
| `EJECT-059` | Planned | Whole/partial public-API output, source-map parity, path/overwrite safety |
| `A11Y-059` | Planned | Contrast/focus/non-color/motion/zoom/text/media/RTL/keyboard/SR evidence |
| `CSP-059` | Planned | External deterministic CSS, hostile inputs, asset/egress policy, no inline requirement |
| `VISUAL-059` | Planned | Three-engine locked gallery, computed facts, controlled visual deltas |
| `ADAPTER-059` | Planned | Honest core/FastAPI/Flask/Django/Jinja/elements/sim/conformance dispositions |
| `REGRESS-059` | Planned | Existing Theme/appearance/scoped-CSS/build and 0.53–0.58 compatibility |
| `DX-059` | Planned | Beginner tasks, complete styling-starter migration, inspect-to-eject learning evidence |
| `PKG-059` | Planned | Clean wheels, exports, optional isolation, docs, upgrades, metadata, rehearsal |

`release-gate-0.59.toml` owns the exact commands and owners. Stage 1 may mark a row Verified only
when its executable or immutable evidence exists. The cut allows zero Deferred rows.

## Conditional refine and predecessor checklist

- [x] D-103 and RFC-0086 assign 0.59 scope.
- [x] Current `Theme`, appearance props/markers, style contracts, scoped CSS, compiler, build, and
      policy remain authoritative.
- [x] The beginner ladder is built-in → brand → recipe → scope → inspect → eject → primitive.
- [x] One styling authority and deterministic lowering are explicit invariants.
- [x] Starter-example migration is normative rather than advisory.
- [x] Fifteen planned gates and W0–W11 are named.
- [x] Planning adds no runtime symbol, package version, registry claim, or release status.
- [ ] Published/Verified in-tree `v0.58.0` satisfies the Stage 1 predecessor prerequisite.
- [x] D-104 accepts an early conditional refine against v0.57.0 plus D-102 contracts.
- [ ] Complete `styling-predecessor-audit-059.toml` against final 0.58 style roles, explanation,
      overrides, ejection, scaffolds, security, and host dispositions before Stage 1.
- [ ] Amend D-104 if that predecessor audit finds material drift.

## Stage 0 checklist

- [x] Freeze the public root type/name, construction path, `Hedron` integration, modules, maturity,
      and exports.
- [x] Freeze brand inputs, coordinated light/dark algorithm contract, adjustment/remediation, and
      supported color formats.
- [x] Freeze finite typed design groups and exact Theme import/export/registration behavior.
- [x] Freeze recipe application spelling, families, compatible components, inheritance, and 0.58
      semantic surface roles.
- [x] Freeze scope boundary implementation, HTML semantics, nesting, and fragment behavior.
- [x] Freeze explicit-prop/recipe/scope/design/theme/base precedence and equal-level conflicts.
- [x] Freeze versioned plan, provenance, diff, and ejection source-map schemas.
- [x] Freeze CLI/Explorer explain, preview, diff, check, and eject behavior from one shared service.
- [x] Freeze diagnostics and reject-not-slice numeric budgets.
- [x] Freeze core/FastAPI/Flask/Django/Jinja/elements/sim/conformance and ecosystem dispositions.
- [x] Freeze accessibility, CSP/security, visual-browser, performance, and upgrade corpora.
- [x] Freeze every starter/beginner/quick-start/golden-path/minimal/first-app/theming/scaffold
      documentation entry and the highest applicable 0.59 abstraction.
- [x] Create all `*-059.toml` contract/tracking artifacts and `upgrade-fixtures-059.md`.
- [x] Create exact `release-gate-0.59.toml` commands and ownership.
- [x] Confirm Stage 0 changes contracts only: no runtime API or version bump.

## Stage 1 delivery checklist

- [ ] W1: portable design plan, provenance, manifest bridge, lowering, explanation, and diff.
- [ ] W2: deterministic brand compiler with coordinated accessible light/dark semantic palettes.
- [ ] W3: typed design groups and lossless bridge to/from existing `Theme`.
- [ ] W4: immutable named family-scoped recipes lowered to existing props/markers.
- [ ] W5: explicit bounded style scopes and machine-checked precedence.
- [ ] W6: shared CLI/Explorer explain, preview, diff, and check.
- [ ] W7: local overrides and safe whole/group/recipe/scope/component ejection.
- [ ] W8: 0.58 semantic surface roles and honest ecosystem/adapter consumption.
- [ ] W9: all styling starter migrations and progressive learning path.
- [ ] W10: accessibility, CSP/security, visual/browser, performance, regression, and upgrade evidence.
- [ ] W11: exports, clean wheels, optional isolation, metadata, and release rehearsal.
- [ ] All fifteen gates Verified with zero Deferred.

## Required representative evidence

- Built-in `default` and `aurora` applications with no 0.59 runtime/asset delta.
- A one-accent branded application with coordinated light/dark palettes and provenance.
- Boundary seed colors that adjust or fail with stable diagnostics and useful remediation.
- Typed geometry, density, typography, elevation, motion, and navigation choices lowered to an
  ordinary `Theme`.
- One control recipe and one surface/data recipe, each compared with equivalent explicit props.
- A compact data scope nested in a comfortable application with one explicit child override.
- Existing custom `Theme` imported as a design base with equivalent emitted output.
- Shared CLI and Explorer explain/preview/diff/check over the same static manifest.
- Whole-design, one-group, one-recipe, one-scope, and one-component-style ejections with parity.
- A 0.58 minimal app, CRUD workspace, dashboard, task, auth, and upload surface inheriting semantic
  roles without behavior/security changes.
- A third-party component with a complete public style contract and one honest unsupported case.
- Strict-CSP/no-inline, hostile configuration, remote font/asset refusal, private-selector, and
  ejection path adversarial corpora.
- Chromium, Firefox, WebKit, native/no-JS, HTMX fragments, keyboard, screen-reader semantics,
  forced colors, reduced motion, print, RTL, 200% zoom, text spacing, long content, and narrow
  viewport evidence.
- A mixed-level application using a branded design, one recipe, explicit component props, and
  owned scoped CSS together.

## Starter documentation acceptance

At cut time, every maintained example identified as starter, beginner, quick start, golden path,
minimal, first app, theming tutorial, or generated scaffold uses the highest applicable 0.59
styling abstraction. This includes 0.58 scaffold output.

The default teaching sequence is:

1. built-in theme or one-step branded design;
2. named recipe for repeated intent;
3. explain and preview;
4. local scope/override;
5. partial ejection;
6. resolved `Theme`, appearance props, tokens, style contracts, scoped CSS, and cascade internals.

Primitive-first documents are allowed only when their purpose is explicitly Theme/tokens/
appearance/style-contract/scoped-CSS/compiler internals and they are labeled Advanced, Explicit,
Lower-level, or Under the hood. Historical release notes and upgrade fixtures remain historically
accurate.

## Cut checklist

- [ ] Every gate in `release-gate-0.59.toml` is Verified with zero Deferred.
- [ ] Train packages and workspace bump to `0.59.0` only after all gates Verify.
- [ ] New APIs are documented Beta; existing stability classifications change only through a
      separate accepted promotion.
- [ ] Root/API/guides/examples/scaffolds teach the new styling abstractions in the locked order.
- [ ] Every inventoried styling starter uses the highest applicable 0.59 abstraction.
- [ ] Explicit `Theme`, appearance props, tokens, scoped CSS, and compiler documentation remains
      complete and is clearly positioned as the advanced/lowered path.
- [ ] Clean wheels install and run every branded/recipe example and migrated 0.58 scaffold.
- [ ] No import, asset, CSS, or browser-runtime cost appears when 0.59 APIs are unused.
- [ ] Default/aurora and final 0.58 compatibility fixtures retain expected output.
- [ ] Release docs, changelogs, STATUS, ROADMAP, compatibility, metadata, and registry truth agree.
- [ ] Tag/PyPI action follows separate release authorization; this plan does not publish.

## Automatic cut blockers

- Any high-level abstraction owns a second theme registry, cascade, CSS compiler, asset pipeline,
  renderer, browser runtime, or component semantics.
- Brand compilation emits a locked measurable pair below target, silently mixes unrelated light/
  dark branding, or silently changes a requested value without provenance.
- A recipe accepts arbitrary CSS declarations/selectors/URLs, applies to an incompatible family,
  adds wrapper DOM/JS, or defeats explicit component props.
- A scope is ambient/invisible, changes DOM/tab/reading order, creates invalid semantics, or relies
  on lifecycle JavaScript after fragment replacement.
- Styling changes route exposure, authorization, mutation meaning, content/state semantics, upload
  enforcement, task behavior, or accessible names.
- Request/user/database data can become CSS, tokens, selectors, class identifiers, URLs, or font
  sources.
- Supported behavior requires inline styles, `unsafe-inline`, implicit network access, private
  selectors, or remote assets outside existing explicit policy.
- Explain/preview/diff/eject invokes application callbacks, loads application data, leaks secrets,
  or includes unstable absolute paths/object representations.
- Ejection escapes the project root, follows an unsafe symlink, overwrites by default, targets
  private markup, or fails generated parity.
- A host/package is labeled Supported without native authority and required evidence.
- Any maintained styling starter teaches raw token maps, repeated appearance bundles, or scoped CSS
  first when an applicable 0.59 abstraction exists.
- Any `*-059` gate remains Planned, Deferred, waived without an accepted destination, or lacks its
  exact evidence.
