# Hedron 1.0 implementation and cut plan

**Status:** **Implemented and Verified; `v1.0.0` tag/PyPI publication pending**
**Baseline:** Verified Beta `v0.67.0`
**Target:** `v1.0.0`
**Authority:** RFC-0096 and D-114–D-117
**Acceptance:** [RELEASE_1_0](../acceptance/RELEASE_1_0.md)

## Objective

Cut the frozen 1.0 subset from 0.67 without inventing a second runtime or adding a Required
capability available only in the major release:

```text
immutable 0.67 public/task/artifact inventory
        -> canonical / Advanced / package-native / transitional dispositions
        -> complete warning + fixture reconciliation
        -> remove only fully evidenced transitional paths
        -> switch docs, tooling, scaffolds, defaults, and package metadata
        -> run one canonical corpus on both 0.67.0 and 1.0.0
```

## Invariants

1. The exact function-only authoring, single-tree returns, `Outcome`, `Interaction`, document-plan,
   browser authority, component-engine, and failure contracts stay as frozen in 0.67.
2. Any canonical correction needed by a 1.0 application lands in 0.67.x first or waits for 1.1.
3. No removal starts from prose alone. It starts from a complete warning record, a source/task
   inventory row, a before/after fixture, and an accepted replacement or non-fit decision.
4. A partial/unknown static-analysis result is useful diagnostic evidence but cannot authorize
   deletion.
5. 1.0 contains no dynamic compatibility facade, duplicate route style, alternate widget engine,
   hidden root shim, or “also spelled” stable documentation.
6. Advanced and package-native interfaces survive only when they provide a distinct capability or
   make optional ownership honest; they are not second beginner paths.
7. The stable promise is enumerated. Beta/Experimental contracts remain visibly outside SemVer's
   stable facade, and independent satellites keep independent versions.
8. Runtime corrections are limited to compatibility-preserving authorization fixes; no net-new
   Required capability is introduced. Package/version/classifier claims are explicit and bumped
   for the coordinated 1.0.0 cut.

## Entry audit (W0)

Generate inventories from the immutable `v0.67.0` artifacts and source tree, not moving `main`:

- root and package exports, stubs, signatures, overloads, schemas, decorators, protocols, and
  dynamic `__getattr__`/import behavior;
- docs, examples, scaffolds, generated code, CLI flags, configuration, HDJ, manifests, browser
  tags/controllers/assets, and package entry points;
- task-to-interface and task-to-engine mappings with canonical, Advanced, package-native,
  transitional, experimental, internal, and deferred dispositions;
- runtime and static warning coverage, callsite behavior, migration automation, and parity fixtures;
- exact coordinated/independent package, Python/dependency, browser, OS, Pyright, asset, adapter,
  and host resolutions; and
- stable maturity, support, security, rollback, and evidence-retention boundaries.

The non-executing generator emits `public-inventory-100.toml` and
`stable-inventory-100.toml` for exports/artifacts plus `task-inventory-100.toml` for every public
class, function, and method discovered in the immutable baseline source, including source lines
and AST-derived signatures. The task inventory is an ownership graph, not an automatic SemVer
promotion; stable status remains governed by the reviewed stable inventory.

Reconcile the generated inventory with `contract-freeze-067.toml`, the component-engine inventory,
the compatibility BOM, docs/API references, and `PUBLIC_FUTURE_WARNINGS`. The eleven warning
records (eight core route/include records plus three Flask adapter records) are fully reconciled.
`ENTRY-100` is Verified: every proposed removal has complete coverage and the stable inventory is
machine-enumerated.

## Work packages

