---
title: NavLink
description: Alias of HtmxLink for navigation lists and AppShell side nav.
---

# `NavLink`

Alias of HtmxLink for navigation lists and AppShell side nav.

| | |
|---|---|
| Import | `from hedron import NavLink` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<!-- hedron-sim:component-nav-link -->

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import NavLink

component = NavLink('Home', '/', hx_get='/', hx_target='#main-panel', active=True)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

NavLink is an intentional DX alias of HtmxLink so shell navigation reads clearly under Nav / AppShell. Behavior, allowlists, and SafeUrl policy are identical.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
NavLink(label, href, *, hx_get=None, hx_target=None, hx_swap=None, active=False, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `…` | `same as HtmxLink` | NavLink is the same component class as HtmxLink. |

## Composition and backend behavior

Keep `NavLink` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Use NavLink in primary navigation; use Link for ordinary content links without HTMX shell targets.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not register both names as separate plugins—only one component class exists.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
