---
title: Loading
description: Show a polite busy status while a request or deferred component is pending.
---

# `Loading`

Show a polite busy status while a request or deferred component is pending.

| | |
|---|---|
| Import | `from hedron import Loading` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Loading"><div class="hdc-stage"><div class="hdc-loading" role="status" aria-live="polite" aria-busy="true"><i></i><span>Loading account activity…</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Loading

component = Loading('Loading account activity…')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Loading emits a status region with polite live and busy semantics. It is frequently used as Lazy or Poll content and as an HTMX indicator.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Loading(message='Loading…')
```

| Parameter | Type | Meaning |
|---|---|---|
| `message` | `str` | Specific progress message. |

## Composition and backend behavior

Keep `Loading` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Name the operation when several requests could be active; remove or replace the status when work completes.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use Loading for indeterminate work that has failed—render ErrorState.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
