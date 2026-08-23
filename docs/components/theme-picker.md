---
title: ThemePicker
description: Render an accessible no-JavaScript form for an allowlisted theme and color-mode preference.
---

# `ThemePicker`

Render an accessible no-JavaScript form for an allowlisted theme and color-mode preference.

| | |
|---|---|
| Import | `from hedron import ThemePicker` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ThemePicker"><div class="hdc-stage"><div class="hdc-result"><strong>ThemePicker</strong><span>Render an accessible no-JavaScript form for an allowlisted theme and color-mode preference.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ThemePicker

component = ThemePicker(selected=ThemePreference(theme='aurora', color_mode='dark'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

ThemePicker emits a native POST form. The application owns persistence and authorization; optional client boot helpers are bounded and do not replace the server-rendered selection.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
ThemePicker(*, themes: 'tuple[str, ...]' = ('default', 'aurora'), color_modes: 'tuple[ColorMode, ...]' = ('system', 'light', 'dark'), selected: 'ThemePreference | None' = None, action: 'SafeUrl | str' = '/preferences/theme', csrf_token: 'str | None' = None, compact: 'bool' = False, id: 'str | None' = None, class_: 'str | None' = None, mark: 'str | None' = None, **kwargs: 'Any') -> 'None'
```

| Parameter | Type | Meaning |
|---|---|---|
| `themes` | `tuple[str, ...]` | Constructor parameter. Default: `('default', 'aurora')`. |
| `color_modes` | `tuple[ColorMode, ...]` | Constructor parameter. Default: `('system', 'light', 'dark')`. |
| `selected` | `ThemePreference | None` | Constructor parameter. Default: `None`. |
| `action` | `SafeUrl | str` | Constructor parameter. Default: `'/preferences/theme'`. |
| `csrf_token` | `str | None` | Constructor parameter. Default: `None`. |
| `compact` | `bool` | Constructor parameter. Default: `False`. |
| `id` | `str | None` | Optional DOM `id`. Default: `None`. |
| `class_` | `str | None` | Optional CSS class string (`class` in HTML). Default: `None`. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). Default: `None`. |

## Composition and backend behavior

Keep `ThemePicker` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`ThemePicker` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep the labels, native submit path, and selected server state available when JavaScript is disabled.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not pass unregistered theme names, remote actions, CSS, or identity-bearing preference values into the picker.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
