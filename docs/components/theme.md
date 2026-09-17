# Theme

Folio is the theme used when no theme is specified. It combines warm paper
surfaces, deep teal accents, serif headings, and compact, flat panels, with a
charcoal dark palette.

Choose a built-in theme in your app:

```python
app = Hedron()                 # Folio
app = Hedron(theme="classic")  # Original blue design
app = Hedron(theme="aurora")   # Violet palette and luminous background
```

For production builds, use the same name in `[tool.hedron]`:

```toml
[tool.hedron]
theme = "classic"
```

The old name `"default"` remains a compatibility alias for Classic. Existing
explicit configurations keep their appearance; apps that omit the theme use
Folio. Python theme factories are `folio_theme()`, `classic_theme()`, and
`aurora_theme()`; `default_theme()` remains the legacy Classic factory.

Folio has an independent accent option. Green is the default; choose `blue`,
`violet`, `amber`, `rose`, or a three- or six-digit hex color:

```python
app = Hedron()                                # Folio, green accent
app = Hedron(theme="folio", accent="blue")
app = Hedron(accent="#a34463")

import edron as ed
app = ed.App(title="My app", accent="violet")
```

The accent coordinates controls, links, focus rings, selection, and chart
highlights in both color modes. Paper and charcoal surfaces, typography,
geometry, and success/warning/error colors remain consistent. Custom hex
colors serve as seeds; Folio adjusts their brightness for readable contrast.
The `accent` app option applies to Folio only.

In Explorer's **Theme Lab**, select Folio in either theme dropdown to reveal
its accent choices. Green is selected initially. Choose an accent and apply
the form to inspect its resolved tokens and export the same selection as JSON.

For a production build, match the app's accent in its configuration:

```toml
[tool.hedron]
theme = "folio"
accent = "blue"
```

Portable theme authoring also accepts the option:

```python
from hedron_core import folio_theme

app = Hedron(theme=folio_theme(accent="rose"))
```

User-facing theme and color-mode preference controls:

- [`ThemePicker`](theme-picker.md) — Render an accessible no-JavaScript form for an allowlisted theme and color-mode preference.
- [`ColorModeToggle`](color-mode-toggle.md) — Let users choose light, dark, or system color preference.
