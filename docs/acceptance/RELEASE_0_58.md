# Hedron `v0.58` progressive feature and styling authoring acceptance

**Status:** Published / Verified (`v0.58.0` on PyPI)<br>
**Required predecessor:** Published and Verified in-tree `v0.57.0` (satisfied; tag/PyPI deferred)<br>
**Target:** Hedron `v0.58.0`<br>
**Decision/RFC:** D-101 / D-102 / D-105 / [RFC-0085](../rfcs/RFC-0085-PROGRESSIVE-FEATURE-AUTHORING.md)<br>
**Implementation plan:** [PROGRESSIVE_AUTHORING_058](../implementation/PROGRESSIVE_AUTHORING_058.md)<br>
**Tracking:** [progressive-tracking-058.toml](progressive-tracking-058.toml)

Stage 0 froze the progressive feature and styling contracts. Stage 1 implemented the
workstreams, Verified all twenty gates, and cut the in-tree tip to `v0.58.0`.
**Do not tag yet.**

Beginners can build a branded screen, typed form command, bounded data workspace, durable
task UI, dashboard, session login loop, and upload flow without learning every interaction
or styling primitive first. One small design input compiles to a coordinated light/dark
`Theme`; semantic recipes style generated feature roles; explicit scopes provide bounded
local variation. Every feature and styling abstraction lowers to existing
Hedron/FastAPI/theme/component/CSS-build authorities and remains inspectable, locally
replaceable, scenario-testable, and safely ejectable.

## Exact gate matrix

| Gate | State | Evidence command |
|---|---|---|
| `CONTRACT-058` | Verified | `python scripts/check_contract_058.py` |
| `LOWER-058` | Verified | `python scripts/check_lower_058.py` |
| `SCREEN-058` | Verified | `python scripts/check_screen_058.py` |
| `FORM-058` | Verified | `python scripts/check_form_058.py` |
| `RESOURCE-058` | Verified | `python scripts/check_resource_058.py` |
| `TASK-058` | Verified | `python scripts/check_task_058.py` |
| `DASH-058` | Verified | `python scripts/check_dash_058.py` |
| `FLOW-058` | Verified | `python scripts/check_flow_058.py` |
| `BRAND-058` | Verified | `python scripts/check_brand_058.py` |
| `THEME-058` | Verified | `python scripts/check_theme_058.py` |
| `RECIPE-058` | Verified | `python scripts/check_recipe_058.py` |
| `SCOPE-058` | Verified | `python scripts/check_scope_058.py` |
| `EXPLAIN-058` | Verified | `python scripts/check_explain_058.py` |
| `VISUAL-058` | Verified | `python scripts/check_visual_058.py` |
| `A11Y-058` | Verified | `python scripts/check_a11y_058.py` |
| `SECURITY-058` | Verified | `python scripts/check_security_058.py` |
| `ADAPTER-058` | Verified | `python scripts/check_adapter_058.py` |
| `REGRESS-058` | Verified | `python scripts/check_regress_058.py` |
| `DX-058` | Verified | `python scripts/check_dx_058.py` |
| `PKG-058` | Verified | `python scripts/check_pkg_058.py` |

Machine-readable index: [release-gate-0.58.toml](release-gate-0.58.toml) (`status = "Verified"`;
zero Deferred).

## Pre-Stage 0 checklist

- [x] D-101/D-102/D-105 and RFC-0085 assign one integrated phase 0.58 scope.
- [x] Existing handles, bundles, catalog, jobs, data, security, uploads, and presentation remain
      the lowering authorities.
- [x] Existing `Theme`, appearance props/markers, style contracts, scoped CSS, the CSS compiler,
      asset manifest, cascade, and CSP policy remain the styling authorities.
- [x] No beginner namespace, global simple mode, second runtime, second theme registry/cascade/
      compiler, universal ORM discovery, hidden client state, worker/scheduler, identity provider,
      storage/scanning service, runtime CSS injector, or automatic external exposure is authorized.
- [x] Workstreams W0–W17 and twenty planned gates are named.
- [x] Published/Verified in-tree `v0.57.0` satisfies the Stage 0 source prerequisite.
- [x] Preserve the deferred 0.57 tag/PyPI status; registry upload is not a 0.58 design blocker.
- [x] Assign one phase owner and tracking packet for W0–W17.
- [x] Accept the unified Stage 0 refine decisions (D-102 and D-105).

## Stage 0 checklist

- [x] Freeze exact public signatures, generic shapes, modules, maturity, and exports.
- [x] Freeze finite named surfaces and facade-to-primitive lowering inventory.
- [x] Freeze `DesignSystem`, brand/theme normalization, typed design groups, recipes, `StyleScope`,
      feature-role integration, and their lowering to the current styling system.
- [x] Freeze versioned feature explanation, design plan/diff/preview, and ejection source-map
      schemas with shared provenance and deterministic composition.
- [x] Freeze styling precedence: explicit component or named-surface override, explicit recipe,
      nearest explicit scope, design default, resolved `Theme`, then first-party baseline.
- [x] Freeze diagnostic families and conflict/error behavior.
- [x] Freeze FastAPI/Flask/Django/portable/conformance/sim dispositions.
- [x] Freeze security requirements for CRUD, jobs, dashboards, sessions, uploads, styling inputs,
      assets, CSP, static tooling, and ejection.
- [x] Freeze scaffold inventory and clean-wheel expected outputs.
- [x] Freeze the complete starter/beginner/quick-start/golden-path/minimal/first-app/theming/scaffold
      documentation inventory and the highest applicable 0.58 feature and styling abstractions for
      each entry.
