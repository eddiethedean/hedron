---
title: Title
description: Set the browser-tab and history-entry title.
---

# `Title`

Set the browser-tab and history-entry title.

| | |
|---|---|
| Import | `from hedron import Title` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Title"><div class="hdc-stage"><div class="hdc-browser"><div><i></i><i></i><i></i><span>Billing · Acme</span></div><main><dl class="hdc-description"><dt>title</dt><dd>Billing · Acme</dd><dt>description</dt><dd>Manage billing</dd></dl></main></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Title

component = Title('Billing · Acme')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

`Title` emits exactly one `<title>` element. Put it in a `Head`, or use the simpler `title=` argument on `Page`.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Title(text=None, *, children=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `text` | `str | None` | Preferred title text. |
| `children` | `str | None` | Alternative authoring form when `text` is omitted. |

## Composition and backend behavior

Keep `Title` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Use a concise, unique title whose most specific information comes first.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- This is document metadata, not a visible heading. Pair it with a page `Heading(level=1)`.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
