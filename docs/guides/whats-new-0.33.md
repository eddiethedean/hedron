# What’s new in 0.33

**Published** as `v0.33.0`. Historical coordinated pin: `hedron>=0.33.0,<0.34`.
For new apps, use `hedron>=0.56.0,<0.59`; see [What’s new in 0.51](whats-new-0.51.md).

Phase **0.33** (D-061 / RFC-0066) ships **`hedron-posit`** as the unified Posit
Workbench / Connect deployment adapter. Native Connect GUID on Connect
**2026.07.0** is Supported; Supported cookie bridge is **out of scope** after
Stage 0 (`BRIDGE_DECISION=drop_supported`).

## Highlights

- **`hedron-posit` `0.33.0` Beta:** `HedronPosit` + nested `PositConfig` /
  `ConnectConfig`; product resolution with conflict fail-closed; native Connect
  base-header / `root_path` contract; `hedron-posit` CLI.
- **`hedron-workbench` `0.33.0` Beta:** thin `HedronWorkbench(HedronPosit)`
  compatibility package (supported through ≥0.35; no 0.33 deprecation warning).
- **Bridge:** `ConnectCookieMode.authenticated_header_v1` remains an
  Experimental extension-point enum only and fails closed (`HED-POSIT-0401`).
- **Coordinated train:** flagship packages `0.33.0`; `fastapi-workbench` stays
  independent `1.x`; MCP remains independent `>=0.2.0,<0.3`.

## Upgrade

```bash
python -m pip install -U "hedron>=0.33.0,<0.34"
python -m pip install -U "hedron[posit]>=0.33.0,<0.34"
# compatibility:
python -m pip install -U "hedron[workbench]>=0.33.0,<0.34"
```

Prefer `from hedron_posit import HedronPosit`. Existing
`from hedron_workbench import HedronWorkbench` imports continue to work.

Details: [RELEASE_0_33](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_33.md) · [Posit guide](posit.md) ·
[upgrade guide](upgrade.md).
