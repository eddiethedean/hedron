# Phase 0.65 full implementation execution plan

Status: **Complete**. This document records the implementation sequence and release-readiness
evidence for Phase 0.65.

Authority: [RFC-0092](../rfcs/RFC-0092-INTEGRATED-STYLING-PLATFORM.md),
[APPLICATION_STYLING_065](APPLICATION_STYLING_065.md), the
[refined scope](../acceptance/application-styling-scope-065.md), and
[RELEASE_0_65](../acceptance/RELEASE_0_65.md).

Target: `v0.65.0`, after the published/in-tree `v0.64.1` predecessor audit.

## Implementation objective

Deliver one inspectable styling path from application registration through build, render, browser
fallback, diagnostics, and ejection:

```text
app.styles(...) → registry → build manifest → CSS/compiler/cascade → page or fragment
                                      ↘ diagnostics / explain / inspect / eject / diff
```

The implementation extends the existing asset graph, CSS compiler, theme graph, component registry,
manifest formats, and `hedron style` CLI. It does not create a second stylesheet registry, CSS
language, cascade/compiler, client runtime, or behavior authority.

## Readiness conditions (satisfied for the Required cut)

The completed implementation records all of the following:

- D-110 is accepted and implemented with the exact signature, schemas, precedence, safety policy, and Required /
  Progressive boundary from the [refined scope](../acceptance/application-styling-scope-065.md).
- The `v0.64.1` build, unit, browser, docs, and package checks are green.
- Issue bodies for #690, #693, #694, and #698 are mapped into the issue-to-gate matrix with
  one owner and one reviewer per issue.
- Fallback checks establish support and behavior for native controls, forced colors,
  reduced motion, print, responsive overflow, and RTL before public names are frozen.
- Baseline measurements and bounded checks exist for the feature-off reference app: manifest bytes, CSS bytes,
  request count, cold compile time, diagnostics time, hook count, and layout-shift scenarios.
- The scope checklist, upgrade fixtures, and Progressive inventory have owners.

If a probe fails, amend D-110 and the machine-readable contract. Do not weaken a gate or silently
move a failing Required slice into Progressive.

## Repository seam map

| Authority | Existing seam | Phase 0.65 extension |
|---|---|---|
| App registration | `packages/hedron/src/hedron/app/hedron.py` | Add `Hedron.styles(...)`, pre-seal registration, app state, and late-registration rejection |
| Asset graph | `packages/hedron-core/src/hedron_core/application_assets.py`, `registry/asset.py`, `registry/builder.py` | Add application-style metadata while preserving local-only, dependency-ordered, CSP-safe asset emission |
| Page/fragment emission | `packages/hedron-core/src/hedron_core/page_assets.py`, `head_support.py` | Emit one fingerprinted stylesheet on PAGE, deduplicate HTMX/head/fragment paths, never emit response `<style>` tags |
| Build | `packages/hedron/src/hedron/build/compile.py`, `build/manifest.py`, `hedron_core/manifests.py` | Compile registered application CSS, write the versioned style manifest, source map, provenance, and asset entries |
| CSS compiler | `packages/hedron-core/src/hedron_core/css/` and `compile_css` | Add application-layer wrapping, scope/selector policy, safe global opt-in, source mapping, and reject-not-slice errors |
| Existing presentation | `packages/hedron-core/src/hedron_core/presentation_064.py`, `style_bundles.py`, `static/hedron-default.css` | Reuse the 0.64 vocabulary and add the six motion, data-view, control, and hook contracts |
| Theme graph | `theme.py`, `theme_platform.py`, `theme_contract.py` | Bridge namespaced application tokens through `Theme`/`ThemeSpec`/`ThemePatch` with provenance and collisions |
| Component metadata | `registry/component.py`, `discovery.py`, `builtins/register.py` | Inventory and emit the five stable #693 component/part/state surfaces |
| Built-ins | `builtins/shell.py`, `process_flow.py`, `surfaces.py`, `forms.py`, `layout.py`, `controls.py` | Add public markers and bounded recipes without changing semantic/state ownership |
| CLI | `packages/hedron/src/hedron/cli/parser.py`, `cli/commands/style.py`, `cli/commands/theme.py` | Add application-CSS registration inspection, explain, check, diff, eject, and update-check modes while retaining 0.60 commands |
| Evidence | `docs/acceptance/release-gate-0.65.toml`, `scripts/check_release_gate.py` | Implement `scripts/check_065.py`, gate-specific fixtures, retained reports, and CI wiring |

