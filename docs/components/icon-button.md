---
title: IconButton
description: Create a compact native button with a required accessible label.
---

# `IconButton`

Create a compact native button with a required accessible label.

| | |
|---|---|
| Import | `from hedron import IconButton` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="IconButton"><div class="hdc-stage"><button class="hdc-icon-button" type="button" aria-label="Delete report" data-hdc-action="count"><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M6.5 3.5h7M8 3.5V2h4v1.5M5 5.5h10l-.6 11H5.6L5 5.5Zm3 2v6m4-6v6"/></svg></button><p class="hdc-muted" data-hdc-status>Accessible name: Delete report</p></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import IconButton

component = IconButton('Delete report', icon='⌫')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

The icon string is rendered inside an aria-hidden span while `label` supplies the button's accessible name. Both values are escaped; this component does not resolve registered SVG names automatically.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
IconButton(label, *, icon, type='button', disabled=False)
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Required accessible name. |
| `icon` | `str` | Escaped visible icon or symbol, hidden from assistive technology. |
| `type` | `button | submit | reset` | Native behavior. |
| `disabled` | `bool` | Prevent activation. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `IconButton` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Make the hit target large enough and keep a tooltip supplementary—the label must exist without hover.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Do not pass SVG markup as the icon string; use the reviewed icon registry in a custom control when a trusted SVG is required.
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
