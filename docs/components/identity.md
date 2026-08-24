---
title: Identity
description: Compose avatar plus primary/secondary identity text.
---

# `Identity`

Compose avatar plus primary/secondary identity text.

| | |
|---|---|
| Import | `from hedron import Identity` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Identity"><div class="hdc-stage"><div class="hdc-inline"><span class="hdc-badge" aria-label="Ada Lovelace">AL</span><span><b>Ada Lovelace</b><small class="hdc-muted">Admin</small></span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Identity

component = Identity('Ada Lovelace', detail='Admin', size='md')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Identity is the typed person/entity strip used by chrome and resource rows. The default theme
keeps the name and detail in a constrained two-line text stack, so long names do not concatenate
with the secondary detail or push the surrounding chrome out of bounds.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Identity(name, *, detail=None, src=None, size=None, appearance=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Primary identity label. |
| `detail` | `str | None` | Secondary line such as role or email. |
| `src` | `SafeUrl | str | None` | Optional avatar image. |
| `size / appearance` | `token | None` | Presentation tokens shared with Avatar. |

## Composition and backend behavior

Keep `Identity` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Identity` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep detail text supplementary; the name remains primary.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not nest a second interactive avatar link inside Identity.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
