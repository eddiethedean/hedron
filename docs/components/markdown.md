---
title: Markdown
description: Render Markdown through the optional, escaped content pipeline.
---

# `Markdown`

Render Markdown through the optional, escaped content pipeline.

| | |
|---|---|
| Import | `from hedron import Markdown` |
| Distribution | `hedron[markdown]` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Markdown"><div class="hdc-stage"><article class="hdc-markdown"><h2>Release notes</h2><ul><li>Safer URLs</li><li>Faster rendering</li></ul><blockquote>Generated from Markdown source.</blockquote></article></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

Install the optional provider before importing this component:

```bash
pip install "hedron[markdown]>=0.39.0,<0.40"
```

## Basic use

```python
from hedron import Markdown

component = Markdown("## Release notes\n\n- Safer URLs\n- Faster rendering")
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Markdown uses the optional markdown dependency and returns reviewed rendered output. Raw HTML handling and sanitization are governed by the content pipeline; it is not a shortcut around TrustedHtml.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Markdown(source)
```

| Parameter | Type | Meaning |
|---|---|---|
| `source` | `str` | Markdown source text. |

## Composition and backend behavior

Keep `Markdown` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Markdown` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Authors still own heading hierarchy, meaningful link text, table captions, and image alternatives in the source.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Install `hedron[markdown]` and never assume arbitrary embedded HTML is trusted.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
