# Inference explain / override inventory (phase 0.4)

| Inference | Explanation | Override |
|---|---|---|
| HTMX target/swap on routes | Explorer routes panel + CLI `preview` explanations | Explicit `hx-target` / `hx-swap` on components |
| Style symbol scoping | Explorer component panel + CLI `inspect` style_symbols | `STYLE_COMPONENT_ID` / ejected local CSS |
| Asset fingerprint URLs | Build manifest + Explorer assets section | Rebuild / custom `assets_url_prefix` |
| Production compile deny | `HED-BUILD-0004` diagnostics / STATUS | `force_runtime_compile` for `hedron build` only |
| Explorer mount mode | Settings panel + docs | `Hedron(explorer=...)` |
| CSRF cookie reuse | Security findings panel | N/A (security default) |
| Plugin contributions | Packages panel + `audit-components` | `[tool.hedron].plugins` filter |
