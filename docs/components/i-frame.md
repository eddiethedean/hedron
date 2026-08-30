---
title: IFrame
description: Policy-bounded sandboxed iframe with SafeUrl source.
---

# `IFrame`

Policy-bounded sandboxed iframe with SafeUrl source.

| | |
|---|---|
| Import | `from hedron import IFrame` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="IFrame"><div class="hdc-stage"><div class="hdc-result"><strong>IFrame</strong><span>Policy-bounded sandboxed iframe with SafeUrl source.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import IFrame
component = IFrame('/embed', title='Embed')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
IFrame(src: 'SafeUrl | str', *, title: 'str', sandbox: 'str' = '', allow: 'str | None' = None, referrerpolicy: 'str' = 'no-referrer', width: 'str | int | None' = None, height: 'str | int | None' = None, allow_remote: 'bool' = False, class_: 'str | None' = None, mark: 'str | None' = None, **kwargs: 'object') -> 'None'
```

| Parameter | Type | Meaning |
|---|---|---|
| `src` | `SafeUrl | str` | Media or document URL (`SafeUrl` preferred for untrusted input). |
| `title` | `str` | Accessible title (document, iframe, dialog, or media). |
| `sandbox` | `str` | IFrame `sandbox` token string (empty = fully sandboxed). Default: `''`. |
| `allow` | `str | None` | Optional iframe `allow` feature policy string. Default: `None`. |
| `referrerpolicy` | `str` | IFrame referrer policy. Default: `'no-referrer'`. |
| `width` | `str | int | None` | Optional width hint (CSS length or pixels). Default: `None`. |
| `height` | `str | int | None` | Optional height hint (CSS length or pixels). Default: `None`. |
| `allow_remote` | `bool` | Allow remote iframe sources when True. Default: `False`. |
| `class_` | `str | None` | Optional CSS class string (`class` in HTML). Default: `None`. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). Default: `None`. |

## Composition and backend behavior

Keep `IFrame` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`IFrame` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keyboard and screen-reader operable; no-JS fallback required where interactive.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not treat client-only hints (geolocation, browser storage) as authorization.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
