---
title: ColorModeToggle
description: Let users choose light, dark, or system color preference.
---

# `ColorModeToggle`

Let users choose light, dark, or system color preference.

| | |
|---|---|
| Import | `from hedron import ColorModeToggle` |
| Distribution | `hedron` |
| Backend activity | On Apply |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ColorModeToggle"><div class="hdc-stage"><form class="hdc-form hdc-theme-control" data-hdc-theme-form><label>Color mode<select data-hdc-theme><option>Light</option><option>Dark</option><option>System</option></select></label><button class="hdc-button" type="submit">Apply</button></form><div class="hdc-theme-swatch" data-hdc-theme-swatch>Preview surface</div><p role="status" data-hdc-status>Light preview selected.</p></div><div class="hdc-request" data-hdc-request hidden><span>Simulated HTMX</span><code>GET /fragment → 200</code></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ColorMode, ColorModeToggle

component = ColorModeToggle(preference=ColorMode.SYSTEM, action='/preferences/color', csrf_token=csrf_token)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The component renders a labelled native select and Apply button with a collision-free relationship, so more than one settings surface can contain a toggle safely. The server can persist a cookie or session preference, while `color_mode_script()` resolves system preference early enough to avoid a flash.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
ColorModeToggle(*, preference=ColorMode.SYSTEM, label='Color mode', id=None, action=None, csrf_token=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `preference` | `ColorMode | str` | Current light/dark/system selection. |
| `label` | `str` | Control label. |
| `id` | `str | None` | Optional select ID; generated collision-free by default. |
| `action` | `str | None` | Persistence endpoint. |
| `csrf_token` | `str | None` | CSRF value for POST persistence. |

## Composition and backend behavior

Keep `ColorModeToggle` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Every theme must meet contrast and focus requirements in all three modes; system mode must respond to user-agent preference.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Treat persistence as a state-changing POST and validate CSRF; do not hide the control based on JavaScript availability.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
