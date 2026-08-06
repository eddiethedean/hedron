---
title: ParameterViewer
description: Schema-oriented parameter documentation with secret redaction.
---

# `ParameterViewer`

Schema-oriented parameter documentation with secret redaction.

| | |
|---|---|
| Import | `from hedron import ParameterViewer` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ParameterViewer"><div class="hdc-stage"><div class="hdc-result"><strong>ParameterViewer</strong><span>Schema-oriented parameter documentation with secret redaction.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ParameterViewer

component = ParameterViewer({'lr': 0.01, 'api_token': 'x'}, secret_keys=('api_token',))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.18 model-demo presentation. Redact secrets before rendering.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
ParameterViewer(parameters, *, title='Parameters', secret_keys=(), class_=None, mark=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `parameters` | `Mapping[str, Any]` | Parameter map rendered as definition list entries. |
| `secret_keys` | `Sequence[str]` | Keys whose values are replaced with [redacted]. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). |

## Composition and backend behavior

Keep `ParameterViewer` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Use readable key labels; redacted values must not leak secrets into markup.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Never log or cache raw secret_keys values in examples or recorders.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
