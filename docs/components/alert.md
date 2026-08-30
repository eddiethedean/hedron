---
title: Alert
description: Present an important text message using an appropriate live-region policy.
---

# `Alert`

Present an important text message using an appropriate live-region policy.

| | |
|---|---|
| Import | `from hedron import Alert` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Alert"><div class="hdc-stage"><div class="hdc-alert" role="status"><strong>Saved</strong><p>Your changes were saved.</p></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Alert
component = Alert('Your changes were saved.', tone='success', title='Saved')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Alerts group an optional strong title and escaped message with tone styling. Danger messaging uses alert semantics; lower-urgency messages use status semantics to avoid unnecessary interruption.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
Alert(message, *, tone='info', title=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `message` | `str` | Escaped alert text. |
| `tone` | `info | success | warning | danger` | Visual and semantic urgency. |
| `title` | `str | None` | Optional concise heading text. |

## Composition and backend behavior

Keep `Alert` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Alert` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Reserve assertive alerts for errors requiring immediate attention and move focus only when the next action would otherwise be unclear.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Alert accepts text, not arbitrary child components; compose a custom semantic region when the message needs structured controls.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
