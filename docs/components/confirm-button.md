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

<!-- hedron-sim:component-confirm -->

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ConfirmButton

component = ConfirmButton('Delete', confirm='Delete item?')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

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

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

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
