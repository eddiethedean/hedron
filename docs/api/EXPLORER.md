---
status: shipped
---

# Explorer API


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Shipped · package `hedron-explorer` via `hedron[dev]`

`hedron-explorer` mounts under **`/hedron-explorer/`** when `explorer` is `development`
or `secured` on `Hedron(...)`.

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
  accessibility, packages, and settings.
- JSON APIs under `/hedron-explorer/api/*` return sanitized registry views (no secrets, no
  absolute paths as live data).
- Preview renders through the production renderer and attaches the active build manifest
  when present.
- Request simulation is allowlisted and mutation-safe by default (`allow_mutations=false`).

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
| Production + `development` | Forced off at startup |
| Path outside allowlist | Blocked (no secret file reads) |

## See also

[Installation](../getting-started/installation.md) · [Security](../guides/security.md)
