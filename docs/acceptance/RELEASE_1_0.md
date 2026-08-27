# Hedron `v1.0.0` interface-consolidation acceptance plan

**Status:** Stage 0 Refined; implementation and release evidence pending

**Baseline:** Verified Beta `v0.67.0`
**Target:** `v1.0.0`
**Authority:** [RFC-0096](../rfcs/RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md), D-114–D-117

The phase is governed by the [cut contract](one-zero-cut-contract.toml), [machine release
gate](release-gate-1.0.toml), [0.67 contract freeze](contract-freeze-067.toml), [compatibility
BOM](compatibility-bom-067.toml), [upgrade fixtures](upgrade-fixtures-1.0.md), [HTMX/Alpine
boundary](../api/HTMX_ALPINE_BOUNDARY_1_0.md), and [implementation
plan](../implementation/HEDRON_1_0.md).

This is a subtractive major release. It makes the canonical surface already shipped in 0.67 the
only ordinary surface, removes fully warned compatibility paths, and changes defaults and
documentation to the frozen model. It does not add a Required runtime capability that exists only
in 1.0, silently remove a 0.67 path, or claim that every importable symbol and satellite is Stable.

The Stage 0 packet is internally verifiable with `python scripts/check_100.py --check-plan`.
That command validates planning honesty only. It does not verify any Planned release gate or
authorize package/version changes.

## Entry decision

The predecessor requirement is satisfied: `v0.67.0` is implemented and its release gate is
Verified. Removal work remains blocked until `ENTRY-100` reconciles the actual 0.67 public surface
with the warning registry and freezes the enumerated stable 1.0 inventory. In particular, the
three in-tree route/include warnings are known fixtures, not evidence that every proposed removal
has been classified.

## Gates

| Gate | Required evidence |
|---|---|
| `ENTRY-100` | Immutable 0.67.0 baseline, generated public/task/artifact inventory, exact support window, no-drift check against the 0.67 freeze, and zero unclassified proposed removals |
| `SURFACE-100` | Enumerated canonical stable symbols/packages/tasks; one documented/scaffolded/generated path per task; Advanced/package-native/experimental boundaries remain explicit |
| `REMOVE-100` | Every deleted import, alias, decorator, argument, CLI/config/HDJ/markup form, root shim, controller, and tag has a complete 0.67 warning/finding and parity fixture; no dynamic compatibility layer remains |
| `MIGRATE-100` | Deterministic text/JSON/SARIF check and static idempotent migrator; no code execution or default overwrite; uncertainty is reported honestly |
| `COMPAT-100` | Complete canonical source/config/HDJ/CLI corpus imports, type-checks, executes, builds, and passes browser journeys unchanged on immutable 0.67.0 and 1.0.0 environments |
| `INTERACTION-100` | Local/request/combined `Interaction`, role-valid `Outcome`, document closure, lifecycle, state reconciliation, failure, and ordinary HTTP/no-JS behavior remain identical to the frozen contract |
| `ENGINE-100` | One engine per task; native/Alpine common widgets and retained specialist Web Components pass parity; public element ABI and third-party authoring remain supported |
| `TOOLING-100` | Docs, scaffolds, generated code, Explorer, check/inspect/build, scenarios, and HDJ emit canonical forms only and find all transitional forms |
| `TYPE-100` | Public signatures, overloads, stubs, schemas, import ownership, and Pyright corpus match the frozen inventory on the full Python/dependency matrix |
| `SECURITY-100` | Removal/default switches do not weaken escaping, trusted values, CSRF/CSP, production gates, redaction, plugin loading, or browser authority boundaries |
| `A11Y-100` | Retained canonical widgets pass semantic/no-JS, keyboard, focus, reflow/zoom, reduced-motion, forced-colors, and browser fixtures; no human-AT conformance claim is inferred |
| `PERF-100` | Feature-off and feature-on budgets do not regress beyond frozen thresholds; removals leave no duplicate assets, observers, shims, or startup work |
| `FLEET-100` | Coordinated packages cut together; independent satellites publish exact compatible ranges and package-native fixtures; optional imports remain honest |
| `DOCS-100` | Task-oriented migration/rollback guide, release/support policy, API task lint, and all maintained examples contain no compatibility spelling or contradictory 1.0 status claim |
| `REGRESS-100` | Full Python, adapter, HDJ, HTMX, Alpine, Web Component, browser, security, accessibility, package, and upgrade suites pass |
| `PKG-100` | Clean wheel/sdist/offline installs, dependency bounds, metadata/classifiers, notices, SBOM/signatures, import-order, and artifact reproducibility pass |
| `RELEASE-100` | All other rows Verified; support and rollback windows published; release rehearsal and immutable evidence approved; no undocumented removal or release blocker remains |

## Release shape

The coordinated 0.67 packages listed in the cut contract move together to `1.0.0`. Independently
versioned satellites retain their versions and must publish exact Hedron 0.67/1.x ranges. SemVer
protects the enumerated stable 1.x inventory; Beta/Experimental surfaces stay visibly outside that
promise. The cut makes no commercial SLA, multi-year LTS, human-AT, or blanket WCAG claim.

## Prerelease checkpoints

| Checkpoint | Exit evidence |
|---|---|
| `1.0a1` | `ENTRY-100`, complete inventory reconciliation, stable inventory, and immutable dual-version corpus |
| `1.0a2` | `SURFACE-100`, `REMOVE-100`, `MIGRATE-100`, and canonical docs/scaffolds/tooling |
| `1.0b1` | Interaction/engine/type/security/a11y/performance and full fleet adoption |
| `1.0rc1` | Dual-version compatibility, full regressions, clean artifacts, support/rollback publication, and zero undocumented removals |

## Stop conditions

Stop removal or the cut if a public 0.67 path lacks complete warning evidence, canonical source
requires a 1.0-only form, an engine migration loses behavior/fallback/ABI, a package has no honest
compatibility range, a security/accessibility boundary weakens, or the stable inventory cannot be
enumerated. Backport the correction to 0.67.x or defer it to 1.1; do not widen the 1.0 contract in
place. After publication, fix forward in 1.0.x rather than retagging or silently restoring aliases.
