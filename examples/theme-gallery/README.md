# Theme gallery

Visual QA fixture for Hedron's built-in themes. Nine screens compose dashboards,
settings, orders, support, button states, forms, surfaces and workflows, identity
and content, and media. Switch between Folio, Classic, and Aurora while forcing either
palette independently of the operating-system preference.

Try the same app's button matrix in the backend-free
[docs Component Explorer](https://hedron.readthedocs.io/en/latest/guides/component-explorer/),
or compare themes and inspect tokens in the
[Styles Explorer](https://hedron.readthedocs.io/en/latest/guides/styles-explorer/).

```bash
uv run uvicorn --app-dir examples/theme-gallery app:app --reload
```

Open <http://127.0.0.1:8000/> and use the Folio, Classic, Aurora, Light, and Dark controls
in the header.
Folio, the automatic theme, uses warm paper surfaces, ink text, deep teal accents, serif display
headings, and compact corners. Its dark palette uses charcoal and pale mint.
Surfaces are flat and bordered; shadows are reserved for overlays. Aurora
retains its violet palette and luminous background. Set `theme="classic"` to
keep the original blue theme, or `theme="folio"` to select Folio explicitly. Existing `theme="default"` configurations remain an
alias for Classic.

The gallery intentionally uses Hedron built-ins without an application
stylesheet, so visual regressions point back to the shared theme.

The component screen covers all six button appearances, all four emphases,
disabled states, sizes, icons, and feedback tones. Forms include native date,
time, file, and multiple-selection controls. The other screens exercise chart
surfaces, tables, disclosures, dialogs, popovers, chat, workflow states, resource
lists, model inspectors, image galleries, carousels, and capture controls. Map
content uses its local fallback; device permissions are requested only when a
user activates a capture control.

Run the browser checks after installing the Playwright browsers:

```bash
HEDRON_BROWSER=1 uv run pytest tests/browser/test_builtin_theme_gallery.py -n 0
```

The suite checks all three themes and palettes at desktop and phone widths in
Chromium, Firefox, and WebKit. It checks rendered text contrast against solid
and translucent fallback surfaces, page overflow, button hover colors, sizes,
and disabled states across complete, emitted-theme, and selected-bundle CSS.
Gradient backgrounds and the overall compositions also require visual review.
