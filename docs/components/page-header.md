---
title: PageHeader
description: Eyebrow/title/description header with optional metadata and actions.
---

# `PageHeader`

Eyebrow/title/description header with optional metadata and actions.

| | |
|---|---|
| Import | `from hedron import PageHeader` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="PageHeader"><div class="hdc-stage"><header class="hdc-type"><span class="hdc-eyebrow">Operate</span><h2>Pipelines</h2><p class="hdc-muted">Source to destination jobs.</p><div class="hdc-inline"><button class="hdc-button hdc-primary" type="button">New</button></div></header></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ActionGroup, Button, PageHeader
component = PageHeader(title='Pipelines', eyebrow='Operate', description='Source to destination jobs.', title_wrap='balance', description_wrap='pretty', actions=ActionGroup(Button('New')))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

PageHeader is the workspace page pattern for title, context, and actions without application CSS.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
PageHeader(title, *, eyebrow=None, description=None, title_measure=None, description_measure=None, title_effect=None, description_effect=None, title_tracking=None, description_tracking=None, title_wrap=None, description_wrap=None, eyebrow_tone=None, eyebrow_tracking=None, eyebrow_wrap=None, actions=None, meta=None, id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `title` | `str | NodeLike` | Primary heading text or node. |
| `eyebrow` | `str | NodeLike | None` | Optional overline label. |
| `description` | `str | NodeLike | None` | Supporting copy under the title. |
| `actions` | `NodeLike | None` | Primary action cluster (often ActionGroup). |
| `meta` | `NodeLike | None` | Optional metadata below the description. |
| `title_measure / description_measure` | `narrow | default | wide | None` | Independent readable-width tokens. |
| `title_effect / description_effect` | `none | subtle | display | None` | Independent named text effects. |
| `title_tracking / description_tracking / eyebrow_tracking` | `tight | normal | loose | wide | None` | Finite letter-spacing choices. |
| `title_wrap / description_wrap / eyebrow_wrap` | `normal | wrap | balance | pretty | break | truncate | clip | None` | Finite text-wrap and overflow choices. |
| `eyebrow_tone` | `accent | muted | neutral | None` | Semantic eyebrow color. |

## Composition and backend behavior

Keep `PageHeader` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`PageHeader` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep one PageHeader per primary view and put long forms below it.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not nest PageHeader inside another PageHeader.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
