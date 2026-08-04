---
title: Status
description: Announce a concise operation state with a semantic tone.
---

# `Status`

Announce a concise operation state with a semantic tone.

| | |
|---|---|
| Import | `from hedron import Status` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Status"><div class="hdc-stage"><div class="hdc-status" role="status"><i></i><span>Import complete: 84 records added.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Status

component = Status('Import complete: 84 records added.', tone='success')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Status is intended for updates such as saved, queued, or completed. With live behavior enabled, an update inserted after page load is announced politely.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Status(message, *, tone='info', live=True)
```

| Parameter | Type | Meaning |
|---|---|---|
| `message` | `str` | Status text. |
| `tone` | `info | success | warning | danger` | Visual token. |
| `live` | `bool` | Enable polite live-region behavior. |

## Composition and backend behavior

Keep `Status` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep the live region mounted when possible and update its text; do not flood it with rapid, low-value changes.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Use Alert/ErrorState for urgent failures that require action.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
