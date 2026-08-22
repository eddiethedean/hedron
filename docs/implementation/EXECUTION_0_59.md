# Phase 0.59 execution plan

**Target:** `v0.59.0`  
**Baseline:** in-tree `v0.58.1`; public upgrade source `v0.58.0`  
**Authority:** D-106 / D-107 / RFC-0087 / [`modern-css-contract-059.toml`](../acceptance/modern-css-contract-059.toml)  
**Implementation detail:** [`MODERN_CSS_059.md`](MODERN_CSS_059.md)  
**Release evidence:** [`release-gate-0.59.toml`](../acceptance/release-gate-0.59.toml)

This is the working sequence for implementing the entire phase. A milestone is complete only when
its code, tests, fallback behavior, documentation, and named gate evidence land together. The phase
does not enter release hardening while a Required capability is merely parsed, visually plausible,
or green in one browser.

## Operating rules

1. Keep one styling authority: `hedron-core` owns tokens, markers, CSS compilation, cascade, and
   generated assets. Host adapters consume the shared output and do not fork it.
2. Work from the 0.58.1 compatibility corpus. Every behavior change gets a before/after fixture,
   a feature-off path, and a rollback path before its default is changed.
3. Land changes in vertical slices. A slice includes implementation, focused unit tests, browser
   tests where applicable, security checks, docs, and its release-gate command.
4. Keep new behavior opt-in until its compatibility evidence is complete. Do not use a hidden
   feature flag to bypass a failed contract; amend the contract or re-home the capability.
5. Do not bump package versions, regenerate the public default asset, close external issues, or
   claim 0.59 readiness until the cut milestone explicitly authorizes it.
6. Preserve the hard boundaries: no runtime CSS compilation, client style injection, mandatory
   Node consumer build, remote font convenience, private-selector ABI, visual DOM reorder, or
   styling-owned behavior/state.

## Entry lock: Stage 1 starts here

Stage 0 is contract-refined. Before implementation branches are opened, complete and retain these
artifacts:

- [x] File the Hedron umbrella and three workstream mirrors named in the contract, backlinking
  consumer issues #4–#7 without replacing their source acceptance criteria.
- [x] Capture the reproducible browser set: Playwright `1.62.0`, Chromium revision `1234`, Firefox
  revision `1538`, and WebKit revision `2336`.
- [x] Add the parser corpus probe covering quoted imports, nested functional selectors, authored
  layers, animation shorthands, URLs, strings/comments, unknown at-rules, malformed input, and
  source locations.
- [x] Add the browser capability probe that records feature-on/feature-off behavior for every
  Required and Progressive inventory row.
- [x] Add the explicit-set recipe probe. If field/layout/scope defaults cannot prove explicitness,
  remove them from Required scope through an amendment before implementing them.
- [x] Record the 0.58.1 baseline: full test result, CSS raw/gzip bytes, request count, compiler cold
  time, representative style/layout measurements, wheel inventory, and browser artifacts.
- [x] Set `stage_1_entry_satisfied = true` only after the above artifacts and backlinks exist.

The `CONTRACT-059` command validates the lock and entry packet. It does not mark the runtime ready.

## Milestones and dependencies

