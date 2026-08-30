---
title: AccountSummary
description: Compact signed-in account summary for shell chrome.
---

# `AccountSummary`

Compact signed-in account summary for shell chrome.

| | |
|---|---|
| Import | `from hedron import AccountSummary` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="AccountSummary"><div class="hdc-stage"><div class="hdc-inline"><strong>Ada Lovelace</strong><span class="hdc-muted">Admin</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import AccountSummary
component = AccountSummary('Ada Lovelace', detail='Admin', href='/account')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

AccountSummary is a compact chrome identity strip, not a full profile page.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
AccountSummary(name, *, detail=None, href=None, id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Display name. |
| `detail` | `str | None` | Optional role or email line. |
| `href` | `SafeUrl | str | None` | Optional account destination. |

## Composition and backend behavior

Keep `AccountSummary` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`AccountSummary` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Pair with Avatar/Identity when a face mark is required.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not nest interactive controls inside the summary link.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
