---
status: shipped
---

# Explorer API


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Shipped · package `hedron-explorer` via `hedron[dev]`

`hedron-explorer` mounts under **`/hedron-explorer/`** when `explorer` is `development`
or `secured` on `Hedron(...)`. Phase **0.50** Explorer architecture is **shipped**
(D-085 / D-086 / RFC-0077; tracking [#501](https://github.com/eddiethedean/hedron/issues/501);
related [#496](https://github.com/eddiethedean/hedron/issues/496)–[#500](https://github.com/eddiethedean/hedron/issues/500) /
[#502](https://github.com/eddiethedean/hedron/issues/502) /
[#503](https://github.com/eddiethedean/hedron/issues/503)) — see [Explorer architecture](EXPLORER_ARCHITECTURE.md).

```python
from hedron import Hedron, Page, Text

app = Hedron(
    title="Demo",
    security="standard",
    session_secret="replace-me",
    explorer="development",  # requires hedron[dev]
)


@app.page("/")
def home() -> Page:
    return Page(Text("open /hedron-explorer/"), title="Home")
```

## Surfaces

- HTML shell with HTMX navigation across components, routes, graph, security,
  accessibility, cache, data, charts, maps, HTMX extensions, auto, packages,
  elements, inventory, interactions, features, and settings.
- JSON APIs under `/hedron-explorer/api/*` return sanitized registry views (no secrets, no
  absolute paths as live data). Additive 0.50 routes include `GET /hedron-explorer/api/diff`
  and `GET /hedron-explorer/api/package-health`. `GET /hedron-explorer/api/dashboard-graph`
  serializes `app.state.hedron_dashboard_graph` when it is an `InteractionGraph`; otherwise
  it returns an empty experimental payload.

```python
from hedron_core.dashboard import InteractionGraph

graph = InteractionGraph()
# graph.declare_inputs(...) / graph.register(...)
app.state.hedron_dashboard_graph = graph
```
- Preview renders through the production renderer and attaches the active build manifest
  when present.
- Request simulation is allowlisted and mutation-safe by default (`allow_mutations=false`). Boolean
  fields require JSON booleans, modes are limited to `fragment`, `boosted`, and `page`, response
  status overrides are limited to 100–599, and targets must be strings.

## Modes

| Mode | Behavior |
|---|---|
| `off` | Not mounted |
| `development` | Mounted locally; **forced off in production** |
| `secured` | Mounted behind `explorer_dependencies` / auth |

## Guarantees

Registry identifiers only; redaction; rate limiting and audit hooks in secured mode;
keyboard-operable shell. Explorer live traces for SSE/WebSocket remain owned Deferred in
0.10.x — see [What's ready](../guides/whats-ready.md).

## Errors

| Condition | Behavior |
|---|---|
| Missing `hedron[dev]` | Mount fails / Explorer unavailable |
| Production + `development` | Forced off at startup after `RISK_EXPLORER_DEVELOPMENT` (accept the risk, Explorer still does not mount) |
| Truncated table | `HED-EXPLORER-0001` plus cursor `Next`/`Previous` links; not a silent slice |
| Provider timeout/crash | `HED-EXPLORER-0002`; other panels keep rendering |
| Provider payload too large | `HED-EXPLORER-0003` |
| Path outside allowlist | Blocked (no secret file reads) |

## See also

[Installation](../getting-started/installation.md) · [Security](../guides/security.md)
