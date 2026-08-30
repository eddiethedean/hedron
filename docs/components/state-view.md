---
title: StateView
description: Unified loading, empty, error, permission, offline, and success surface.
---

# `StateView`

Unified loading, empty, error, permission, offline, and success surface.

| | |
|---|---|
| Import | `from hedron import StateView` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="StateView"><div class="hdc-stage"><div class="hdc-alert" role="status"><strong>Empty</strong><p>No pipelines yet. Create a pipeline to start ingesting data.</p><button class="hdc-button hdc-primary" type="button">New pipeline</button></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Button, StateView
component = StateView('No pipelines yet', kind='empty', description='Create a pipeline to start ingesting data.', actions=Button('New pipeline'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

StateView chooses an appropriate live-region role and always shows a textual kind label so state is never color- or icon-only.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
StateView(title, *nodes, *, kind='empty', description=None, detail=None, actions=None, id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `title` | `str` | Primary message for the state. |
| `kind` | `loading | empty | error | permission | offline | success` | Closed state vocabulary. |
| `description / detail` | `str | None` | Optional supporting copy. |
| `actions` | `NodeLike | None` | Optional recovery or next-step controls. |

## Composition and backend behavior

Keep `StateView` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`StateView` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Prefer StateView for empty tables, failed loads, and permission blocks instead of ad-hoc cards.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use StateView for ordinary inline validation—use FormErrors or Alert.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
