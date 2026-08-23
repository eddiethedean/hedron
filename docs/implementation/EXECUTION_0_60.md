# Phase 0.60 execution plan

**Status:** In progress — Stage 0 packet and additive runtime slice implemented; release gates remain Planned
**Authority:** RFC-0089 / proposed D-108 / `THEME_PLATFORM_060.md`
**Target:** `v0.60.0`

## Milestones

| Milestone | Workstreams | Required exit |
|---|---|---|
| E0 — lock | W0 | Baseline, component-contract/profile map, issue mapping, schemas, diagnostics, budgets, and capped theme brief reviewed |
| E1 — truth | W1 | 0.59 claim/runtime reconciliation is executable and all gaps are owned |
| E2 — color | W2 | Modern color parser, palette-v2, fallback, provenance, contrast, fuzz, and compatibility pass |
| E3 — author | W3 | ThemeSpec, builder, token graph, patches, registry-derived contracts/profiles, fingerprints, validation, and packages pass |
| E4 — context | W4–W5 | Accessibility modes, recipe registry, explicitness, and scoped context pass |
| E5 — preference | W6 | Server-first preference, picker, CSP boot, no-JS, history, and no-flash browser matrix pass |
| E6 — components | W7–W8 | #627–#630 zero-CSS component fixtures pass across required modes |
| E7 — fleet | W9 | Reviewed built-in catalog and every package disposition pass the fleet matrix |
| E8 — experience | W10 | CLI, Theme Lab, conformance kit, starter, documentation, lifecycle, and diagnostics workflows pass |
| E9 — harden | W11 | Security, a11y, visual, compatibility, performance, and regression gates pass |
| E10 — cut | W12 | All gates Verified, #627–#635 closed from evidence, clean packages, release truth checked |

## Dependency rules

- E0 is the only allowed first milestone.
- E1 must finish before any 0.59 claim is reused as 0.60 evidence.
- E2 precedes color-seeded ThemeSpec/package validation.
- E3 establishes registry-derived contracts and profiles before package-backed recipes, preference
  selection, conformance fixtures, or built-in catalog packaging.
- E4 recipe scope work stops if explicit-authored-value tracking cannot preserve precedence.
- E5 may prototype earlier but cannot close before the registered theme catalog is stable.
- E6 component work may proceed after E0 and integrate with E4/E7 before closure.
- E7 cannot accept a built-in theme without E3/E4 validation and accessibility-mode coverage.
- E8 consumes shared validation services; it may not reimplement them in CLI or Explorer.
- E10 never waives or converts a Required gate to Deferred.

## Pull-request sequence

1. Contract and issue mapping only.
2. Reconciliation tests and reports only.
3. Color model/parser and palette-v2 schema.
4. Canonical ThemeSpec, semantic graph, ThemeBuilder facade, and ThemePatch composition.
5. ComponentThemeContract registry, coverage profiles, relationship validation, fingerprints, then
   theme package/archive/registry integration.
6. Accessibility modes and emitted media rules.
7. Explicitness tracking, RecipeFamily, then StyleContext/StyleScope.
8. ThemePreference/ThemePicker/server markers, then optional boot asset.
9. Brand and ToastHost vertical slices.
10. ConnectorFlow and ScrollRegion vertical slices.
11. Built-in themes and whole-fleet token/state migration.
12. Shared tooling, Theme Lab, conformance kit, docs, templates, lifecycle, and upgrade paths.
13. Cross-cutting hardening and release rehearsal.

Each implementation PR names its RFC section, workstream, issue(s), gate(s), public compatibility
effect, security/a11y evidence, and rollback. A marker-only test is not sufficient for visual,
layout, color, announcement, or no-flash claims.

## Stop conditions

Stop and require a contract amendment if:

- a modern color cannot be converted/gamut-mapped deterministically in the pure-Python path;
- ThemeBuilder becomes a second token/theme authority rather than a facade over ThemeSpec;
- a public themeable component can ship without a registered component contract and profile
  disposition;
- ThemePatch accepts arbitrary CSS, suppresses provenance, or bypasses complete revalidation;
- compilation fingerprints are non-reproducible or omit registry/algorithm compatibility inputs;
- package loading requires executable hooks or remote resources;
- recipe defaults cannot distinguish explicit from omitted component values;
- a recipe field can influence behavior, semantic state, routes, effects, or authorization;
- forced-colors support requires suppressing user-agent colors globally;
- no-flash behavior requires unsafe inline script or request-provided selector values;
- detached fragment/overlay scope inheritance would require ambient process-global mutation;
- a required built-in theme lacks the complete accessibility/state matrix, or catalog breadth
  displaces platform/conformance completeness;
- the phase exceeds locked budgets without a measured, reviewed amendment.

## Release handoff

E10 produces the final gate report, issue audit, theme catalog/validation digests, built package
fixtures, visual review manifest, upgrade results, performance report, security/a11y summaries,
release notes, and rollback instructions. Version metadata changes only in the explicit release
change after all evidence is final.