## Contract decisions to implement

### Application registration

The implemented API on `Hedron` and the app-facing protocol is:

```text
app.styles(
    name: str,
    source: str | Path,
    *,
    scope: str | None = None,
    layer: Literal["application", "overrides"] = "application",
    global_: bool = False,
    media: tuple[str, ...] = (),
) -> StyleSheetSpec
```

The implementation must:

1. resolve `source` relative to the application/package root;
2. reject missing files, symlink escapes, remote/import URLs, duplicate names, invalid media,
   private response styles, unsafe at-rules, and unowned package paths;
3. register a deterministic logical id, source digest, package/distribution owner, scope, layer,
   media, CSP disposition, and provenance in the existing registry;
4. emit a stable `data-hedron-style-scope` root when `scope` is supplied;
5. require `global_=True` for global selectors and retain that decision in the manifest; and
6. fail closed after registry/catalog/OpenAPI sealing, matching existing registration behavior.

Use an additive `ApplicationStyleManifest` with schema `hedron.application-styles/1`. Add it to the
build manifest with a new build-manifest format while retaining a reader for the `v0.64.1` format
that produces an empty application-style section. Existing asset and CSS-symbol readers remain
compatible.

### Cascade and selectors

Every generated stylesheet begins with the single order:

```css
@layer reset, tokens, base, components, application, utilities, overrides;
```

Application CSS is compiled into `application`; explicit per-instance utilities and overrides stay
stronger. Scoped application selectors are constrained to the registered root. Hedron component
selectors must use manifest-backed `data-hedron-*` hooks; application-owned selectors are allowed
only inside the explicit application scope. Private generated classes, user-data selector values,
remote imports, unsafe at-rules, and behavior-changing declarations reject with deterministic
diagnostics.

### Tokens and provenance

The wire token name is `namespace/name`. The adapter validates the namespace, maps it into the
existing theme token graph, and emits a safe CSS variable. Each token record carries type, default,
modes, fallback, source, owner, and provenance. Core-token collisions reject; application tokens do
not mutate the core registry or create a second theme registry.

### Public hooks

The first manifest-backed inventory is finite:

- `AppShell.nav.link`: default, hover, current, disabled;
- `ProcessFlow.step`: current, complete, blocked, skipped;
- `Card`: heading, supporting copy, metadata;
- `FormField`: control, focus, invalid, disabled;
- `SplitView`: separator and responsive collapse.

Add a shared marker helper, then update only these surfaces. Keep classes and unlisted descendant
DOM shapes private. Hook values are finite, escaped, deterministic, and stable across a patch
release; state remains owned by the component/server.

## Work packages

Each work package is a reviewable pull request or a deliberately split series. The listed files are
the expected first touch points; implementation may add focused modules and tests beside them.

