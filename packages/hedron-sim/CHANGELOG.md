# Changelog

## [0.42.0] — 2026-08-14

### Added
- Phase 0.42 production-grade Web Component platform graduation (D-070).

### Changed
- Coordinated train tip `0.42.0` (in-tree cut; tag/PyPI deferred).

## [0.1.0] — 2026-08-07

### Fixed

- Store route tables in ``<template data-hedron-sim-routes>`` instead of
  ``<script type="application/json">``. MkDocs Material ``navigation.instant``
  strips ``<script>`` nodes from fetched pages, which left demo buttons dead until
  a hard refresh.
- Escape ``__HEDRON_SIM_FORM:*__`` token substitutions with ``escapeHtml`` so invite
  demos cannot inject markup via form fields.
- Boot on ``DOMContentLoaded`` even when Material's ``document$`` is present, and
  handle Text-node click targets / form-inherited ``hx-*`` on submit buttons.
- Expand docs sim includes *after* Markdown so `__HEDRON_SIM_UTC__` tokens are not
  turned into `<strong>` (which broke timestamp swaps on Read the Docs).
- Neutralize *all* progressive `a[href]` / `form[action]` targets inside sim islands
  (not only `hx-*` anchors), and block leftover navigations/submits in capture phase
  so demo clicks cannot hit Read the Docs / Cloudflare WAF paths.
- Force `action="#"` on every sim `<form>` (even when `action` was omitted) and always
  `preventDefault` sim submits before route init, so `method="post"` forms cannot POST
  the current docs URL.
- Re-check boot invariants (no root/http `href`, forms `action="#"`) and record repairs
  on `data-hedron-sim-blocked` for tests.
- While a sim click/submit is in flight, reject `fetch` / `XMLHttpRequest` so a
  regression cannot hit Read the Docs network paths (MkDocs/RTD traffic outside that
  window is unaffected).
- Accept legacy markdown-mangled `<strong>HEDRON_SIM_UTC</strong>` tokens in the JS shim.
- Intercept demo `hx-*` clicks/submits in the capture phase so MkDocs Material
  instant navigation cannot follow progressive-enhancement `href`s out of the docs.
- Rewrite demo anchor `href`s to `#` at boot (original kept in `data-hedron-sim-href`)
  because Material registers its capture listener before extra scripts.

### Added

- Route ``validate="credentials"`` + ``variants`` for docs auth demos (``ada`` /
  ``correct-horse``).
- Route extras ``accumulate="field"`` + ``empty=...`` and ``list_remove=True`` so list
  demos (CRUD notes) append and delete items client-side instead of replacing one row.
- Layout styles for ``OobHost`` rows so the host id and caption are not jammed together.
- Docs theme tokens for Material `slate` / `default` schemes.
- Bounded `hx-trigger="load"` and `hx-confirm` support in the JS shim.
- PAGE / FRAGMENT mode-toggle helper for core-concepts demos.


### Added

- Initial Alpha: `SimApp`, `embed_demo`, `sim_utc` / `sim_form` placeholders, and a browser HTMX shim.
- Route extras: email `validate` + `variants`, and `sequence` responses for poll-style demos.
- Docs guides and HTMX-native component galleries migrated onto generated `<!-- hedron-sim:… -->` islands.
