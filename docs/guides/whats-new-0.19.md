# What’s new in 0.19

**Implemented on `main` as `0.19.0`** (2026-08-07); superseded by **0.20 Ready-to-cut** before
a public `v0.19.0` tag. Last published PyPI/git = `v0.18.0`. Historical pin for this phase
was `hedron>=0.19.0,<0.20`; current train is `hedron>=0.20.0,<0.21`.

Phase 0.19 delivers accessibility engineering and inclusive authoring without automatic
WCAG / legal / VPAT claims (D-050).

## Highlights

- Machine-readable `AccessibilityContract` catalog (curated reviewed set + registry stubs) and
  versioned WCAG 2.2 A/AA + WAI-ARIA 1.2 profile (`hedron_core.a11y`)
- Explorer accessibility review workspace (profile, reviewed/stub contracts, structure outline,
  review-mode checklist); ATAG-oriented `inspect` / `eject` metadata with curated contracts
- Landmark components as real types with safe attrs (no hostile `role` overrides); allowlisted
  `Page(scripts=[SafeUrl…])` with `script_defer` / `script_async`
- Documented progressive-enhancement POST path (no-JS redirect / full page alongside HTMX)
- `AccessibilityScenario`, markup heuristic tree snapshots, axe → SARIF helpers
- Automated three-engine Playwright / axe AT matrix (`AT-019`); human screen-reader evaluation
  Deferred → 0.21
- Media track validation via `MediaTrackContract` on `Audio`/`Video` track maps

## Upgrade

See [Upgrade](upgrade.md) and the [0.19 acceptance checklist](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_19.md).