| ID | Work package | Primary files | Depends on | Gate / owner |
|---|---|---|---|---|
| W0 | Contract freeze and probes | acceptance packet, `scripts/check_065.py`, new probe fixtures | — | `CONTRACT-065`, core-styling |
| W1 | Style registration model | new `hedron_core/application_styles.py`, registry asset/builder, `Hedron` | W0 | `ASSET-065`, assets |
| W2 | Build and manifest integration | `manifests.py`, `build/compile.py`, `build/manifest.py`, CSS compiler | W1 | `ASSET-065`, `CSS-065`, compiler |
| W3 | Public hook manifest | marker helper, `presentation_064.py`, five built-ins, component registry | W0 | `HOOKS-065`, components |
| W4 | Application token bridge | `theme.py`, `theme_platform.py`, `theme_contract.py` | W0 | `TOKEN-065`, theme |
| W5 | Cascade, scope, and selector policy | `css/`, `presentation_064.py`, `style_bundles.py`, static CSS | W1–W4 | `LAYER-065`, `CSS-065`, core-styling |
| W6 | Diagnostics and CLI | `cli/parser.py`, `cli/commands/style.py`, new diagnostic helpers/codes | W1–W5 | `INSPECT-065`, tooling |
| W7 | Safe ejection and update | new ejection service, CLI, manifest/source-map readers | W5–W6 | `EJECT-065`, tooling |
| W8 | Motion vertical | `presentation_064.py`, theme tokens, `static/hedron-default.css` | W3–W5 | `MOTION-065`, presentation |
| W9 | Parts/state recipes | five built-ins, hook/recipe manifest | W3–W5 | `HOOKS-065`, `RECIPE-065`, components |
| W10 | Data-view/table chrome | data/table built-ins, theme tokens, static CSS | W4–W5 | `DATA-065`, data |
| W11 | Native controls | `builtins/controls.py`, `forms.py`, static CSS and browser fixtures | W4–W5 | `CONTROLS-065`, components |
| W12 | Touched-surface fallback matrix | browser/a11y/print/RTL/no-JS fixtures | W8–W11 | `A11Y-065`, `PRESENT-065`, a11y |
| W13 | Fleet migration | reference app, starters, package examples, adapters, docs | W1–W12 | `FLEET-065`, fleet |
| W14 | Hardening and upgrade | security, budgets, browser matrix, upgrade fixtures, CI | W7–W13 | `SECURITY-065`, `PERF-065`, `UPGRADE-065`, release |
| W15 | Documentation and release | API/guides/migration, gate reports, changelog/version workflow | W14 | `DOCS-065`, `PKG-065`, release |

### W0 — contract, probes, and executable gates

- Create `scripts/check_065.py` with one deterministic subcommand per gate; it must support
  `--gate`, `--verify`, `--allow-planned`, and machine-readable output.
- Add schema/packet shape checks for the refined scope, contract, inventory, budgets, and upgrade
  fixture. Verify every gate id has an owner, command, issue/scope mapping, and artifact location.
- Add browser probes before API freeze for native control appearance, `forced-colors`, reduced
  motion, print, responsive overflow, RTL logical properties, and no-JS rendering.
- Record baseline reports in the CI evidence bundle; never commit generated build output.

Exit: D-110 and the scope checklist are accepted, all gate commands resolve to existing scripts or
tests, and the baseline report is reproducible.

### W1–W2 — registration, build, and asset delivery

- Introduce the immutable style registration/spec type and use the existing registry builder,
  snapshot/restore, asset ordering, head admission, CSP policy, and local path checks.
- Extend build compilation to collect registered app styles after component CSS, preserve source
  locations, rewrite/fingerprint local referenced assets, and write application-style entries.
- Preserve page, fragment, HTMX, head-support, default-styles-off, and no-JS behavior. A fragment
  may reference an already registered stylesheet but may not inject a new response style tag.
- Make repeated build output byte-identical and make asset registration idempotence/conflicts
  explicit.

Exit: ASSET/LAYER/CSS fixtures prove local ownership, one request, deduplication, CSP/no-JS,
fragment safety, deterministic fingerprinting, and reject-not-slice behavior.

### W3–W5 — hooks, tokens, cascade, and ordinary CSS

- Generate the hook manifest from the component registry plus the explicit five-surface inventory;
  do not infer public selectors from arbitrary DOM or class names.
- Add marker data to the five required surfaces and test that caller `data` cannot overwrite
  Hedron-owned hook values.
- Add namespaced token registration to the existing Theme/ThemeSpec/ThemePatch path. Validate
  aliases, modes, fallbacks, provenance, and core collisions before CSS emission.
- Extend the CSS AST/compiler with layer normalization, scope prefixing, public-hook validation,
  app-local selector validation, source positions, and fail-closed diagnostics.
- Update all generated default/component bundles to declare the `application` layer without
  changing output when no application stylesheet is registered.

Exit: feature-off output is unchanged, feature-on CSS has the exact layer order, public hook and
token manifests round-trip, unsafe/private selectors reject, and application CSS cannot alter
behavior, semantics, routes, authorization, or interaction state ownership.

### W6–W7 — diagnostics, explain, inspect, and ejection

Extend the existing `hedron style` command family without breaking theme/design-system commands:

