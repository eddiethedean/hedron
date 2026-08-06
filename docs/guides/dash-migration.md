# Dash migration inventory (phase 0.17)

Hedron adopts useful Dash outcomes via explicit actions, fragments, and
[`DashboardBinding`](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0040-INTERACTION-GRAPH.md)
/ patches — **not** a React callback DAG or automatic conversion of clientside JavaScript.

| Dash concept | Hedron direction | Notes |
|---|---|---|
| `Input` / `Output` / `State` | `TriggerContext` triggers vs snapshot inputs | RFC-0040 |
| Chained callbacks | Finite `InteractionGraph` edges | Fail closed on cycles / duplicate writers |
| `Patch` / `set_props` | `PropertyPatch` / `CollectionPatch` | RFC-0041; full-fragment fallback |
| Pattern-matching IDs | Collection selectors | Not DOM CSS as authz |
| `dcc.Graph` events | 0.12 `ChartEvent` → cross-filter bindings | XFILTER-017 |
| Jupyter display | `hedron-notebook` preview | Experimental; localhost-oriented |
| Dash MCP | `hedron-mcp` opt-in projection | Deny-by-default empty |

**Non-parity:** clientside callback strings, undeclared `set_props`, unordered duplicate writers,
filesystem page magic, AG Grid Enterprise as OSS claims.

Tools may emit a **review plan**; they must never claim automatic semantic conversion of arbitrary
callbacks or JavaScript (`MIGRATE-017`).