| Work package | Scope | Exit gates |
|---|---|---|
| W0 — inventory and no-drift lock | Generate/reconcile the complete 0.67 surface and task graph; publish support window and exact matrix | `ENTRY-100` |
| W1 — canonical facade | Reduce root exports, docs task map, schemas, and package ownership to one stable path plus distinct Advanced/package-native seams | `SURFACE-100`, `TYPE-100` |
| W2 — removal slices | Remove one warning-backed slice at a time; delete aliases/shims/controllers/tags only after before/after parity | `REMOVE-100` |
| W3 — migration tooling | Finish target check and static migrator for imports, calls, args, config, CLI, HDJ, markup, manifests, and generated forms | `MIGRATE-100` |
| W4 — interaction/default cutover | Make frozen `Interaction`/`Outcome`/document closure canonical and remove parallel defaults without authority changes | `INTERACTION-100` |
| W5 — engine cutover | Finish common-widget native/Alpine lowering and specialist-host retention while preserving public task names and element ABI | `ENGINE-100` |
| W6 — authoring consumers | Convert docs, examples, templates, scaffolds, generated code, Explorer, scenarios, CLI, and HDJ to canonical forms | `TOOLING-100`, `DOCS-100` |
| W7 — hardening | Run security, a11y, performance, feature-off, lifecycle/leak, and negative corpora after compatibility code removal | `SECURITY-100`, `A11Y-100`, `PERF-100` |
| W8 — dual-version/fleet | Execute immutable canonical corpus on 0.67.0 and 1.0.0; verify adapters/satellites and exact ranges | `COMPAT-100`, `FLEET-100` |
| W9 — artifacts and cut | Build/reproduce packages, run full regression/rehearsal, publish support/rollback, approve immutable evidence | `REGRESS-100`, `PKG-100`, `RELEASE-100` |

W1 and W2 do not begin before W0. W3 can expand analyzers during W0 but cannot claim complete
automation until the inventory is closed. W4–W6 may proceed by independent, warning-backed slice
after `ENTRY-100`; W8 starts only when canonical artifacts are buildable; W9 is last.

## Execution contract

Every workstream produces three things: a reviewed code/configuration change, executable evidence,
and a machine-readable update to the 1.0 packet. A workstream is not complete because its code
exists or because a test passes locally. The owner must attach the exact baseline commit, Python and
dependency lock, browser/container identity where relevant, command output, artifact digest, and
the gate row it advances.

The immutable baseline is the published `v0.67.0` source/wheel/sdist and its lockfile. Create a
separate baseline directory outside the source packages (for example `.evidence/1.0/baseline/`)
containing:

- source commit and clean-install metadata;
- `pyproject.toml`, `uv.lock`, package versions, Python/Pyright versions, and adapter extras;
- browser, Playwright, OS/container, Alpine/HTMX asset, and Web Component ABI identities;
- exported symbol/signature snapshots and the 0.67 warning registry snapshot; and
- checksums for every input and generated report.

No workstream may use a moving checkout as its predecessor evidence. If a baseline artifact cannot
be reproduced, stop at `ENTRY-100` and repair the evidence rather than weakening the comparison.

## Deliverables and repository seams

The following files are the planned source-of-truth outputs. They are deliberately separate from
the human packet so tooling can reject drift and reviewers can inspect one bounded concern at a
time.

| Deliverable | Owner | Contents | First gate |
|---|---|---|---|
| `docs/acceptance/public-inventory-100.toml` | architecture/API | Every documented/exported/generated/configured/CLI/HDJ/markup/browser/package path, task, owner, maturity, and disposition | `ENTRY-100` |
| `docs/acceptance/task-inventory-100.toml` | architecture/API | AST-derived public class/function/method task-to-interface graph with immutable provenance | `ENTRY-100` |
| `docs/acceptance/stable-inventory-100.toml` | API/release | Enumerated SemVer-protected symbols, signatures, schemas, packages, and supported adapters | `SURFACE-100` |
| `docs/acceptance/removal-inventory-100.toml` | migration/API | One row per removed path, replacement/non-fit reason, warning code, fixture, confidence, and removal slice | `REMOVE-100` |
| `docs/acceptance/warnings-100.toml` | migration/tooling | Runtime/static warning schema, source forms, diagnostic metadata, and coverage status | `ENTRY-100` |
| `docs/acceptance/baseline-100.json` | release engineering | Immutable 0.67.0 commit, locks, artifacts, browsers, tools, and hashes | `ENTRY-100` |
| `docs/acceptance/support-policy-100.md` | release/docs | 0.67.x migration window, 1.x support boundary, rollback policy, and no-SLA/LTS claims | `ENTRY-100` |
| `docs/acceptance/compatibility-report-100/` | compatibility | Dual-version imports, typing, execution, build, CLI, HDJ, browser, and package reports | `COMPAT-100` |
| `.evidence/1.0/` (ignored) | all owners | Reproducible logs, traces, screenshots, SBOMs, wheels, sdists, and digests linked by packet rows | all gates |