- [x] Freeze numeric budgets and benchmark corpora without inventing silent slices.
- [x] Create `upgrade-fixtures-058.md` from final Published `v0.57.0`.
- [x] Create `release-gate-0.58.toml` and exact evidence commands.
- [x] Confirm Stage 0 changes contracts only: no runtime symbols or version bump.

## Stage 1 delivery checklist

- [x] W0: maintain the single unified contract and inventory packet.
- [x] W1: shared explanation, named surfaces, design plans, provenance, source maps, and safe
      whole/partial ejection.
- [x] W2: `Hedron.screen` and `ScreenHandle`.
- [x] W3: `Hedron.form_command` through existing `FormBody`/`ActionHandle` authority.
- [x] W4: `DataWorkspace.with_screen` and complete CRUD scaffold.
- [x] W5: `TaskFlow` with exact request scope and terminal polling.
- [x] W6: `DashboardWorkspace` with typed URL filters and loader/panel split.
- [x] W7: bounded `SessionAuthFlow` around explicit application callbacks.
- [x] W8: bounded `UploadFlow` around explicit storage/scanning/result ownership.
- [x] W9: `DesignSystem` brand compiler, typed design groups, `Theme` bridge, and `Hedron(theme=...)`
      normalization.
- [x] W10: semantic recipes, built-in generated-surface roles, `StyleScope`, and exact precedence.
- [x] W11: one CLI/Explorer explain, graph, preview, diff, check, override, and eject toolchain.
- [x] W12: feature↔styling integration, including shared IDs, override precedence, and both recipe-
      preserving and fully explicit ejection.
- [x] W13: minimal/CRUD/dashboard/task scaffolds, every starter migration, and one progressive
      feature-and-styling learning path.
- [x] W14: adapter/conformance/sim/package capability dispositions and scenarios.
- [x] W15: security/CSP, accessibility, three-engine visual, and performance evidence.
- [x] W16: explicit API regression and unified `v0.57.0` upgrade evidence.
- [x] W17: packaging, documentation truth, and release rehearsal.
- [x] All twenty gates Verified with zero Deferred.

## Required representative evidence

- A hello/status app using `screen` and one refreshable view.
- A typed form app using `form_command`, plus its explicit `command`/`FormBody` equivalent.
- An authorized persisted notes/orders workspace with list/detail/create/edit and delete disabled by
  default.
- A sales dashboard with typed filters, metric/chart/table panels, URL history, slow/stale errors,
  and one explicit advanced interaction.
- A durable report task with subject+tenant scoping, status, cancel disposition, terminal polling,
  failure, and authorized download.
- A session login/protected workspace/logout/timeout loop without claiming IdP or authorization
  ownership.
- An upload/quarantine/process/result flow with parser limits, cleanup, scanning callback, and
  independent download authorization.
- A mixed-level application proving facade and explicit interfaces compose.
- The same applications using a built-in theme and a generated brand, built-in semantic feature
  roles, one recipe override, and one explicit `StyleScope` without behavior or accessibility drift.
- Whole-feature and one-surface ejections that pass generated parity scenarios, with styling either
  preserved as recipe references or resolved to explicit public props/`Theme`/scoped CSS.
- Chromium, Firefox, WebKit, native HTTP, HTMX, failed-upgrade/no-JS, strict-CSP, keyboard,
  screen-reader semantics, 200% zoom, narrow viewport, reduced motion, forced colors, RTL, print,
  long-content, and fragment replacement evidence where applicable.

## Cut checklist

- [x] Train packages and workspace bumped to `0.58.0` only after all gates Verify.
- [x] New APIs documented as Beta; existing stable/explicit API classifications unchanged unless a
      separate accepted promotion says otherwise.
- [x] `docs/release.toml`, STATUS, ROADMAP, release notes, changelogs, compatibility, and registry
      truth updated.
- [x] Clean wheels install every scaffold with optional packages both present and absent.
- [x] Every inventoried starter example uses the highest applicable 0.58 feature and styling
      abstractions; explicit primitive spellings appear only in clearly labeled advanced/lowered/
      under-the-hood sections.
- [x] Release rehearsal verifies no hidden runtime/asset/dependency cost when facades are unused.
- [x] PyPI publication is recorded in `docs/release.toml`; Git tagging remains a separately
  authorized maintainer action.

## Automatic cut blockers

- Any facade owns a second request/workflow/render runtime.
- Any rendered component or included feature becomes remotely exposed without explicit opt-in.
- Any mutation/auth/job/upload path infers authorization, tenancy, destructive intent, persistence,
  transaction, worker, storage, scanning, or retention authority.
- Any facade lacks a native HTTP path, named override, static explanation, or safe ejection path.
- Any explanation/ejection invokes application callbacks or emits sensitive values.
- Any task observation substitutes stored identity for the current caller or permits job
  enumeration.
- Any dashboard accepts sensitive URL filters or unbounded refresh fan-out.
- Any upload display limit diverges from enforcement or cleanup fails on a terminal path.
- Any host is labeled Supported without native framework authority and parity evidence.
- Any styling abstraction adds another theme registry, cascade, selector language, CSS compiler,
  runtime injector, browser state store, hidden I/O, implicit remote asset, or inline-style need.
- Any generated design silently ships a failing contrast pair or undisclosed color adjustment.
- Any recipe or scope changes authorization, routes, effects, destructive meaning, DOM/reading
  order, accessible names, authoritative values, interaction, or application state.
- Any feature named-surface override loses to a generated styling default.
- Any maintained starter/beginner/quick-start/golden-path/minimal/first-app/theming/scaffold example
  still teaches a lower-level feature or styling spelling first when an applicable 0.58 abstraction
  exists.
- Any `*-058` gate is Planned, Deferred, waived without accepted destination, or missing evidence.
