---
title: Toast
description: Render a polite, transient-looking status message.
---

# `Toast`

Render a polite, transient-looking status message.

| | |
|---|---|
| Import | `from hedron import Toast` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Toast"><div class="hdc-stage"><button class="hdc-button" type="button" data-hdc-action="show-toast">Show toast</button><div class="hdc-toast" role="status" data-hdc-toast hidden><span>API key copied.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Toast

component = Toast('API key copied.', tone='success')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Toast emits a polite status region with a tone class. It does not include timing or dismissal behavior; the docs Show button simulates inserting the server-rendered toast into an application shell.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Toast(message, *, tone='info')
```

| Parameter | Type | Meaning |
|---|---|---|
| `message` | `str` | Escaped toast text. |
| `tone` | `info | success | warning | danger` | Visual token. |

## Composition and backend behavior

Keep `Toast` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

If application JavaScript removes the toast, allow enough reading time, pause any timer on hover or focus, and preserve critical messages elsewhere.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Never auto-dismiss errors that require a user decision, and do not expect a `dismissible` constructor option.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
