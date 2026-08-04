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

<section class="hedron-component-demo" data-hedron-component-demo="RefreshButton"><div class="hdc-stage"><div class="hdc-result" id="status-card" aria-live="polite"><strong>Service healthy</strong><span>Checked just now</span></div><button class="hdc-button" type="button" data-hdc-action="refresh">Refresh status</button></div><div class="hdc-request" data-hdc-request hidden><span>Simulated HTMX</span><code>GET /fragment → 200</code></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import RefreshButton

component = RefreshButton('Refresh status', href='/status', target='#status-card', swap='innerHTML')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

The rendered native button receives `hx-get`, target, and swap metadata. A ComponentRef also carries its method and typed query parameters. The docs demo intercepts the request and replaces the target locally.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

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

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `RefreshButton` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Announce refreshed content through a status or live region and keep keyboard focus stable unless the task changes.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Do not accept user-controlled target selectors or refresh destructive endpoints with GET.
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
