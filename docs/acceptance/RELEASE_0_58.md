# Hedron `v0.58` progressive feature authoring acceptance

**Status:** Stage 0 Refined; implementation Planned  
**Required predecessor:** Published and Verified in-tree `v0.57.0` (satisfied; tag/PyPI deferred)  
**Target:** Hedron `v0.58.0`  
**Decision/RFC:** D-101 / D-102 / [RFC-0085](../rfcs/RFC-0085-PROGRESSIVE-FEATURE-AUTHORING.md)  
**Implementation plan:** [PROGRESSIVE_AUTHORING_058](../implementation/PROGRESSIVE_AUTHORING_058.md)  
**Tracking:** [progressive-tracking-058.toml](progressive-tracking-058.toml)

D-102 freezes the Stage 0 contract packet and exact Planned evidence commands. No 0.58 runtime
symbols, evidence implementations, version changes, or release claims exist yet.

## Outcome

Beginners can build a screen, typed form command, bounded data workspace, durable task UI,
dashboard, session login loop, and upload flow without learning every underlying interaction
primitive first. Every facade lowers to existing Hedron/FastAPI authorities and remains
inspectable, replaceable by named surface, scenario-testable, and safely ejectable to reviewable
explicit Python.

## Planned gate matrix

| Gate | State before Stage 0 | Evidence owner |
|---|---|---|
| `CONTRACT-058` | Planned | Public signatures, inventories, diagnostics, host dispositions |
| `LOWER-058` | Planned | Facade-to-primitive differential and no-second-runtime proof |
| `SCREEN-058` | Planned | Screen/Page/shell/navigation/native page behavior |
| `FORM-058` | Planned | Form model/control/validation/CSRF/effect/native+HTMX behavior |
| `RESOURCE-058` | Planned | Complete bounded DataWorkspace screen and CRUD scaffold |
| `TASK-058` | Planned | Scoped durable submit/status/cancel/result and polling behavior |
| `DASH-058` | Planned | Typed filters, loader/panel split, history, stale/fan-out behavior |
| `FLOW-058` | Planned | Session auth and upload composition boundaries |
| `EXPLAIN-058` | Planned | Static redacted explain/graph/check/ejection/source-map parity |
| `A11Y-058` | Planned | Semantics, keyboard, announcements, no-JS, zoom/media modes |
| `SECURITY-058` | Planned | Auth/tenant/CSRF/redirect/URL/upload/ejection/exposure adversarial proof |
| `ADAPTER-058` | Planned | Honest FastAPI/Flask/Django/portable/sim dispositions |
| `REGRESS-058` | Planned | Existing explicit APIs and 0.43–0.57 evidence |
| `DX-058` | Planned | Four scaffolds; inventoried starter adoption and measured learning path |
| `PKG-058` | Planned | Wheels, optional isolation, docs, upgrades, metadata, rehearsal |

Stage 0 replaces “Not created” with exact Planned rows in `release-gate-0.58.toml`; Stage 1 may
mark a row Verified only when its executable/immutable evidence exists. The cut permits zero
Deferred rows.

## Pre-Stage 0 checklist

- [x] D-101 and RFC-0085 assign phase 0.58 scope.
- [x] Existing handles, bundles, catalog, jobs, data, security, uploads, and presentation remain
      the lowering authorities.
- [x] No beginner namespace, global simple mode, second runtime, universal ORM discovery, hidden
      client state, worker/scheduler, identity provider, storage/scanning service, or automatic
      external exposure is authorized.
- [x] Workstreams W0–W12 and fifteen planned gates are named.
- [x] Published/Verified in-tree `v0.57.0` satisfies the Stage 0 source prerequisite.
- [x] Preserve the deferred 0.57 tag/PyPI status; registry upload is not a 0.58 design blocker.
- [x] Assign one phase owner and tracking packet for W0–W12.
- [x] Accept the Stage 0 refine decision (D-102).

## Stage 0 checklist

- [x] Freeze exact public signatures, generic shapes, modules, maturity, and exports.
- [x] Freeze finite named surfaces and facade-to-primitive lowering inventory.
- [x] Freeze versioned explanation and ejection source-map schemas.
- [x] Freeze diagnostic families and conflict/error behavior.
- [x] Freeze FastAPI/Flask/Django/portable/conformance/sim dispositions.
- [x] Freeze security requirements for CRUD, jobs, dashboards, sessions, and uploads.
- [x] Freeze scaffold inventory and clean-wheel expected outputs.
- [x] Freeze the complete starter/beginner/quick-start/golden-path/minimal/first-app documentation
      inventory and the highest applicable 0.58 abstraction for each entry.
- [x] Freeze numeric budgets and benchmark corpora without inventing silent slices.
- [x] Create `upgrade-fixtures-058.md` from final Published `v0.57.0`.
- [x] Create `release-gate-0.58.toml` and exact evidence commands.
- [x] Confirm Stage 0 changes contracts only: no runtime symbols or version bump.

## Stage 1 delivery checklist

- [ ] W1: explanation, named surfaces, source maps, safe whole/per-surface ejection.
- [ ] W2: `Hedron.screen` and `ScreenHandle`.
- [ ] W3: `Hedron.form_command` through existing `FormBody`/`ActionHandle` authority.
- [ ] W4: `DataWorkspace.with_screen` and complete CRUD scaffold.
- [ ] W5: `TaskFlow` with exact request scope and terminal polling.
- [ ] W6: `DashboardWorkspace` with typed URL filters and loader/panel split.
- [ ] W7: bounded `SessionAuthFlow` around explicit application callbacks.
- [ ] W8: bounded `UploadFlow` around explicit storage/scanning/result ownership.
- [ ] W9: CLI/Explorer explain, graph, preview, check, override, eject, and diff.
- [ ] W10: minimal/CRUD/dashboard/task scaffolds, all starter-example migrations, and progressive
      learning path.
- [ ] W11: adapter/conformance/sim capability dispositions and scenarios.
- [ ] W12: security, accessibility, three-engine, performance, upgrade, and package evidence.
- [ ] All fifteen gates Verified with zero Deferred.

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
- Whole-feature and one-surface ejections that pass generated parity scenarios.
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
- [ ] Every inventoried starter example uses the highest applicable 0.58 abstraction; explicit
      primitive spellings appear only in clearly labeled advanced/lowered/under-the-hood sections.
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
- Any maintained starter/beginner/quick-start/golden-path/minimal/first-app example still teaches a
  lower-level spelling first when an applicable 0.58 abstraction exists.
- Any `*-058` gate is Planned, Deferred, waived without accepted destination, or missing evidence.
