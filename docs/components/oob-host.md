---
title: OobHost
description: Stable out-of-band swap root with a reserved id.
---

# `OobHost`

Stable out-of-band swap root with a reserved id.

| | |
|---|---|
| Import | `from hedron import OobHost` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<!-- hedron-sim:component-oob-host -->

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import OobHost, Toast

component = OobHost(Toast('Saved'), id='toast-host')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

OobHost reserves a predictable DOM root for `oob_swap` updates. Pair with authorize_oob_update and reserved-id rules so fragments cannot target arbitrary selectors.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
OobHost(*nodes, *, id, tag='div', class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `id` | `str` | Required stable element id for OOB targeting. |
| `tag` | `str` | Host element tag (default div). |
| `class_` | `str | None` | Optional CSS classes. |

## Composition and backend behavior

Keep `OobHost` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Give each OOB host a unique page-local id and keep toast/status regions outside MainPanel when they must survive panel swaps.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not reuse an OobHost id for ordinary fragment regions.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
