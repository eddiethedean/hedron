# Chrome with zero application CSS

Reference fixture for [#528](https://github.com/eddiethedean/hedron/issues/528):
a Data Mover-class front end whose entire appearance is configured in Python.

**Zero-application-CSS intent.** This directory contains no `.css` file, no
`<style>` block, and no `style=` attribute. Every visual decision comes from a
`Theme` (tokens, palette, density, shape, nav width, elevation) plus Hedron's
built-in chrome components, and Hedron ships the stylesheet that renders them.
There is no CSS escape hatch on this path — if something cannot be expressed
through a theme field or a built-in prop, that is a framework gap, not an
application one.

```bash
uv run uvicorn --app-dir examples/chrome-zero-css app:app --reload
hedron style check --zero-app-css examples/chrome-zero-css
hedron theme check
```

`style check` exits non-zero if a stylesheet or inline style block ever appears
here, so the claim above is enforced rather than asserted.

## Surfaces

| Path | Surface | Chrome exercised |
|---|---|---|
| `/` | Pipelines | `PageHeader`, `SplitView`, `ProcessFlow`/`FlowStep`, `Table` with `TableColumn`, `StateView(kind="permission")` |
| `/sign-in` | Sign in | `FormGrid` with a breakpoint column map, `ActionGroup`, `StateView(kind="offline")` |
| `/settings` | Settings | `DescriptionList` columns/density, responsive `FormGrid` |
| `/team` | Team | `Table` density, `Button(leading_icon=...)` |
| `/audit` | Audit log | `StateView(kind="empty")`, `Icon`, `Typography` roles |

Every page is wrapped by `AppShell` chrome slots (`banner`, `brand`,
`env_badge`, `account`, `nav_groups`, `nav_footer`, `app_footer`,
`content_width`) and starts with a `SkipLink` to the main panel. The account
area holds a `RequestIndicator` that HTMX controls can target with
`indicator="#global-indicator"`.

## Design system in Python

`app.py` compiles one seed color into an accessible token set and derives the
application theme from the built-in default:

```python
BRAND = compile_palette("#2f6fed")

THEME = default_theme().extend(
    "datamover",
    tokens=BRAND,
    palette={"brand.seed": "#2f6fed"},
    density="comfortable",
    shape={"radius": "0.65rem"},
    nav_width="16rem",
    elevation={"raised": "0 1px 2px rgb(15 23 42 / 8%)"},
)
```

`compile_palette` guarantees WCAG AA for its text pairs by construction, and
`contrast_diagnostics(THEME)` (also run by `hedron theme check`) reports any pair
that falls below target. `extend` records `parent="default"`, so the derived
theme restates only what it changes.

Design-system fields reach CSS as custom properties (`--hedron-nav-width`,
`--hedron-shape-radius`, `--hedron-palette-brand-seed`, the overlay/stacking
tokens, and `--hedron-theme-name` / `--hedron-theme-parent`).
`emit_theme_css` writes them to both `:root` and
`[data-hedron-theme="datamover"]`, so a scoped subtree can opt into the theme;
this page opts in document-wide with `Page(..., data_hedron_theme=THEME.name)`.
Run `hedron build` to emit the compiled token stylesheet for production.
