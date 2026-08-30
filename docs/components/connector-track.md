---
title: ConnectorTrack
description: Accessible visual link between provider-neutral workflow nodes.
---

# `ConnectorTrack`

Accessible visual link between provider-neutral workflow nodes.

| | |
|---|---|
| Import | `from hedron import ConnectorTrack` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ConnectorTrack"><div class="hdc-stage"><div class="hdc-connector-track" aria-label="Transfer stages"><span>Transfer stages</span><small>TLS 1.3 · Encrypted in transit</small></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ConnectorTrack, Text
component = ConnectorTrack(Text('TLS 1.3 · Encrypted in transit'), label='Transfer stages', active=True)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

ConnectorTrack keeps the line and annotations useful without motion. Active animation is progressive enhancement and is disabled under reduced-motion preferences.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
ConnectorTrack(*nodes, children=None, active=False, label=None, id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes / children` | `NodeLike` | Track annotation or process content. |
| `active` | `bool` | Opt-in active motion hook; the static track remains present. |
| `label` | `str | None` | Accessible label for the track when needed. |

## Composition and backend behavior

Keep `ConnectorTrack` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`ConnectorTrack` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Give the track a concise label when its annotation is not otherwise clear from the adjacent nodes.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not make the animated state the only indication that a transfer is running.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
