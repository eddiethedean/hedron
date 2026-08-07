# Changelog

## [Unreleased]

### Fixed

- Expand docs sim includes *after* Markdown so `__HEDRON_SIM_UTC__` tokens are not
  turned into `<strong>` (which broke timestamp swaps on Read the Docs).
- Neutralize *all* progressive `a[href]` / `form[action]` targets inside sim islands
  (not only `hx-*` anchors), and block leftover navigations/submits in capture phase
  so demo clicks cannot hit Read the Docs / Cloudflare WAF paths.
- Accept legacy markdown-mangled `<strong>HEDRON_SIM_UTC</strong>` tokens in the JS shim.
- Intercept demo `hx-*` clicks/submits in the capture phase so MkDocs Material
  instant navigation cannot follow progressive-enhancement `href`s out of the docs.
- Rewrite demo anchor `href`s to `#` at boot (original kept in `data-hedron-sim-href`)
  because Material registers its capture listener before extra scripts.

### Added

- Docs theme tokens for Material `slate` / `default` schemes.
- Bounded `hx-trigger="load"` and `hx-confirm` support in the JS shim.
- PAGE / FRAGMENT mode-toggle helper for core-concepts demos.

## [0.1.0] — 2026-08-07

### Added

- Initial Alpha: `SimApp`, `embed_demo`, `sim_utc` / `sim_form` placeholders, and a browser HTMX shim.
- Route extras: email `validate` + `variants`, and `sequence` responses for poll-style demos.
- Docs guides and HTMX-native component galleries migrated onto generated `<!-- hedron-sim:… -->` islands.
