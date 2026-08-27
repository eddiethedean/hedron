---
title: Dialog
description: Present focused content in a native dialog with an explicit title and close path.
---

# `Dialog`

Present focused content in a native dialog with an explicit title and close path.

| | |
|---|---|
| Import | `from hedron import Dialog` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Dialog"><div class="hdc-stage"><div class="hdc-dialog-launch"><span class="hdc-file-icon" aria-hidden="true">R</span><span><strong>Quarterly report</strong><small>Updated 2 minutes ago</small></span><button class="hdc-button" type="button" data-hdc-action="open-dialog">Delete…</button></div><dialog class="hdc-dialog" data-hdc-dialog aria-labelledby="hdc-dialog-title"><header><h2 id="hdc-dialog-title">Delete report?</h2><form method="dialog"><button type="submit" class="hdc-dialog-close" aria-label="Close dialog">×</button></form></header><p>This removes the saved report. The source data is unchanged.</p><footer><button class="hdc-button" type="button" data-hdc-action="close-dialog">Cancel</button><button class="hdc-button hdc-primary" type="button" data-hdc-action="close-dialog">Delete report</button></footer></dialog><p class="hdc-muted" role="status" data-hdc-status>Dialog closed.</p></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Dialog, Text

component = Dialog('Delete report', Text('This action cannot be undone.'), id='delete-report')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Dialog renders a native `<dialog>` with a level-two title, body region, built-in Close form using the browser's dialog submission method, and an optional actions slot. A button whose `data-hedron-dialog-open` value is the dialog's `#id` opens it through the shipped browser module; modal dialogs use `showModal()`, while `modal=False` uses `show()`. Already-open modal dialogs are upgraded to `showModal()` on boot and after HTMX swaps. The component never treats confirmation as authorization.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Dialog(title, *nodes, children=None, open=False, modal=True, id=None, element_id=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `title` | `str` | Required dialog heading text. |
| `nodes` | `NodeLike` | Positional dialog body content. |
| `children` | `NodeLike | sequence | None` | Keyword body content; combines with positional nodes. |
| `open` | `bool` | Render the native open attribute initially. |
| `modal` | `bool` | Browser-module intent exposed as data-modal. |
| `id` | `str | None` | Stable ID for a trigger and focus restoration. |
| `element_id` | `str | None` | Compatibility alias for id. |

## Composition and backend behavior

Keep `Dialog` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Dialog` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

## Accessibility

Open it from a clearly labelled trigger, place initial focus deliberately, support Escape and the Close control, and restore focus to the trigger when it closes.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- The `open` attribute alone does not create modal focus trapping or background inertness; use the supported browser module to call `showModal()`.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
