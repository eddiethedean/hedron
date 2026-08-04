---
title: SubmitButton
description: Submit the nearest form with consistent primary-action styling.
---

# `SubmitButton`

Submit the nearest form with consistent primary-action styling.

| | |
|---|---|
| Import | `from hedron import SubmitButton` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="SubmitButton"><div class="hdc-stage"><form data-hdc-form><button class="hdc-button hdc-primary" type="submit">Save profile</button></form><p role="status" data-hdc-status>Ready to save.</p></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import SubmitButton

component = SubmitButton('Save profile')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The component fixes `type=submit`, avoiding the ambiguity of a generic button in a form, and applies the primary button class.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
SubmitButton(label='Submit', *, disabled=False)
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Visible submit action. |
| `disabled` | `bool` | Prevent submission. |

## Composition and backend behavior

Keep `SubmitButton` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Use a specific verb and expose pending state without replacing the accessible name with an unexplained spinner.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not disable the only submit path permanently after an HTMX error.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