| ID | Milestone | Depends on | Primary outputs | Gates closed or advanced |
|---|---|---|---|---|
| E0 | Entry, baselines, and probes | D-107 | probe corpus, issue mirrors, 0.58.1 evidence bundle | `CONTRACT-059` |
| E1 | Compiler v2 | E0 | grammar-aware compiler, v2 manifest/source map, v1 reader, fuzz corpus | `COMPILER-059`, `SECURITY-059`, `COMPAT-059` |
| E2 | Cascade and asset foundation | E1 | modular source manifest, deterministic default CSS, selector/token inventory | `CASCADE-059`, `PERF-059` |
| E3 | Theme, color, and typography | E1, E2 | canonical tokens, aliases, variants, palette-v2, typography assets/roles | `TOKENS-059`, `COLOR-059`, `TYPE-059` |
| E4 | Responsive layout and media | E2, E3 | query boundaries, intrinsic/logical layout, subgrid fallback, print/media matrix | `CONTAINER-059`, `LAYOUT-059`, `MEDIA-059`, `A11Y-059` |
| E5 | Overlay and motion | E1, E2, E4 | placement contract, static fallbacks, reduced-motion and transition enhancements | `OVERLAY-059`, `MOTION-059` |
| E6 | Consumer vertical slices | E3, E4, E5 | controls, AppShell, workflow presentation, Data Mover migration fixtures | `CONTROL-059`, `CHROME-059`, `WORKFLOW-059`, `CONSUMER-059` |
| E7 | Authoring and inspection | E1–E6 as required | explain/check/preview/diff/eject, Explorer provenance, migration tooling | `DX-059`, advances `COMPAT-059` |
| E8 | Fleet conformance | E2–E7 | package dispositions, zero-CSS gallery, visual and accessibility corpus | `VISUAL-059`, `A11Y-059`, `REGRESS-059` |
| E9 | Release hardening and cut | E0–E8 | security/performance/package evidence, upgrade rehearsal, release metadata | `SECURITY-059`, `PERF-059`, `PKG-059`, all gates |

The critical path is `E0 → E1 → E2 → E4 → E6 → E8 → E9`. E3 can begin after E1 and parallelize
with late E2. E5 can prototype against E1/E2 while E4 is completing. E7 starts with compiler
provenance but cannot graduate tooling until the underlying token, layer, fallback, and budget facts
are available.

## E0 — Entry, baselines, and probes

**Owners:** `hedron-core`, `hedron-conformance`, repository maintainers  
**Exit:** the entry lock is reproducible and no design question remains open.

Implementation order:

1. Add `check_contract_059.py` to validate D-107, all machine locks, gate IDs, package ownership,
   browser revisions, and the no-runtime-change rule.
2. Add a versioned compiler corpus under the conformance fixtures. Store source, expected symbols,
   expected diagnostics, output digest, and compatibility disposition; never store secrets or
   absolute paths.
3. Add parser and browser capability probes. A probe records engine, revision, feature, input,
   result, fallback result, and artifact digest.
4. Add the explicit-set and scoped-default feasibility fixture. Its failure result must include the
   destination phase/amendment, not a silent downgrade.
5. Record baseline metrics and attach them to `PERF-059` evidence without changing its Planned
   state.

## E1 — Grammar-aware scoped compiler

**Owners:** `hedron-core` CSS/compiler maintainers  
**Exit:** `COMPILER-059`, `SECURITY-059`, and compiler-related `COMPAT-059` evidence pass.

Implement in this order:

1. Extend the in-tree tokenizer/AST with source spans while preserving comments, strings, escapes,
   URLs, declaration values, and unknown safe syntax.
2. Classify selector, declaration, descriptor, function, custom-property, keyframe, import, and
   at-rule contexts before discovering symbols.
3. Rewrite classes only in selector grammar, including nesting and `:is()`, `:where()`, `:not()`,
   and `:has()`. Preserve `:global(...)` semantics.
4. Rewrite keyframe and other accepted custom identifiers only in their grammar positions; parse
   animation shorthand instead of replacing whitespace-delimited words.
5. Resolve bounded local imports and validate every URL-bearing token. Reject remote imports,
   traversal, symlinks, unsafe schemes, cycles, and budget exhaustion with source-located errors.
6. Normalize compiler-owned layers versus authored sublayers and preserve legal charset/import/layer
   ordering.
7. Emit deterministic v2 CSS, manifest, source map, capability report, and redacted diagnostics;
   read v1 manifests and preserve v1 hashes by default.
8. Fuzz malformed CSS, recursion, imports, escapes, URL schemes, custom identifiers, and manifest
   input. Keep the historical regression seeds permanently.

## E2 — Cascade and default asset foundation

**Owners:** `hedron-core` CSS/assets maintainers  
**Exit:** one deterministic default asset passes cascade, ABI, and budget checks.

- Split source by explicit manifest into `reset`, `tokens`, `base`, `components`, `utilities`, and
  `overrides` layers.