```text
hedron style explain <surface> [--property <name>] [--manifest <path>]
hedron style inspect <manifest-or-source> [--format human|json]
hedron style check --custom-css [--project <path>]
hedron style eject <surface> --output <path>
hedron style diff <ejected-path> [--manifest <path>]
hedron style update --check [--manifest <path>]
```

Diagnostics must identify code, severity, source, selector/hook, property, layer, token,
fallback, remediation, and manifest/source digest. Output is sorted, redacted, and stable.

Ejection writes only inside the project root, retains generated-block markers and source-map /
manifest provenance, refuses accidental overwrite, detects drift, and emits manual merge guidance.
The registered application source remains the source of truth; ejection never changes it.

Exit: explain identifies the winning declaration deterministically; inspect/check reject every
unsafe fixture; ejection round-trips; diff detects source and upstream drift; update-check never
silently overwrites a manual edit.

### W8–W11 — required issue verticals

Implement each vertical behind its own gate and issue-linked test file:

| Gate | Required implementation | Minimum evidence |
|---|---|---|
| `MOTION-065` / #690 | `instant`, `standard`, `emphasized`, `reveal`, `elevate`, `crossfade`; bounded duration/easing/distance/opacity; busy/progress clarity | deterministic CSS, reduced-motion, print, keyboard, and budget matrix |
| `RECIPE-065` / #693 | finite properties for AppShell nav links, ProcessFlow steps, Card roles, FormField states, SplitView separator/collapse | hook manifest, state ownership, responsive, forced-colors, print, and stability fixtures |
| `DATA-065` / #694 | table border/radius, header, row separator/hover/selected, numeric/code, sticky header surface/elevation, compact/spacious density | semantic state, overflow, sticky, print, forced-colors/high-contrast, TableColumn composition |
| `CONTROLS-065` / #698 | native-first checkbox/radio, select, range, file, date/time, number; accent/appearance and all required states | Chromium/Firefox/WebKit platform matrix, keyboard/touch, forced-colors, validation fallback |

Use existing semantic markup and server state. Do not introduce a generic input selector contract,
custom paint where the platform cannot support it, or motion that owns layout/state.

### W12 — touched-surface fallback matrix

For every surface changed by W8–W11, retain evidence for:

- keyboard order, `:focus-visible`, invalid, disabled, busy, and screen-reader-visible state;
- forced-colors/high contrast and reduced transparency;
- reduced motion and print;
- responsive overflow, touch target, and RTL/logical properties where applicable;
- full-page, fragment, no-JS, and semantic fallback behavior.

Broader navigation/overlay, container/density, product-wide typography/media/icon, visualization /
export, and full preference expansion remain Progressive with an owner and fallback in the
inventory. They do not block 0.65 unless a Required surface adopts one.

### W13 — migration order

Migrate consumers only after manifest and asset fingerprints are stable:

1. reference app: register one local stylesheet and replace private selectors with hooks;
2. flagship/starter examples: demonstrate semantic props → theme → app CSS → eject;
3. built-in component packages: add the five public surfaces and issue verticals;
4. adapters (FastAPI, Flask, Django, Jinja): verify asset URL, head, fragment, CSP, and no-JS parity;
5. docs and examples: remove unsupported private-selector guidance and label Progressive surfaces;
6. package build: verify CSS, manifests, source maps, and local assets are present in wheel/sdist.

Every migration has a feature-off golden and a feature-on golden. No issue is closed until its
implementation, public contract, tests, and retained release evidence link to the issue.

### W14–W15 — hardening and release handoff

- Run adversarial CSS tests: remote imports, unsafe at-rules, inline/response styles, user-data
  selectors, symlink escapes, token collisions, duplicate registration, stale manifests, drift,
  and budget overruns.
- Measure three cold repetitions against the `v0.64.1` feature-off reference app and compare the
  maximum to the frozen budgets. Exceeding a budget fails the slice; it never drops CSS.
- Run the complete unit, browser, docs, adapter, package, and upgrade matrix. Retain reports in the
  release evidence bundle named by gate and commit.
- Update API docs, migration guide, examples, changelog, support dispositions, package metadata,
  and release gate states only after runtime evidence is complete.
- Cut `v0.65.0` from the verified commit, publish, install the clean artifacts, rerun the published
  quick-start and application-CSS fixture, then create the GitHub release.

