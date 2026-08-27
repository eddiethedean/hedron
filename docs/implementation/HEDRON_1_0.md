# Hedron 1.0 implementation and cut plan

**Status:** Stage 0 Refined; W1 removal work blocked on `ENTRY-100`
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
8. No package/version/classifier claim changes during Stage 0 refinement.

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

Reconcile the generated inventory with `contract-freeze-067.toml`, the component-engine inventory,
the compatibility BOM, docs/API references, and `PUBLIC_FUTURE_WARNINGS`. The current three warning
records are a known lower bound. `ENTRY-100` remains Planned until every proposed removal has
complete coverage and the stable inventory is machine-enumerated.

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