- Generate one default stylesheet and digest; do not hand-edit generated CSS.
- Audit every public class, `data-hedron-*` marker, custom property, part, and package consumer.
- Collapse authored copies of the owning layer and make sublayer order independent of filesystem
  order.
- Establish the selector-specificity ceiling and use `:where()` only where zero specificity is
  intended.
- Deduplicate responsive selector matrices without changing 0.58 viewport semantics.
- Verify `default_styles=False`, strict-CSP external delivery, asset request count, and application
  override authority.

## E3 — Tokens, themes, color, and typography

**Owners:** `hedron-core` theme/design-system maintainers; `hedron-conformance` for evidence  
**Exit:** semantic output is compatible, explainable, and tested across modes and engines.

- Select and document the canonical semantic namespace; emit every public 0.58 alias through 0.59.
- Emit `Theme.variants` only through an explicit finite marker and reject unknown variants.
- Parse the locked absolute color inputs, normalize deterministically, emit tested sRGB fallbacks,
  and record gamut/contrast/focus adjustments in `hedron.brand-palette/2`.
- Add only the `@property`, `light-dark()`, and wide-gamut enhancements that pass their fallback
  probes; fallbacks remain authoritative.
- Define finite typography roles for wrapping, hyphenation, code, numeric content, variable/local
  fonts, metrics fallbacks, and international text.
- Validate local font licensing, asset roots, preload policy, CSP, and no remote fetches.

## E4 — Responsive layout and media

**Owners:** `hedron-core` built-ins; `hedron-conformance` browser/accessibility fixtures  
**Exit:** container and media gates pass with feature-on and feature-off equivalence.

- Add opt-in `inline-size` query boundaries and named thresholds to the existing `Container`; retain
  viewport defaults and existing responsive maps.
- Add container context to selected built-ins without introducing a second responsive authority.
- Implement intrinsic sizing, dynamic viewport units, safe-area handling, aspect ratio, logical
  properties, RTL, mixed direction, and selected vertical-writing behavior.
- Use subgrid only as a Progressive enhancement over ordinary Grid/FormGrid tracks.
- Add real print rules and test shell, links, forms, tables, statuses, workflow, disclosures, and
  page breaks.
- Test 320 CSS px, 200% zoom, text spacing, long/unbroken/international content, no script,
  fragment replacement, focus visibility, and complete-content access.

## E5 — Overlays and motion

**Owners:** `hedron-core` interaction/presentation maintainers  
**Exit:** native semantics and final state are identical with enhancements on or off.

- Keep dialog/popover/top-layer behavior and keyboard/focus semantics canonical.
- Add finite logical placement and collision strategies; enhance with anchor positioning only when
  the capability probe passes.
- Add starting-style, discrete-transition, and view-transition polish behind feature detection.
- Make reduced motion resolve to immediate stable states and preserve title/history/focus/HTMX/server
  state.
- Keep scroll-driven animation Experimental, decorative, opt-in, and disconnected from task state.

## E6 — Consumer vertical slices

**Owners:** `hedron-core` built-ins plus consumer migration owner  
**Exit:** each source issue has a Hedron fixture, browser evidence, and a validated migration diff.

### Controls — source issues #4 and #5

- Implement the shared `attrs` seam with global, ARIA, data, approved HTMX, and dialog-trigger
  allowlists.
- Reject event handlers, inline style, unsafe URLs, malformed ARIA, and non-allowlisted HTMX.
- Align Button/LinkButton size, width, line-height, padding, icons, focus, disabled, and responsive
  markers; forward attributes to the native element.
- Remove the Data Mover workaround selectors and prove forms, methods, targets, swaps, and dialog
  behavior remain unchanged.

### AppShell — source issue #6

- Compose typed brand, account action/form, footer, banner, navigation, and auth-state slots.
- Preserve landmarks, CSRF, routes, accessible names, document order, and complete content.
- Prove authenticated and login/register shell layouts with viewport and container fallbacks.

### Workflow presentation — source issue #7

- Compose provider-neutral source/destination nodes, connectors, explicit operational states, logs,
  statuses, progress, and compact history from existing presentation authorities.
- Ensure every state has non-color cues and a static/reduced-motion representation.
- Keep execution, polling, authorization, provider metadata, and domain transitions in the consumer.

