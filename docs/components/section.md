---
title: Section
description: Render the semantic `section` landmark for a thematically grouped region.
---

# `Section`

Render the semantic `section` landmark for a thematically grouped region.

| | |
|---|---|
| Import | `from hedron import Section` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Section"><div class="hdc-stage"><section class="hdc-landmark"><span>&lt;section&gt;</span><strong>Section content</strong><p>Render the semantic `section` landmark for a thematically grouped region.</p></section></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Heading, Section, Text

component = Section(Heading('Recent activity', level=2), Text('Three deployments succeeded'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

`Section` emits a native `<section>`, preserving semantic navigation instead of using a generic div. Children may be passed individually or as one non-string sequence. Landmark helpers are real typed classes with an allowlisted attr set (`LANDMARK-019`).

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Section(*nodes, children=None, class_=None, id=None, lang=None, dir=None, role=None, aria=None, data=None, ...)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional content belonging to this semantic region. |
| `children` | `NodeLike | sequence | None` | Keyword alternative; combines with positional nodes. |
| `class_` | `str | None` | Optional authored class name. |
| `id` | `str | None` | Stable fragment or target identifier. |
| `lang / dir / role / title / tabindex / aria / data / hidden` | `allowlisted` | Safe HTML attrs (`LANDMARK-019`); hostile roles like `presentation` / `none` are rejected. |

## Composition and backend behavior

Keep `Section` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Every significant section should have a heading that gives the region an accessible name.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- If the content has no meaningful heading, a generic container may be more appropriate.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