Primary runtime seams are `packages/hedron-core/src/hedron_core/migration.py` (warning records),
`packages/hedron-core/src/hedron_core/__init__.py` and `packages/hedron/src/hedron/__init__.py`
(exports), `packages/hedron/src/hedron/cli/commands/check.py` (static findings), the routing and
interaction modules under `packages/hedron-core/src/hedron_core/` and `packages/hedron/src/hedron/`,
the browser asset/registry modules under `packages/hedron-core/src/hedron_core/`, HDJ under
`packages/hedron-jinja/src/hedron_jinja/`, and component/element registries under the core and
`hedron-elements` packages. Tests belong beside the relevant phase suites plus
`tests/upgrade/` for cross-version fixtures; generated evidence never belongs in source packages.

## Workstream runbooks

### W0 — inventory, baseline, and entry lock

1. Build the `v0.67.0` baseline in a clean environment and record the checksums and tool/browser
   identities in `baseline-100.json`. The repository generator is
   `scripts/generate_100_inventory.py`; it materializes the tag with `git archive`, parses exports
   without importing code, and emits deterministic public/stable/task inventories plus baseline
   counts. The task inventory preserves public class/function/method interfaces that are not
   visible in an import-only snapshot.
2. Extract `__all__`, public imports, signatures, overloads, schemas, decorators, CLI/config/HDJ
   forms, generated output, browser tags/controllers/assets, manifests, and package entry points.
3. Normalize aliases and alternate spellings by developer task, not by module name. Join the result
   to the component-engine dispositions and `contract-freeze-067.toml`.
4. Diff the generated result against docs, examples, scaffolds, Explorer, `PUBLIC_FUTURE_WARNINGS`,
   `codes.py`, and existing upgrade fixtures. Every mismatch becomes an inventory row.
5. Publish stable, transitional, Advanced, package-native, Beta, Experimental, internal, Deferred,
   and not-fit dispositions. Resolve the current eleven-warning floor (`app.component`,
   `app.fragment`, `app.include_feature`, `router.component`, `app.screen`, `app.refreshable`,
   `app.command`, `app.form_command`) against the complete extracted surface.
6. Publish the 0.67.x migration-support window and exact dual-version matrix. Do not choose a
   calendar release date; the cut remains evidence-triggered.

**Exit checklist:** all eight W0 deliverables exist; inventory counts are reproducible; every
proposed removal has a disposition; no public path is `unknown` without an owner; the stable
inventory is enumerated; and `python scripts/check_100.py --check-plan` plus `ENTRY-100` evidence
pass. Until then, no deletion or 1.0-only default switch is allowed.

### W1 — canonical surface and type boundary

1. Turn the stable inventory into the authoritative export/stub/signature allowlist. Remove only
   duplicate root re-exports; preserve package-native ownership and optional import errors.
2. Make function-only `page`/`view`/`action`, one-tree returns, role-valid `Outcome`, closed
   `Interaction`, `hedron.ui`, and `app.include` the only ordinary generated/scaffolded forms.
3. Mark retained `Page`, raw responses, low-level modules, and specialist hosts as Advanced or
   package-native in exports, docs, autodoc, and diagnostics.
4. Add API/task lint that fails when one task has two stable documented/scaffolded/generated paths,
   or when a Beta/Experimental path leaks into the stable facade.
5. Update typing stubs, overloads, schemas, import-order tests, autodoc snapshots, and package
   `__all__` assertions together; a signature change without its fixture is incomplete.

**Exit checklist:** `stable-inventory-100.toml` is reviewed; `SURFACE-100` and `TYPE-100` pass;
the canonical corpus still imports and type-checks against 0.67.0; and no package version has been
bumped.

### W2 — warning-backed removal slices

Process removals in small, independently revertible slices ordered by blast radius:

1. duplicate decorators/aliases and root shims;
2. duplicate component/controller/tag paths selected by `ENGINE-067`;
3. browser activation knobs and manual ordinary-page plugin paths;
4. duplicate response/update/interaction spellings; and
5. generated, CLI/config, HDJ, manifest, and template compatibility forms.

