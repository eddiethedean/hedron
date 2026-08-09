# hedron-explorer

Development Component Explorer for Hedron.

**Package maturity:** Beta · **Train:** `0.23.0` · pin `>=0.23.0,<0.24`  
**Flagship extra:** `hedron[dev]` · **Import:** `hedron_explorer`  
**Mount:** `/hedron-explorer/` when enabled · **not required in production**

## Install

```bash
pip install "hedron[dev]>=0.23.0,<0.24"
# or
pip install "hedron-explorer>=0.23.0,<0.24"
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
| HTML panels | Components, routes, graph, security, a11y, packages, settings |
| JSON APIs | `/hedron-explorer/api/*` — sanitized registry views |
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
| Production + `development` | Forced off at startup |
| Path outside allowlist | Blocked (no secret file reads) |

## Related docs

- API: [Explorer](../api/EXPLORER.md)
- A11y: [Accessibility API](../api/A11Y.md)
- Install troubleshooting: [Explorer 404](../guides/troubleshooting.md#explorer-404-or-missing-in-production)

## Links

- [PyPI](https://pypi.org/project/hedron-explorer/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-explorer/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-explorer)
