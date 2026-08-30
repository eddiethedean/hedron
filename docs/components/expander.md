---
title: Expander
description: Reveal optional content with native details/summary behavior.
---

# `Expander`

Reveal optional content with native details/summary behavior.

| | |
|---|---|
| Import | `from hedron import Expander` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Expander"><div class="hdc-stage"><details class="hdc-expander"><summary>Advanced settings</summary><p>Configure retry and timeout behavior.</p></details></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Expander, Text
component = Expander('Advanced settings', Text('Configure retry and timeout behavior.'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The native details element supplies keyboard and disclosure state without custom JavaScript. Content remains in the document and participates in search.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
Expander(title, *nodes, children=None, open=False, id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `title` | `str` | Visible summary label. |
| `nodes` | `NodeLike` | Positional disclosure content. |
| `children` | `NodeLike | sequence | None` | Keyword disclosure content; combines with positional nodes. |
| `open` | `bool` | Initial expanded state. |
| `id` | `str | None` | Stable ID for links, tests, or replacement. |
| `class_` | `str | None` | Application class appended to `hedron-expander`. |

## Composition and backend behavior

Keep `Expander` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Expander` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Use a summary that describes the hidden content, not a generic “More”.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not hide required fields or primary instructions in a collapsed expander.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
