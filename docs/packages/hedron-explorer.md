# hedron-explorer

Development Component Explorer for Hedron.

**Package maturity:** Beta · **Train:** `0.64.x` (`v0.64.0` published on PyPI) · pin `>=0.64.0,<0.65`
**Flagship extra:** `hedron[dev]` · **Import:** `hedron_explorer`  
**Mount:** `/hedron-explorer/` when enabled · **not required in production**  
**Shipped:** phase [0.50](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md#050--explorer-architecture-and-operator-grade-development-tooling-v0500) — modular architecture, provider API, headless parity, large-app resilience (D-085 / D-086 / RFC-0077; [#501](https://github.com/eddiethedean/hedron/issues/501); in-tree `v0.50.3`).

## Install

```bash
pip install "hedron[dev]>=0.64.0,<0.65"
# or
pip install "hedron-explorer>=0.64.0,<0.65"
```

Requires [`hedron`](https://pypi.org/project/hedron/) (FastAPI flagship).

## When to use

- Inspect components, routes, dependency graph, security, and accessibility locally
- Simulate interactions against allowlisted endpoints during development

Leave Explorer **`off`** in production. Prefer `development` locally; use `secured`
only with explicit auth dependencies.

## Quick start

```python
from hedron import Hedron, Page, Text

app = Hedron(
    title="Demo",
    security="standard",
    session_secret="replace-me",
    explorer="development",
)


@app.page("/")
def home() -> Page:
    return Page(Text("Open /hedron-explorer/"), title="Home")
```

Open **`/hedron-explorer/`** on the running app.

## Surfaces

| Surface | Role |
|---|---|
| `explorer_router` | FastAPI router mounted under `/hedron-explorer/` |
| HTML panels | Components, routes, graph, security, a11y, cache, data, charts, maps, HTMX extensions, auto, packages, elements, inventory, interactions, features, settings |
| JSON APIs | `/hedron-explorer/api/*` — sanitized registry views plus `GET /api/diff` and `GET /api/package-health` |
| Element detail | Inspect ABI, parts/slots/tokens, events, and fallback for registered definitions |
| Element simulate | `POST /hedron-explorer/api/element-simulate` for allowlisted event simulation |
| Preview | Production renderer + active build manifest when present |
| Request simulation | Allowlisted; mutation-safe by default |

## Modes

| Mode | Behavior |
|---|---|
| `off` | Not mounted |
| `development` | Mounted locally; **forced off in production** |
| `secured` | Mounted behind `explorer_dependencies` / auth |

## Guarantees

- Registry identifiers only — no secrets, no absolute paths as live data
- Rate limiting and audit hooks in secured mode
- Keyboard-operable shell
- Explorer live traces for SSE/WebSocket remain Deferred (prefer polling)

## Errors and failure modes

| Condition | Behavior |
|---|---|
| Missing `hedron[dev]` | Mount fails / Explorer unavailable |
| Production + `development` | Forced off at startup after `RISK_EXPLORER_DEVELOPMENT` |
| Truncated table | `HED-EXPLORER-0001` with cursor pagination |
| Isolated provider crash/timeout | `HED-EXPLORER-0002` |
| Isolated provider payload ceiling | `HED-EXPLORER-0003` |
| Path outside allowlist | Blocked (no secret file reads) |

## Related docs

- API: [Explorer](../api/EXPLORER.md) · [Explorer architecture (0.50 shipped)](../api/EXPLORER_ARCHITECTURE.md)
- A11y: [Accessibility API](../api/A11Y.md)
- Install troubleshooting: [Explorer 404](../guides/troubleshooting.md#explorer-404-or-missing-in-production)

## Links

- [PyPI](https://pypi.org/project/hedron-explorer/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-explorer/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-explorer)