## Test and evidence inventory

Create or extend these focused suites; each gate command should call the smallest relevant subset
before the full CI matrix:

| Area | Planned test/evidence location |
|---|---|
| registration and manifest | `tests/unit/test_application_styling_065.py`, `tests/unit/test_release_manifest.py` |
| build/asset/fragment/CSP | `tests/unit/test_theme_assets_build.py`, `tests/unit/test_asset_053.py`, new application asset fixtures |
| hooks and recipes | `tests/unit/test_public_style_hooks_065.py`, `tests/unit/test_phase064_presentation.py` |
| tokens and cascade | `tests/unit/test_application_style_tokens_065.py`, `tests/unit/test_css.py` |
| diagnostics and CLI | `tests/unit/test_application_style_diagnostics_065.py`, CLI command tests |
| ejection and drift | `tests/unit/test_application_style_ejection_065.py`, upgrade fixtures |
| issue verticals | `tests/unit/test_issue_690_motion_065.py`, `test_issue_693_recipes_065.py`, `test_issue_694_data_view_065.py`, `test_issue_698_controls_065.py` |
| browser/a11y/print | `tests/browser/test_application_styling_065.py`, `tests/browser/test_application_styling_a11y_065.py` |
| fleet/adapters | `tests/integration/test_application_styling_fleet_065.py` and adapter-specific suites |
| release commands | `scripts/check_065.py`, `tests/ops/test_release_gate_evidence.py` |

The exact filenames may be consolidated when an existing suite is the canonical owner; the gate
manifest must still point to stable commands and artifact paths.

## Pull-request sequence and merge rules

1. **Contract PR:** W0, schemas, probes, gate runner, and no runtime symbols beyond data models.
2. **Foundation PR:** W1–W2 registration, build, manifest, asset, and layer behavior.
3. **Public styling PR:** W3–W5 hooks, tokens, selector policy, compiler, and feature-off parity.
4. **Tooling PR:** W6–W7 diagnostics, source maps, ejection, drift, and CLI compatibility.
5. **Issue PRs:** W8, W9, W10, and W11 independently, each with its gate and issue evidence.
6. **Fallback PR:** W12 browser/accessibility/print/RTL/no-JS matrices and Progressive dispositions.
7. **Migration PR:** W13 reference app, starters, packages, adapters, and docs examples.
8. **Release PR:** W14–W15 hardening, package/version/changelog changes, verified evidence, and gate state.

Each PR includes RFC/decision links, gate ids, test commands, artifact paths, compatibility impact,
and rollback notes. CI must run feature-off regression tests on every foundation and vertical PR.

## Rollout and rollback

Roll out in this order:

1. land dormant manifest/schema readers and feature-off tests;
2. enable registration only for the reference app;
3. enable one scoped stylesheet and inspect its emitted manifest/CSS;
4. enable public hooks and the four verticals one gate at a time;
5. migrate fleet consumers after each browser and adapter matrix is green;
6. enable release-version and publish workflow only after all gates are Verified.

Rollback is a clean feature-off build using `default_styles`/existing asset settings and the
previous build manifest. If a generated artifact or hook changes unexpectedly, remove the app
registration, restore the prior build directory atomically, retain the failed evidence, and amend
the contract before retrying. Do not delete user ejected CSS; mark it as manually orphaned and
provide the source-manifest hash needed for recovery.

## Definition of done

Phase 0.65 is fully implemented only when:

- all Required foundation, issue, fallback, security, performance, fleet, upgrade, regression,
  documentation, and package gates are Verified with retained artifacts;
- the four issue slices are linked to their exact implementation and evidence;
- feature-off `v0.64.1` output remains compatible and the upgrade fixture passes;
- no private selector, silent CSS omission, unsafe asset, unowned token, response style tag, or
  behavior-changing CSS path remains;
- ejection/diff/update, diagnostics, and published clean-install quick-start checks pass; and
- every broader styling omission is explicitly Progressive/Deferred with a fallback and no implied
  Supported claim.

The release gate is not marked Verified from unit tests alone. It requires the complete command
matrix, browser evidence, retained artifacts, package verification, and the published-artifact
rerun.
