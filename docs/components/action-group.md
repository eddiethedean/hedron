---
title: ActionGroup
description: Aligned cluster of actions for headers and footers.
---

# `ActionGroup`

Aligned cluster of actions for headers and footers.

| | |
|---|---|
| Import | `from hedron import ActionGroup` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ActionGroup"><div class="hdc-stage"><div class="hdc-inline"><button class="hdc-button" type="button">Cancel</button><button class="hdc-button hdc-primary" type="button">Save</button></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ActionGroup, Button

component = ActionGroup(Button('Cancel', appearance='ghost'), Button('Save'), align='end')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

ActionGroup keeps toolbar spacing and alignment in the default theme.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
ActionGroup(*actions, *, align='end', gap='0.5rem', id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `actions` | `NodeLike` | Buttons or links in the cluster. |
| `align` | `str` | `start` / `center` / `end` / `between`. |

## Composition and backend behavior

Keep `ActionGroup` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`ActionGroup` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Place primary actions last in LTR layouts.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use ActionGroup for navigation lists—use Nav / NavLink.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
