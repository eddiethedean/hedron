# What’s new in 0.19


!!! note "Current train is 0.60"

    Pin `hedron>=0.53.0,<0.54` for new apps (checkout tip; current PyPI pin `>=0.60.0,<0.61`). The pin below is historical for this train only.
    See [What’s new in 0.51](whats-new-0.51.md).

**Published as `v0.19.0`** (2026-08-07). Current published train is **0.60.x** (`v0.60.0`).
Historical installs for this phase used a 0.19 upper-bound pin; the current pin is
`hedron>=0.60.0,<0.61`.

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
  remains owned by **0.21** (D-050)

## See also

[Upgrade](upgrade.md) · [What’s ready](whats-ready.md) · [What’s new in 0.20](whats-new-0.20.md) ·
[STATUS](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md)
