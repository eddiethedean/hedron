---
title: Auto
description: Choose an inspectable built-in renderer for a Python value.
---

# `Auto`

Choose an inspectable built-in renderer for a Python value.

| | |
|---|---|
| Import | `from hedron import Auto` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Auto"><div class="hdc-stage"><dl class="hdc-description"><dt>Region</dt><dd>iad</dd><dt>Healthy</dt><dd><span class="hdc-badge">True</span></dd><dt>Replicas</dt><dd>3</dd></dl></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Auto

component = Auto({'region': 'iad', 'healthy': True})
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Auto applies bounded data intelligence and records why a renderer was selected. Mappings become description lists, sequences can become lists or tables, and explicit `as_` overrides ambiguity.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Auto(value=None, *, as_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `value` | `Any` | Value to inspect and render. |
| `as_` | `str | None` | Explicit renderer override. |

## Composition and backend behavior

Keep `Auto` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Auto` renders data the server already prepared. Keep queries, authorization, and redaction on the route or data source — do not treat the component as a place for side effects.

## Accessibility

Inspect generated hierarchy and table labeling; automatic structure cannot infer every domain meaning.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not pass unbounded, secret-bearing, or adversarial objects without limits and redaction.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
