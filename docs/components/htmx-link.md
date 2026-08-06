---
title: HtmxLink
description: Navigate with a SafeUrl href and typed HTMX attributes for in-shell swaps.
---

# `HtmxLink`

Navigate with a SafeUrl href and typed HTMX attributes for in-shell swaps.

| | |
|---|---|
| Import | `from hedron import HtmxLink` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="HtmxLink"><div class="hdc-stage"><div class="hdc-result"><strong>HtmxLink</strong><span>Navigate with a SafeUrl href and typed HTMX attributes for in-shell swaps.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import HtmxLink

component = HtmxLink('Reports', '/reports', hx_get='/reports', hx_target='#main-panel', hx_swap='innerHTML')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

HtmxLink keeps ordinary anchor navigation as the progressive-enhancement path while attaching the same HTMX allowlist used by `html.a` and ComponentRef. Use it under Nav for in-shell panel swaps.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
HtmxLink(label, href, *, hx_get=None, hx_target=None, hx_swap=None, active=False, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Visible link text. |
| `href` | `SafeUrl | str` | Validated navigation URL (also the no-JS fallback). |
| `hx_get / hx_post / …` | `str | None` | Typed HTMX request attrs from the html.a allowlist. |
| `hx_target / hx_swap` | `str | None` | Approved swap target and strategy. |
| `active` | `bool` | Optional active styling hook for current location. |
| `class_` | `str | None` | Additional CSS classes. |

## Composition and backend behavior

Keep `HtmxLink` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Prefer descriptive labels and stable region ids for `hx_target`. Keep CSRF and region authorization on the receiving action.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use HtmxLink for mutating form posts that belong on Button or Form; it is navigation-first.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
