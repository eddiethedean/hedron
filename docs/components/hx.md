---
title: Hx
description: First-class HTMX attribute bundle for Form (validated selectors and swap).
---

# `Hx`

First-class HTMX attribute bundle for Form (validated selectors and swap).

| | |
|---|---|
| Import | `from hedron import Hx` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Hx"><div class="hdc-stage"><div class="hdc-result"><strong>Hx</strong><span>First-class HTMX attribute bundle for Form (validated selectors and swap).</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Form, Hx

component = Form(..., hx=Hx(target='#region', swap='outerHTML', indicator='#busy'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Prefer `hx=Hx(...)` over raw `hx-*` kwargs so unsafe selectors cannot slip through.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Hx(*, target=None, swap='outerHTML', select=None, indicator=None, trigger=None, include=None, validate=None, ...)
```

| Parameter | Type | Meaning |
|---|---|---|
| `target` | `str | None` | hx-target selector (must pass safe_css_selector). |
| `swap` | `str` | hx-swap value (must pass safe_hx_swap). |
| `select` | `str | None` | hx-select selector. |
| `indicator` | `str | None` | hx-indicator selector. |
| `trigger` | `str | None` | `hx-trigger`. |
| `include` | `str | None` | `hx-include`. |
| `validate` | `str | None` | `"native"` compiles `hx-validate="true"`. |
| `vals` / `headers` | `str | None` | JSON only; `js:` expressions are rejected. |

## Composition and backend behavior

Keep `Hx` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Hx` participates in interaction markup. Pair it with an explicit `@action` / `@component` POST (and CSRF) when the control mutates state.

## Accessibility

Selector validation is the security boundary; do not bypass with stringly kwargs.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Raw kwargs that survive after Hx merge are still validated.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
