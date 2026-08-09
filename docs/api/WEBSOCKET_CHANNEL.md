---
status: experimental
---

# Page/session WebSocket channel


!!! note "Stability"

    Classifications live in [STABILITY.md](STABILITY.md). Page/session channels are
    **experimental** (`hedron.experimental`) under Accepted 0.24 **`polling_only`**
    ([LIVE_DISPOSITION](LIVE_DISPOSITION.md)). Prefer polling in production.

**Status:** Shipped in `0.10.0` (experimental)

Helpers: `accept_page_session_channel`, `send_region_update`, `origin_allowed`,
`ALLOW_MISSING_ORIGIN` — import from `hedron.experimental`. Channel models live in
`hedron_core.channel` (`PageSessionChannel`, `RegionUpdate`, `ChannelMessage`).

## `accept_page_session_channel`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `websocket` | Starlette `WebSocket` | required | Incoming socket |
| `channel` | `PageSessionChannel` | required | Session-scoped channel |
| `allowed_origins` | `frozenset[str] \| None` | same-host default | Explicit Origin allowlist |
| `allow_missing_origin` | `bool` | `False` | Permit non-browser clients without Origin |
| `on_client_state` | async callable \| `None` | `None` | Serve allowlisted client-state reads |
| `producer` | async callable \| `None` | `None` | Background push loop |

Closes with code `1008` when Origin is rejected. Client messages use JSON `kind` values
such as `close` and `client-state-request`.

## `send_region_update(websocket, update)`

Sends a `RegionUpdate` (or compatible payload) as a JSON text frame.

## `origin_allowed`

Returns whether the WebSocket `Origin` is permitted. Missing Origin is denied unless
`allow_missing_origin=True` or `ALLOW_MISSING_ORIGIN` (`"*"`) is in `allowed_origins`.

## Errors

| Condition | Behavior |
|---|---|
| Origin denied | Socket closed (`1008`); no accept |
| Disconnect | Handler exits; producer task cancelled |
| Invalid client-state field | Channel validation raises before send |

## See also

[Live interaction guide](../guides/live-interaction.md)
