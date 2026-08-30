---
title: EnvironmentBanner
description: Non-production environment banner for shell chrome.
---

# `EnvironmentBanner`

Non-production environment banner for shell chrome.

| | |
|---|---|
| Import | `from hedron import EnvironmentBanner` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="EnvironmentBanner"><div class="hdc-stage"><div class="hdc-banner hdc-warning" role="status"><strong>Staging</strong></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import EnvironmentBanner
component = EnvironmentBanner('Staging', tone='warning')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

EnvironmentBanner keeps staging/canary honesty visible without custom CSS.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
EnvironmentBanner(label, *, tone='warning', id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Environment label shown to operators. |
| `tone` | `info | warning | danger` | Semantic urgency token. |

## Composition and backend behavior

Keep `EnvironmentBanner` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`EnvironmentBanner` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Prefer warning for non-prod and danger for break-glass hosts.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use this banner for ordinary product marketing copy.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
