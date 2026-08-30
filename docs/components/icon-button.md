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

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import IconButton
component = IconButton('Delete report', icon='⌫')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The icon string is rendered inside an aria-hidden span while `label` supplies the button's accessible name. Both values are escaped; this component does not resolve registered SVG names automatically.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
IconButton(label, *, icon, type='button', disabled=False)
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Required accessible name. |
| `icon` | `str` | Escaped visible icon or symbol, hidden from assistive technology. |
| `type` | `button | submit | reset` | Native behavior. |
| `disabled` | `bool` | Prevent activation. |

## Composition and backend behavior

Keep `IconButton` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`IconButton` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

## Accessibility

Make the hit target large enough and keep a tooltip supplementary—the label must exist without hover.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not pass SVG markup as the icon string; use the reviewed icon registry in a custom control when a trusted SVG is required.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
