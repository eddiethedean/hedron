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

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import ColorMode, ColorModeToggle

component = ColorModeToggle(preference=ColorMode.SYSTEM, action='/preferences/color', csrf_token=csrf_token)
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

The component renders a labelled native select and Apply button with a collision-free relationship, so more than one settings surface can contain a toggle safely. The server can persist a cookie or session preference, while `color_mode_script()` resolves system preference early enough to avoid a flash.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

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

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `ColorModeToggle` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Every theme must meet contrast and focus requirements in all three modes; system mode must respond to user-agent preference.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Treat persistence as a state-changing POST and validate CSRF; do not hide the control based on JavaScript availability.
- Do not copy docs-preview JavaScript into an application server; demos simulate HTMX locally.
- Choose components for semantics first, then theme them.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

For interactive flows, assert method, URL, headers, fragment body, and status with a framework test client. Add a browser test when keyboard or HTMX swap behavior is material.

[All component demos](index.md) · [Built-in API baseline](../api/BUILT_INS.md) · [Testing UI](../guides/testing.md) · [Forms and actions](../guides/forms-and-actions.md)
