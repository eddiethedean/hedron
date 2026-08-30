---
title: Head
description: Compose explicit document-head children when building lower-level document output.
---

# `Head`

Compose explicit document-head children when building lower-level document output.

| | |
|---|---|
| Import | `from hedron import Head` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Head"><div class="hdc-stage"><div class="hdc-browser"><div><i></i><i></i><i></i><span>Billing · Acme</span></div><main><dl class="hdc-description"><dt>title</dt><dd>Billing · Acme</dd><dt>description</dt><dd>Manage billing</dd></dl></main></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Head, Title, html
component = Head(Title('Reports'), html.meta(name='description', content='Weekly reports'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

`Head` renders a semantic `<head>` node. Most applications should prefer `Page(title=..., head=...)`, while `Head` is useful to libraries and tests that need explicit document composition.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
Head(*nodes, children=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional head-safe nodes such as `Title` and `html.meta`. |
| `children` | `NodeLike | sequence | None` | Keyword alternative; combines with positional nodes. |

## Composition and backend behavior

Keep `Head` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Head` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Give every page a useful title; metadata has no visible fallback for assistive-technology users.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Never place user-supplied raw markup in the head. Use validated native elements and `TrustedHtml` only at a reviewed trust boundary.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
