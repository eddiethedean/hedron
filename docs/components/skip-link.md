---
title: SkipLink
description: Keyboard bypass link to the shell main panel.
---

# `SkipLink`

Keyboard bypass link to the shell main panel.

| | |
|---|---|
| Import | `from hedron import SkipLink` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="SkipLink"><div class="hdc-stage"><p><a class="hdc-chip" href="#component-demo-result">Skip to main content</a><span class="hdc-muted">Focusable bypass to the main panel.</span></p></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import SkipLink

component = SkipLink(target='#main-panel')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

SkipLink is styled by the default theme so authors never write CSS for the focusable bypass control.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
SkipLink(target='#main-panel', *, label='Skip to main content', id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `target` | `SafeUrl | str` | Same-document fragment such as `#main-panel`. |
| `label` | `str` | Discernible link text for assistive technology. |

## Composition and backend behavior

Keep `SkipLink` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`SkipLink` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Place SkipLink as the first focusable element in the document and point it at AppShell's panel id.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use an external URL or an empty fragment as the target.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
