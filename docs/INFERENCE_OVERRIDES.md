# Inference explain / override inventory

Phase 0.4 surfaces plus phase 0.5 data/cache/ColorMode inferences.

| Inference | Explanation | Override |
|---|---|---|
| HTMX target/swap on routes | Explorer routes panel + CLI `preview` explanations | Explicit `hx-target` / `hx-swap` on components |
| Style symbol scoping | Explorer component panel + CLI `inspect` style_symbols | `STYLE_COMPONENT_ID` / ejected local CSS |
| Asset fingerprint URLs | Build manifest + Explorer assets section | Rebuild / custom `assets_url_prefix` |
| Production compile deny | `HED-BUILD-0004` diagnostics / STATUS | `force_runtime_compile` for `hedron build` only |
| Explorer mount mode | Settings panel + docs | `Hedron(explorer=...)` |
| CSRF cookie reuse | Security findings panel | N/A (security default) |
| Plugin contributions | Packages panel + `audit-components` | `[tool.hedron].plugins` filter |
| `Auto()` renderer selection | Explorer `/auto` panel + `get_last_auto_decision` | Explicit `as_=` / `register_renderer` |
| Cache scope rejection | Explorer `/cache` traces (`reject` events) | Provide `vary_on` for user/tenant/session; avoid user kwargs under `public` |
| ColorMode resolution | Cookie/session preference + `data-theme` | Explicit `ColorMode.LIGHT` / `DARK` / `SYSTEM` |
| DataEditor writable fields | Column metadata + `filter_writable_changes` | Explicit `writable_fields` / `read_only` / `hidden` / `allow_deletes` |
| Sync vs async DataEditorSource | Construction requires `page=` for async `fetch` | Await `fetch` then pass `page=`; use `apply_changes_async` |
