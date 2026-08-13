# Upgrade to Hedron 0.33

This guide covers an application upgrade onto the **0.33.x** train
(current tip **`v0.33.0`**). New applications should use
[Build your first app](../getting-started/quickstart.md).

## Summary

Hedron 0.33.x ships **`hedron-posit`** as the preferred Posit Workbench / Connect
deployment facade (D-061 / RFC-0066). Native Connect GUID on Connect **2026.07.0**
is Supported. Supported cookie bridge is **out of scope** (`BRIDGE_DECISION=drop_supported`).
`hedron-workbench` remains a Supported compatibility package through at least 0.35.

Prior trains remain in force: MCP (`hedron-mcp` `0.2.x`), Workbench ASGI
(`fastapi-workbench` `1.x`), tooling-grade conformance packages, and
`hedron migrate streamlit`. Polling remains the production recommendation for live
status. SSE, WebSocket, streaming, and navigation preload remain experimental.

## Before upgrading

1. Commit or back up your lockfile.
2. Confirm you are on a recent pin (`hedron>=0.29.0,<0.30` through `>=0.32.0,<0.33`,
   or the tip pin already).
3. If you use Posit Workbench or Connect, prefer `hedron[posit]` / `HedronPosit`.
   Existing `hedron[workbench]` / `HedronWorkbench` imports continue to work.
4. Do not select `ConnectCookieMode.authenticated_header_v1` — it fails closed in 0.33.

## Install

```bash
python -m pip install -U "hedron>=0.33.0,<0.34"
python -m pip install -U "hedron[posit]>=0.33.0,<0.34"
# compatibility:
python -m pip install -U "hedron[workbench]>=0.33.0,<0.34"
```

## Posit migration sketch

```python
# Before (still supported)
from hedron_workbench import HedronWorkbench
app = HedronWorkbench(...)

# Preferred
from hedron_posit import HedronPosit, PositConfig
app = HedronPosit(..., posit=PositConfig())
```

See [What’s new in 0.33](whats-new-0.33.md) · [Posit guide](posit.md) ·
[What’s ready](whats-ready.md) · [release notes](release-notes.md).
