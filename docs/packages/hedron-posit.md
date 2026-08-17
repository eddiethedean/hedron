# hedron-posit

Unified Posit Workbench / Connect deployment adapter for Hedron.

**Package maturity:** Beta (`0.36.0`) · extra `hedron[posit]` · pin `>=0.49.0,<0.50`

Installing or importing the package does **not** wrap your application.
`RS_SERVER_URL` is discovery-only and never grants trust. Connect credential
headers are never mapped to Hedron authentication.

Guide: [Posit deployments](../guides/posit.md) · RFC:
[RFC-0066](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0066-HEDRON-POSIT.md)

## Public API

| Symbol | Role |
|---|---|
| `HedronPosit` | Preferred `Hedron` facade for local / Workbench / Connect |
| `PositConfig` / `PositProduct` | Nested frozen product configuration |
| `ConnectConfig` / `ConnectCookieMode` | Native Connect cookies (Supported); bridge enum fails closed |
| `PositStatus` / `app.posit_status()` | Typed, secret-free diagnostics |
| `resolve_posit_deployment` / `resolve_product` | Pure product + Workbench resolution |
| `WorkbenchConfig` / Workbench helpers | Delegated Workbench surface |
| `hedron-posit run` / `check` / `doctor` | Pre-import launcher and diagnostics |

Dependency graph (one-way):

```text
hedron-workbench -> hedron-posit -> hedron + fastapi-workbench
```

`hedron-workbench` remains a Supported compatibility package through at least
0.35 (`HedronWorkbench` subclass; no 0.33 deprecation warning).

Supported Workbench floor is **2025.05.1**; current verified lane is **2026.07.0**.
