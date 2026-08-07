---
title: ConfirmButton
description: Button with explicit confirmation prompt (not authorization).
---

# `ConfirmButton`

Button with explicit confirmation prompt (not authorization).

| | |
|---|---|
| Import | `from hedron import ConfirmButton` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ConfirmButton"><div class="hdc-stage"><button class="hdc-button" type="button" data-hdc-action="confirm-delete">Delete item</button><p class="hdc-muted" role="status" data-hdc-status>Confirmation required before the action runs.</p></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ConfirmButton

component = ConfirmButton('Delete', confirm='Delete item?')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
ConfirmButton(label: 'str', *, confirm: 'str', type: "Literal['button', 'submit', 'reset']" = 'button', disabled: 'bool' = False, variant: "Literal['primary', 'secondary', 'danger']" = 'danger', mark: 'str | None' = None, **kwargs: 'Any') -> 'None'
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Accessible label text shown to users. |
| `confirm` | `str` | Confirmation prompt text shown before the action runs. |
| `type` | `Literal['button', 'submit', 'reset']` | Native button `type` (`button`, `submit`, or `reset`). Default: `'button'`. |
| `disabled` | `bool` | Whether the control is non-interactive. Default: `False`. |
| `variant` | `Literal['primary', 'secondary', 'danger']` | Visual / semantic variant for the control. Default: `'danger'`. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). Default: `None`. |

## Composition and backend behavior

Keep `ConfirmButton` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keyboard and screen-reader operable; no-JS fallback required where interactive.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not treat client-only hints (geolocation, browser storage) as authorization.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