## E7 — Authoring, inspection, and migration

**Owners:** `hedron`, `hedron-core`, Explorer maintainers  
**Exit:** DX evidence proves one understandable built-in-to-CSS learning path.

- Extend explain/check/preview/diff/eject with source spans, layer/specificity, token/alias,
  variant/container, fallback/capability, asset, and budget provenance.
- Add read-only Explorer views; do not execute callbacks or expose application data.
- Implement no-overwrite migration/codemod output with source maps and reviewable diffs.
- Graduate field/layout/scope recipe defaults only if E0 feasibility evidence passes; otherwise
  record the deferral and keep 0.58 behavior.
- Update starter, theming, component-CSS, and advanced examples to the correct authoring level.

## E8 — Fleet conformance and regression

**Owners:** all package owners; conformance and visual QA  
**Exit:** every first-party package has a disposition and the fleet gallery is clean.

- Run the canonical token/marker/layer/style-contract inventory across every package.
- Migrate applicable packages to shared CSS authority; record explicit Not Applicable or
  compatibility-only dispositions where appropriate.
- Expand the zero-application-CSS gallery with controls, shell, layouts, overlays, print, content
  stress, and workflow operations.
- Run the three-engine DOM/computed-style/pixel matrix across themes, directions, zoom, media,
  feature flags, container sizes, and content lengths.
- Retain reviewed visual deltas with DOM facts, computed-style facts, and accessibility confirmation.
- Keep 0.57/0.58 styling issue contracts and both upgrade sources in the regression suite.

## E9 — Release hardening and cut

**Owners:** release maintainers; `hedron-conformance`; package owners  
**Exit:** all 23 gates are Verified, zero are Deferred, and release metadata is truthful.

1. Run security fuzzing and strict-CSP checks; verify redaction and deterministic rebuilds.
2. Run raw/gzip CSS, compiler cold-time, style/layout, request-count, and required-JS budgets.
3. Run the full `ci_checks.sh all --python 3.12 --all-browsers --gate-version 0.59.0 --jobs 1`
   suite and every `check_*_059.py` command.
4. Build clean wheels from a fresh environment, verify exports/licenses/lazy assets, and prove no
   consumer Node dependency.
5. Rehearse upgrades from public `v0.58.0` and in-tree `v0.58.1`, including rollback and
   `default_styles=False`.
6. Refresh live issues, validate the consumer migration, and close source issues only after their
   acceptance criteria and `CONSUMER-059` evidence pass.
7. Update changelogs, compatibility/migration docs, `STATUS`, `ROADMAP`, release metadata, and
   gate states. Bump versions only at this final cut step.

## Evidence and handoff standard

Every gate artifact must include:

- command, commit, Python and Playwright versions, engine/revision, and environment metadata;
- source fixture or corpus identifier and deterministic digest;
- DOM, computed-style, accessibility, network, CSS, and visual facts appropriate to the gate;
- fallback/feature-off result where the capability is Progressive;
- redacted logs and no secrets or absolute local paths; and
- owner, review status, and the exact contract row or issue acceptance criterion covered.

The final handoff is not “tests passed.” It is a release packet containing the 23 Verified rows,
the two-source upgrade report, package/wheel report, budget report, security report, visual gallery,
consumer migration diff, issue audit, rollback instructions, and truthful Required/Progressive/
Experimental/Deferred documentation.

## Stop conditions

Pause the affected lane and return to contract review when:

- a public 0.58 signature, marker, token, DOM order, or default behavior changes unexpectedly;
- a fallback loses semantics, keyboard access, complete content, or state parity;
- a browser-specific result requires user-agent detection or an unbounded workaround;
- a parser rewrite is ambiguous, a URL leaves its registered root, or a manifest cannot be redacted;
- a budget regresses beyond the locked ceiling; or
- a consumer migration requires Hedron to own application behavior, authorization, execution, or
  domain state.

The permitted responses are a compatibility-preserving fix, a documented amendment, or a
re-homing to Progressive/Experimental/Deferred scope. Do not weaken the acceptance contract to
keep the milestone green.