For each slice, add the complete row to `removal-inventory-100.toml`, implement the 0.67 warning or
static finding first, add the before/after fixture, run the non-executing migrator, update all
consumers, then delete the 1.0 path. Keep the old path in 0.67 migration tooling where the warning
contract requires it. Never use a dynamic `__getattr__`, import hook, shadow module, or broad alias
to make a removed path appear to work in 1.0.

**Exit checklist:** every deleted path has complete warning coverage, a replacement/non-fit reason,
an idempotent migration result, and parity evidence; `REMOVE-100` passes with zero undocumented
removals; and a clean search finds no compatibility spelling in the stable source/docs/generated
output.

### W3 — static checking and migration tooling

1. Extend `hedron check --target 1.0` to imports, calls, keyword arguments, config, CLI, HDJ,
   manifests, browser markup, generated code, and templates without importing or executing the
   application.
2. Emit deterministic text, JSON, and SARIF findings with code, source span, replacement/non-fit
   reason, owner, removal version, documentation anchor, fixture, and complete/partial/unknown
   confidence.
3. Implement `hedron migrate api --target 1.0` as a reviewable transform: default diff/report,
   explicit output/apply, no overwrite, no execution, idempotence, and a refusal for opaque or
   dynamic constructs that cannot be proven safe.
4. Keep runtime `HedronFutureWarning` records and static findings generated from the same registry;
   add a registry lint preventing duplicate codes, missing fixtures, or stale paths.

**Exit checklist:** `MIGRATE-100` passes the complete/partial/unknown corpus, no-execution probes,
SARIF schema, idempotence, and no-overwrite tests; static findings match runtime metadata; and
opaque constructs are reported rather than declared clean.

### W4 — interaction and lifecycle cutover

1. Validate the frozen `Interaction` union and role-indexed `Outcome` at construction, static check,
   route registration, and response lowering.
2. Verify local effects lower only to Alpine; request effects lower only to Hedron/HTMX; combined
   effects use one lifecycle coordinator and one request maximum.
3. Exercise document-plan closure, fragment subset checks, state ownership/reconciliation,
   init/cleanup/settle/OOB/history/error, focus/announcement, stale-result, and failure behavior.
4. Remove any parallel default path only after the 0.67 fixture demonstrates ordinary HTTP and
   no-JavaScript parity. Keep Morph non-admission valid and explicit.

**Exit checklist:** `INTERACTION-100` passes local/request/combined, reset/preserve, duplicate
request, dual-writer, cross-authority, OOB/history, missing-asset, and no-JS fixtures in all three
browsers; boundary traces are redacted and source-mapped.

### W5 — component-engine cutover

1. Convert each `ENGINE-067` disposition into a 1.0 inventory row with public Python task name,
   engine, owner, ABI, fallback, lifecycle, resource, CSP, and accessibility evidence.
2. Migrate only common widgets with native/Alpine parity. Retain chart/map/data-editor and other
   specialist hosts where their resource or ABI boundary is real.
3. Preserve the Web Component ABI and third-party author kit; never expose engine choice as an
   ordinary author parameter or publish parallel `Alpine*`/Web Component names.
4. Run keyboard/focus/no-JS/HTMX cleanup and browser parity before deleting each legacy wrapper.

**Exit checklist:** `ENGINE-100` passes one-task/one-engine lint, specialist-host ABI fixtures,
common-widget parity, fallback, CSP, lifecycle, and provenance checks.

### W6 — consumer and documentation migration

Migrate the maintained surface in dependency order: core examples and reference app, scaffolds and
generated projects, API/task pages and autodoc, Explorer and scenarios, FastAPI/Flask/Django/HDJ
adapters, Workbench/Posit, package-native satellite examples, CLI/config schemas, and migration
guides. Run the target check over the entire tree after each batch. The batch is rejected if it
introduces a second spelling, a deprecated browser asset, a missing feature demand, or a misleading
stability claim.

**Exit checklist:** `TOOLING-100` and `DOCS-100` pass source search, generated-output comparison,
task lint, API link checks, HDJ static checks, Explorer/scenario snapshots, and a clean beginner
walkthrough.

### W7 — quality closure after removals

