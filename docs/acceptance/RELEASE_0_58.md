# Hedron `v0.58` progressive feature and styling authoring acceptance

**Status:** Stage 0 Refined; implementation Planned  
**Required predecessor:** Published and Verified in-tree `v0.57.0` (satisfied; tag/PyPI deferred)  
**Target:** Hedron `v0.58.0`  
**Decision/RFC:** D-101 / D-102 / D-105 / [RFC-0085](../rfcs/RFC-0085-PROGRESSIVE-FEATURE-AUTHORING.md)

**Implementation plan:** [PROGRESSIVE_AUTHORING_058](../implementation/PROGRESSIVE_AUTHORING_058.md)  
**Tracking:** [progressive-tracking-058.toml](progressive-tracking-058.toml)

D-102 freezes the feature-authoring contracts. D-105 folds the complete progressive-styling
contract into the same Stage 0 packet and exact Planned evidence commands. No 0.58 runtime symbols,
evidence implementations, version changes, or release claims exist yet.

## Outcome

Beginners can build a branded screen, typed form command, bounded data workspace, durable task UI,
dashboard, session login loop, and upload flow without learning every interaction or styling
primitive first. One small design input compiles to a coordinated light/dark `Theme`; semantic
recipes style generated feature roles; explicit scopes provide bounded local variation. Every
feature and styling abstraction lowers to existing Hedron/FastAPI/theme/component/CSS-build
authorities and remains inspectable, locally replaceable, scenario-testable, and safely ejectable.

## Planned gate matrix

| Gate | State before Stage 0 | Evidence owner |
|---|---|---|
| `CONTRACT-058` | Planned | Feature/design signatures, inventories, schemas, diagnostics, dispositions |
| `LOWER-058` | Planned | Facade-to-primitive differential and no-second-runtime proof |
| `SCREEN-058` | Planned | Screen/Page/shell/navigation/native page behavior |
| `FORM-058` | Planned | Form model/control/validation/CSRF/effect/native+HTMX behavior |
| `RESOURCE-058` | Planned | Complete bounded DataWorkspace screen and CRUD scaffold |
| `TASK-058` | Planned | Scoped durable submit/status/cancel/result and polling behavior |
| `DASH-058` | Planned | Typed filters, loader/panel split, history, stale/fan-out behavior |
| `FLOW-058` | Planned | Session auth and upload composition boundaries |
| `BRAND-058` | Planned | Deterministic coordinated light/dark brand compilation and disclosed adjustment |
| `THEME-058` | Planned | Typed design groups, `Theme` bridge, constructor normalization, and build parity |
| `RECIPE-058` | Planned | Family-scoped recipes, built-in feature roles, clone/precedence behavior |
| `SCOPE-058` | Planned | Explicit bounded theme/color-mode/density scopes and marker parity |
| `EXPLAIN-058` | Planned | Static redacted feature/design explain, preview, diff, check, ejection, and source-map parity |
| `VISUAL-058` | Planned | Deterministic design gallery and three-engine visual/computed-fact matrix |
| `A11Y-058` | Planned | Semantics, contrast, keyboard, announcements, no-JS, zoom/media modes |
| `SECURITY-058` | Planned | Auth/tenant/CSRF/redirect/URL/upload/CSP/asset/ejection/exposure adversarial proof |
| `ADAPTER-058` | Planned | Honest FastAPI/Flask/Django/portable/sim dispositions |
| `REGRESS-058` | Planned | Existing explicit feature/styling APIs and 0.43–0.57 evidence |
| `DX-058` | Planned | Four scaffolds; both starter inventories and measured learning path |
| `PKG-058` | Planned | Wheels, optional isolation, docs, upgrades, metadata, rehearsal |

The Stage 0 packet records exact Planned rows in `release-gate-0.58.toml`; Stage 1 may mark a row
Verified only when its executable/immutable evidence exists. The cut permits zero Deferred rows.

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

- [ ] W0: maintain the single unified contract and inventory packet.
- [ ] W1: shared explanation, named surfaces, design plans, provenance, source maps, and safe
      whole/partial ejection.
- [ ] W2: `Hedron.screen` and `ScreenHandle`.
- [ ] W3: `Hedron.form_command` through existing `FormBody`/`ActionHandle` authority.
- [ ] W4: `DataWorkspace.with_screen` and complete CRUD scaffold.
- [ ] W5: `TaskFlow` with exact request scope and terminal polling.
- [ ] W6: `DashboardWorkspace` with typed URL filters and loader/panel split.
- [ ] W7: bounded `SessionAuthFlow` around explicit application callbacks.
- [ ] W8: bounded `UploadFlow` around explicit storage/scanning/result ownership.
- [ ] W9: `DesignSystem` brand compiler, typed design groups, `Theme` bridge, and `Hedron(theme=...)`
      normalization.
- [ ] W10: semantic recipes, built-in generated-surface roles, `StyleScope`, and exact precedence.
- [ ] W11: one CLI/Explorer explain, graph, preview, diff, check, override, and eject toolchain.
- [ ] W12: feature↔styling integration, including shared IDs, override precedence, and both recipe-
      preserving and fully explicit ejection.
- [ ] W13: minimal/CRUD/dashboard/task scaffolds, every starter migration, and one progressive
      feature-and-styling learning path.
- [ ] W14: adapter/conformance/sim/package capability dispositions and scenarios.
- [ ] W15: security/CSP, accessibility, three-engine visual, and performance evidence.
- [ ] W16: explicit API regression and unified `v0.57.0` upgrade evidence.
- [ ] W17: packaging, documentation truth, and release rehearsal.
- [ ] All twenty gates Verified with zero Deferred.

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

- [ ] Train packages and workspace bumped to `0.58.0` only after all gates Verify.
- [ ] New APIs documented as Beta; existing stable/explicit API classifications unchanged unless a
      separate accepted promotion says otherwise.
- [ ] `docs/release.toml`, STATUS, ROADMAP, release notes, changelogs, compatibility, and registry
      truth updated.
- [ ] Clean wheels install every scaffold with optional packages both present and absent.
- [ ] Every inventoried starter example uses the highest applicable 0.58 feature and styling
      abstractions; explicit primitive spellings appear only in clearly labeled advanced/lowered/
      under-the-hood sections.
- [ ] Release rehearsal verifies no hidden runtime/asset/dependency cost when facades are unused.
- [ ] Git tag/PyPI action follows the repository's release authorization; this plan does not tag.

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
