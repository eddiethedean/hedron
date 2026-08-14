# Upgrade to Hedron 0.36

This guide covers an application upgrade onto the **0.36.x** train
(current tip **`v0.37.0`**). New applications should use
[Build your first app](../getting-started/quickstart.md).

## Summary

Hedron 0.36.x ships the Web Component ABI foundation and Alpha **`hedron-elements`**
(D-064 / RFC-0060). Prefer `hedron[posit]` / `HedronPosit` for Posit Workbench /
Connect. Native Connect GUID on Connect **2025.06.0** through **2026.07.0** is
Supported. Posit Workbench **2025.05.1** through **2026.07.0** is Supported for
`hedron-workbench`, `hedron-posit`, and `fastapi-workbench`. Supported cookie bridge
is **out of scope** (`BRIDGE_DECISION=drop_supported`). `hedron-workbench` remains a
Supported compatibility package.

Prior trains remain in force: MCP (`hedron-mcp` `0.2.x`), Workbench ASGI
(`fastapi-workbench` `1.x`), tooling-grade conformance packages, and
`hedron migrate streamlit`. Polling remains the production recommendation for live
status. SSE, WebSocket, streaming, and navigation preload remain experimental.

## Before upgrading

1. Commit or back up your lockfile.
2. Confirm you are on a recent pin (`hedron>=0.29.0,<0.30` through `>=0.35.0,<0.36`,
   or the tip pin already).
3. If you use Posit Workbench or Connect, prefer `hedron[posit]` / `HedronPosit`.
   Existing `hedron[workbench]` / `HedronWorkbench` imports continue to work.
4. Do not select `ConnectCookieMode.authenticated_header_v1` — it fails closed in 0.33+.
5. Optional: install `hedron[elements]` only if you need Alpha Web Component hosts.

## Install

```bash
python -m pip install -U "hedron>=0.37.0,<0.38"
python -m pip install -U "hedron[posit]>=0.37.0,<0.38"
# optional Alpha elements:
python -m pip install -U "hedron[elements]>=0.37.0,<0.38"
# compatibility:
python -m pip install -U "hedron[workbench]>=0.37.0,<0.38"
```

## Posit migration sketch

Prefer `from hedron_posit import HedronPosit` over legacy Workbench-only imports when
starting new apps. See [Posit](posit.md) and [What’s new in 0.36](whats-new-0.36.md).

## See also

[Release notes](release-notes.md) · [What’s ready](whats-ready.md) ·
[COMPATIBILITY](../COMPATIBILITY.md) · [RELEASE_0_36](../acceptance/RELEASE_0_36.md)