Run the security, accessibility, and performance suites after compatibility code has been removed;
do not rely only on the 0.67 results. Include unsafe directive/HTML/URL/state inputs, CSRF/CSP and
redaction, production plugin policy, feature-off zero assets, leak/idempotent cleanup, lifecycle
repetition, keyboard/focus/reflow/forced-colors/reduced-motion/RTL, and cold/warm import/render/
request/asset measurements. Numeric ceilings are frozen from evidence and recorded in the packet;
benchmarks cannot bypass semantic or security checks.

**Exit checklist:** `SECURITY-100`, `A11Y-100`, and `PERF-100` pass on the declared matrix with no
new waiver that lacks an owner, expiry, and explicit maturity downgrade.

### W8 — dual-version and fleet compatibility

1. Build the canonical corpus once and run it in isolated 0.67.0 and 1.0.0 environments. Compare
   imports, Pyright, rendered HTML/manifest/trace facts, HTTP outcomes, browser screenshots/traces,
   CLI/HDJ/build output, and error metadata with approved nondeterministic fields only.
2. Run the coordinated package matrix together and each independent satellite at its exact declared
   range. Test optional packages both installed and absent; import-order tests must remain acyclic.
3. Retain the exact lock, wheel/sdist hashes, browser identities, and reports for every matrix row.
   A declared-but-untested range is Unsupported, never inferred from a neighboring row.

**Exit checklist:** `COMPAT-100` and `FLEET-100` pass all canonical/shared/transitional/negative/
rollback lanes; no 1.0 fixture depends on a removed 0.67 path; and all independent ranges are
published in package metadata and docs.

### W9 — artifacts, release candidate, and cut

1. Update coordinated package versions/classifiers/changelogs on the dedicated `v1.0` branch once
   the implementation surface is ready; publication still waits for every behavior and migration
   gate. Keep independent satellite versions independent.
2. Build clean wheels and sdists twice from the same source with normalized timestamps; compare
   manifests, hashes, license notices, SBOMs, and browser assets.
3. Exercise offline installation, fresh virtual environments, import order, CLI scaffolding,
   rollback rehearsal, and the release workflow from the candidate tag.
4. Publish support/rollback policy and migration documentation, then request `RELEASE-100` approval.
   Tag and publish only from the approved immutable commit.

**Exit checklist:** `REGRESS-100`, `PKG-100`, and `RELEASE-100` are Verified; every prior gate is
Verified; the release report links all evidence; and no user-facing page calls the candidate
released before publication.

## Pull-request sequence and ownership

Use one narrowly scoped PR per row or removal slice. The recommended order is:

| PR group | Required contents | Must be green before |
|---|---|---|
| P0 baseline | W0 generators, snapshots, inventories, support policy, checker schemas | Any runtime deletion |
| P1 surface | Stable exports, signatures, API/task lint, package ownership | P2 |
| P2 migration registry | Warning records, codes, static findings, fixture harness | P3 |
| P3 migration transforms | One warning-backed removal slice per PR, with before/after fixtures | P4 |
| P4 interaction | Outcome/Interaction validation, lifecycle traces, closure/state fixtures | P5 |
| P5 engines | One component disposition/migration at a time, ABI and fallback evidence | P6 |
| P6 consumers | Examples, scaffolds, Explorer, HDJ, adapters, CLI/config, docs | P7 |
| P7 hardening | Security/a11y/performance and three-browser reruns | P8 |
| P8 fleet | Dual-version and satellite matrices, lock/artifact reports | P9 |
| P9 release | Version/changelog/metadata changes, clean artifacts, release rehearsal | Tag/publication |

Every PR description includes the task, disposition row, gate IDs, baseline identity, changed
authority (which must remain unchanged), fixture commands, and rollback action. Reviewers reject
mixed removal slices that cannot be reverted independently.

## Verification command matrix

The exact commands live in `release-gate-1.0.toml`; this is the execution order and minimum CI
shape. Commands that verify implementation evidence do not exist until the corresponding workstream
lands; the planning checker must continue to fail closed before then.

