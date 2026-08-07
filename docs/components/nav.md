---
title: Nav
description: Render the semantic `nav` landmark for a major collection of navigation links.
---

# `Nav`

Render the semantic `nav` landmark for a major collection of navigation links.

| | |
|---|---|
| Import | `from hedron import Nav` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Nav"><div class="hdc-stage"><nav class="hdc-landmark"><span>&lt;nav&gt;</span><strong>Nav content</strong><p>Render the semantic `nav` landmark for a major collection of navigation links.</p></nav></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Heading, Nav, Text

component = Nav(Heading('Documentation', level=2), Text('Guides and reference'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

`Nav` emits a native `<nav>`, preserving semantic navigation instead of using a generic div. Children may be passed individually or as one non-string sequence. Landmark helpers are real typed classes with an allowlisted attr set (`LANDMARK-019`).

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Nav(*nodes, children=None, class_=None, id=None, lang=None, dir=None, role=None, aria=None, data=None, ...)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional content belonging to this semantic region. |
| `children` | `NodeLike | sequence | None` | Keyword alternative; combines with positional nodes. |
| `class_` | `str | None` | Optional authored class name. |
| `id` | `str | None` | Stable fragment or target identifier. |
| `lang / dir / role / title / tabindex / aria / data / hidden` | `allowlisted` | Safe HTML attrs (`LANDMARK-019`); hostile roles like `presentation` / `none` are rejected. |

## Composition and backend behavior

Keep `Nav` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Give each navigation landmark a distinct accessible label when a page contains more than one.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use Nav for every group of links; reserve it for significant navigation.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
