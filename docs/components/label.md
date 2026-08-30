---
title: Label
description: Associate visible text with a form control ID.
---

# `Label`

Associate visible text with a form control ID.

| | |
|---|---|
| Import | `from hedron import Label` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Label"><div class="hdc-stage"><div class="hdc-form"><label for="demo-search">Search projects</label><input id="demo-search" type="search" placeholder="Try typing…"></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Label

component = Label('Search projects', for_='project-search')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

`for_` uses the Python-safe spelling but serializes to the native `for` attribute. Prefer FormField when you also need help, required, or error binding.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Label(text, *, for_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `text` | `str` | Visible label. |
| `for_` | `str | None` | Target control ID; renders as `for`. |

## Composition and backend behavior

Keep `Label` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Label` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

## Accessibility

Labels should state what information to enter, not merely repeat a placeholder.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- A placeholder is not a replacement for Label because it disappears during entry.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