```text
python scripts/generate_100_inventory.py --baseline v0.67.0 --output-dir docs/acceptance
python scripts/check_100.py --check-plan
python scripts/check_100.py --gate ENTRY-100 --verify
python scripts/check_100.py --gate SURFACE-100 --verify
python scripts/check_100.py --gate TYPE-100 --verify
python scripts/check_100.py --gate REMOVE-100 --verify
python scripts/check_100.py --gate MIGRATE-100 --verify
python scripts/check_100.py --gate INTERACTION-100 --verify
python scripts/check_100.py --gate ENGINE-100 --verify
python scripts/check_100.py --gate TOOLING-100 --verify
python scripts/check_100.py --gate DOCS-100 --verify
python scripts/check_100.py --gate SECURITY-100 --verify
python scripts/check_100.py --gate A11Y-100 --verify
python scripts/check_100.py --gate PERF-100 --verify
python scripts/check_100.py --gate COMPAT-100 --verify
python scripts/check_100.py --gate FLEET-100 --verify
bash scripts/ci_checks.sh all --python 3.12 --all-browsers --gate-version 1.0.0 --jobs 1
python scripts/check_100.py --gate PKG-100 --verify
python scripts/check_100.py --gate RELEASE-100 --verify
```

The CI matrix must include CPython 3.10–3.14, the exact FastAPI/Pydantic bounds, FastAPI plus
Flask/Django/HDJ adapter rows, optional satellite present/absent rows, Pyright, and Chromium/
Firefox/WebKit. Browser rows run on the pinned Playwright lock and record screenshots/traces;
non-browser rows run in clean isolated environments. The release job consumes evidence artifacts
from earlier jobs and never converts a Planned row to Verified by editing TOML.

## Definition of done

Phase 1.0 is fully implemented only when all of the following are true:

- the 0.67 baseline and public inventory are reproducible and `ENTRY-100` is Verified;
- the stable inventory is enumerated and one task has one ordinary public path;
- every removed path was warned/found in 0.67, migrated or explicitly dispositioned, and fixture-backed;
- the canonical interaction, outcome, document-plan, lifecycle, component-engine, fallback,
  security, accessibility, and performance contracts pass after removal;
- the same canonical source/config/HDJ/CLI corpus passes unchanged on 0.67.0 and 1.0.0;
- coordinated packages build at 1.0.0 while independent satellites retain exact ranges;
- docs, scaffolds, generated code, Explorer, and package metadata contain no stale compatibility
  spelling or contradictory maturity/release claim;
- clean, offline, reproducible artifact and rollback rehearsals pass; and
- all 17 release rows are Verified with no undocumented removal, unsupported range, or open cut
  blocker.

## Removal slice protocol

Each pull request names one developer task and contains:

1. the 0.67 source/artifact inventory rows and usage evidence;
2. canonical, Advanced, package-native, removal, or non-fit disposition;
3. exact 0.67 warning/finding with complete coverage;
4. before/after source, typing, runtime, HTTP/no-JS, browser, security, and accessibility fixtures
   appropriate to the task;
5. migrator transform or explicit manual reason, including idempotence and no-execution proof;
6. root/package export, docs, scaffold, HDJ, CLI/config, manifest, and generated-code updates; and
7. a dual-version canonical fixture proving the replacement already runs on 0.67.0.

If any item is absent, keep the 0.67 path out of the stable facade but do not delete it in that
slice. An accepted amendment may defer the removal to 2.0; it may not make the deletion silent.

## Verification order

1. `python scripts/check_100.py --check-plan`
2. `ENTRY-100`, then `SURFACE-100` and `TYPE-100`
3. per-task `REMOVE-100` and `MIGRATE-100` slices
4. interaction/engine/tooling/docs checks
5. security/a11y/performance checks
6. immutable 0.67.0/1.0.0 compatibility and fleet matrix
7. full regressions, package/offline/reproducibility checks, and release rehearsal
8. `RELEASE-100` only after every earlier machine row is Verified

The planning checker intentionally refuses `--verify` for a Planned gate. Gate verification is
added only with its executable evidence; changing prose or a TOML state is insufficient.

## Rollback and stop rules

Before publication, stop and restore the last fully canonical internal build if a removal violates
the warning/fixture rule, canonical code fails on 0.67, a package range is unresolved, or an
authority/security/a11y/ABI boundary changes. After publication, preserve the tag and fix forward
in 1.0.x. Do not reintroduce silent aliases; if an emergency compatibility aid is unavoidable, it
requires a public decision, explicit diagnostic, expiry, and removal release.
