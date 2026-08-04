---
title: DescriptionList
description: Present term/value pairs as a native description list.
---

# `DescriptionList`

Present term/value pairs as a native description list.

| | |
|---|---|
| Import | `from hedron import DescriptionList` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="DescriptionList"><div class="hdc-stage"><dl class="hdc-description"><dt>Region</dt><dd>us-east-1</dd><dt>Status</dt><dd><span class="hdc-badge">Healthy</span></dd></dl></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Badge, DescriptionList, Status

component = DescriptionList(('Region', 'us-east-1'), ('Status', Badge('Healthy', tone='success')))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Every pair becomes a `dt` followed by a `dd`. Values can be components, which makes the component useful for metadata, summaries, and key/value inspection.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
DescriptionList(*pairs)
```

| Parameter | Type | Meaning |
|---|---|---|
| `pairs` | `tuple[NodeLike, NodeLike]` | Term and description pairs. |

## Composition and backend behavior

Keep `DescriptionList` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Terms should be concise and values should make sense when announced immediately after their term.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Use Table instead when rows share column headers or users need to compare several records.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
