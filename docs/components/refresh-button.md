---
title: RefreshButton
description: Refresh a target component through a typed reference or safe URL.
---

# `RefreshButton`

Refresh a target component through a typed reference or safe URL.

| | |
|---|---|
| Import | `from hedron import RefreshButton` |
| Distribution | `hedron` |
| Backend activity | On activation |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<!-- hedron-sim:component-refresh -->

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import RefreshButton

component = RefreshButton('Refresh status', href='/status', target='#status-card', swap='innerHTML')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The rendered native button receives `hx-get`, target, and swap metadata. A ComponentRef also carries its method and typed query parameters. The docs demo intercepts the request and replaces the target locally.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
RefreshButton(label='Refresh', *, ref=None, href=None, target=None, swap='outerHTML')
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Visible command. |
| `ref` | `ComponentRef | None` | Preferred typed route reference. |
| `href` | `str | None` | Fallback GET URL. |
| `target` | `safe CSS selector | None` | Element to update. |
| `swap` | `str` | HTMX swap strategy. |

## Composition and backend behavior

Keep `RefreshButton` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Announce refreshed content through a status or live region and keep keyboard focus stable unless the task changes.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not accept user-controlled target selectors or refresh destructive endpoints with GET.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
