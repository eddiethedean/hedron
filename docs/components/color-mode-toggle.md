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

component = ColorModeToggle(preference=ColorMode.SYSTEM, action='/preferences/color', csrf_token=token)
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

The component renders a labelled native select and Apply button. The server can persist a cookie or session preference, while `color_mode_script()` resolves system preference early enough to avoid a flash.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
ColorModeToggle(*, preference=ColorMode.SYSTEM, label='Color mode', action=None, csrf_token=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `preference` | `ColorMode | str` | Current light/dark/system selection. |
| `label` | `str` | Control label. |
| `action` | `str | None` | Persistence endpoint. |
| `csrf_token` | `str | None` | CSRF value for POST persistence. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `ColorModeToggle` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX routes should return only the component region being replaced and should preserve stable target IDs across success, validation, empty, loading, and error responses.

When a request can mutate data, use POST, validate CSRF, authenticate and authorize on the server, validate typed input again, and return a bounded fragment. GET interactions must remain safe and repeatable. Native links and forms should still reach a useful server response when HTMX is unavailable.

## Accessibility

Every theme must meet contrast and focus requirements in all three modes; system mode must respond to user-agent preference.

Test the demo and your application with keyboard-only input, visible focus, zoom, reduced motion, and at least one screen reader. Never make color, position, animation, or an icon the only carrier of state. Dynamic results need an appropriate status or alert and a deliberate focus strategy.

## Security and validation

Treat all request data, database content, filenames, URLs, labels, chart data, and Markdown as untrusted until the owning boundary validates it. Hedron escapes text and constrains dangerous surfaces, but it cannot decide application authorization or data exposure. Keep responses bounded, redact secrets before rendering, and use the narrowest URL and trust types available.

## Common mistakes

- Treat persistence as a state-changing POST and validate CSRF; do not hide the control based on JavaScript availability.
- Do not copy the demo's JavaScript into a server application as a substitute for an HTMX endpoint. The simulation exists only because the hosted docs have no application backend.
- Do not select components by visual appearance alone; choose the native semantics first, then theme them.

## Testing

Render the component at the boundary you intend to ship and assert behavior rather than a large, brittle snapshot:

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

For interactive use, add a framework test that sends the same method, URL, headers, and typed payload as the browser, then assert the returned fragment, status code, cache policy, and security headers. Add a browser test for keyboard behavior, focus, live announcements, and the HTMX swap lifecycle when those behaviors are material.

[All component demos](index.md) · [Built-in API baseline](../api/BUILT_INS.md) · [Testing UI](../guides/testing.md)
