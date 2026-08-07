---
title: AppShell
description: Document shell with optional side nav and a MainPanel body.
---

# `AppShell`

Document shell with optional side nav and a MainPanel body.

| | |
|---|---|
| Import | `from hedron import AppShell` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<!-- hedron-sim:component-app-shell -->

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import AppShell, Heading, Nav, NavLink

component = AppShell(Heading('Home', level=1), nav=Nav(NavLink('Home', '/'), NavLink('Reports', '/reports')), panel_id='main-panel')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

AppShell composes landmark-friendly chrome with a swappable MainPanel so full page loads and HTMX fragment swaps share one layout. Use with HtmxLink/NavLink targeting the panel id.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
AppShell(*body, *, nav=None, panel_id='main-panel', class_=None, id=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `body` | `NodeLike` | Primary content placed inside MainPanel. |
| `nav` | `NodeLike | None` | Optional side navigation (often Nav of NavLinks). |
| `panel_id` | `str` | Id forwarded to the composed MainPanel. |

## Composition and backend behavior

Keep `AppShell` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Keep global chrome outside MainPanel; put page-specific content inside the body slot.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use AppShell as a generic card or modal wrapper.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
