# What’s new in 0.19

**Ready to cut / Implemented on `main`:** `0.19.0` (2026-08-07). Last published PyPI/git =
`v0.18.0`. Pin `hedron>=0.19.0,<0.20`.

Phase 0.19 delivers accessibility engineering and inclusive authoring without automatic
WCAG / legal / VPAT claims (D-050).

## Highlights

- Machine-readable `AccessibilityContract` catalog and versioned WCAG 2.2 A/AA + WAI-ARIA 1.2
  profile (`hedron_core.a11y`)
- Explorer accessibility review workspace; ATAG-oriented `inspect` / `eject` metadata
- Landmark components as real types with safe attrs; allowlisted `Page(scripts=[SafeUrl…])`
- Documented progressive-enhancement POST path (no-JS redirect / full page alongside HTMX)
- `AccessibilityScenario`, semantic-tree snapshots, axe → SARIF helpers
- Automated three-engine Playwright / axe AT matrix (`AT-019`); human screen-reader evaluation
  Deferred → 0.21

## Upgrade

See [Upgrade](upgrade.md) and the [0.19 acceptance checklist](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_19.md).
