# Phase 0.65 execution plan

Status: **Planned**. The sequence is an implementation plan, not evidence that any milestone has
shipped.

Authority: [RFC-0092](../rfcs/RFC-0092-INTEGRATED-STYLING-PLATFORM.md),
[APPLICATION_STYLING_065](APPLICATION_STYLING_065.md), and the
[refined scope](../acceptance/application-styling-scope-065.md).

## Ordered milestones

| Milestone | Scope | Depends on | Exit evidence |
|---|---|---|---|
| E0 | Reconcile `v0.64.1`, audit live issue bodies, freeze the refined Required/Progressive boundary, and baseline the existing theme/compiler/asset authorities | — | D-110, issue-to-gate matrix, measured budgets, and scope checklist accepted |
| E1 | Register local application stylesheets in the asset and CSP/HTMX graphs | E0 | asset manifest, fingerprint, head/fragment and no-JS fixtures |
| E2 | Emit and inventory public component/part/state hooks | E0 | hook manifest, stability rules, browser markup fixtures |
| E3 | Add namespaced application tokens to ThemeSpec/ThemePatch and provenance | E0 | token schema, collision/rejection tests, theme matrix |
| E4 | Add the `application` cascade layer and scoped/global ordinary CSS policy | E1–E3 | compiled CSS, layer-order, specificity and source-map fixtures |
| E5 | Build static style explain/inspect/check diagnostics | E1–E4 | deterministic redacted findings and exit-code tests |
| E6 | Build provenance-preserving ejection, diff, and update checks | E4–E5 | round-trip, drift, rollback, and partial-ejection fixtures |
| E7 | Deliver six named motion presets, five #693 public-part/state slices, data-view chrome, and native-control families | E2–E6 | #690/#693/#694/#698 mapped tests and fallback matrices |
| E8 | Apply cross-cutting focus/preference/print/RTL/no-JS checks to touched surfaces; disposition broader navigation/overlay/layout/type/media/icon/visualization work | E2–E7 | Required fallback journeys and owned Progressive/Deferred inventory |
| E9 | Migrate flagship, starters, component packages, and adapter examples | E1–E8 | fleet matrix with zero private-selector dependence |
| E10 | Harden security, accessibility, performance, browser compatibility, and upgrades | E7–E9 | all planned gates verified or explicitly rehomed |
| E11 | Publish docs, migration guide, API references, and release evidence | E10 | release packet complete and docs checks green |

## Critical path

`E0 → E1/E2/E3 → E4 → E5 → E6 → E7 → E8 → E9 → E10 → E11`.

E1, E2, and E3 may proceed in parallel after the contract freeze. E7 cannot begin until the
precedence, exact issue slices, and fallback rules are fixed; E9 cannot begin until public hooks
and asset ownership are stable. Any failed browser or explicitness probe returns to E0 with an
amended contract rather than weakening a gate in place.

## Pull-request sequence

1. contract-only schemas, refined scope, and issue disposition matrix;
2. asset graph and application layer;
3. hook and token manifests;
4. diagnostics and source maps;
5. ejection and upgrade fixtures;
6. the four open-issue verticals;
7. fleet migrations and examples;
8. hardening, docs, and release evidence.

Every pull request names its RFC, implementation workstream, public contract, gate IDs, and
retained artifact paths. No release or issue closure is inferred from a passing unit test alone.
