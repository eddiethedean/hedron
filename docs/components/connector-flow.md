---
title: ConnectorFlow
description: Responsive connector canvas for source, track, and destination workflow nodes.
---

# `ConnectorFlow`

Responsive connector canvas for source, track, and destination workflow nodes.

| | |
|---|---|
| Import | `from hedron import ConnectorFlow` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ConnectorFlow"><div class="hdc-stage"><div class="hdc-connector-flow"><article class="hdc-connector-node"><strong>CSV source</strong><small>Ready</small></article><div class="hdc-connector-track" aria-label="Transfer stages"><span>Transfer</span></div><article class="hdc-connector-node"><strong>Warehouse target</strong><small>Running</small></article></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ConnectorFlow, ConnectorNode, ConnectorTrack
component = ConnectorFlow(ConnectorNode('CSV', kind='source'), ConnectorTrack(label='Transfer'), ConnectorNode('Warehouse', kind='target'), direction='horizontal')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

ConnectorFlow provides a responsive, semantic canvas while preserving source order for fallback and reduced-motion rendering. It reuses the process-flow layout contract so applications do not need bespoke connector CSS.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
ConnectorFlow(*nodes, children=None, direction='horizontal', collapse='md', id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes / children` | `NodeLike` | ConnectorNode and ConnectorTrack children in reading order. |
| `direction` | `horizontal | vertical` | Primary flow orientation. |
| `collapse` | `never | sm | md | lg` | Breakpoint where a horizontal flow stacks. |

## Composition and backend behavior

Keep `ConnectorFlow` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`ConnectorFlow` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Choose an orientation that remains understandable when the flow collapses, and keep node state text in each node.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use ConnectorFlow as primary navigation or rely on JavaScript to make the workflow legible.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
