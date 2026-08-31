# hedron-posit

Unified Posit Workbench / Connect deployment adapter for Hedron.

**Package maturity:** Beta · **Package line:** `1.0.x`

Installing or importing the package does **not** wrap your application.
`RS_SERVER_URL` is discovery-only and never grants trust. Connect credential
headers are never mapped to Hedron authentication.

Guide: [Posit deployments](../guides/posit.md) · RFC:
[RFC-0066](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0066-HEDRON-POSIT.md) ·
0.52 lifecycle:
[RFC-0079](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md) /
companions [#508](https://github.com/eddiethedean/hedron/issues/508)–[#513](https://github.com/eddiethedean/hedron/issues/513).

## Public API

| Symbol | Role |
|---|---|
| `HedronPosit` | Preferred `Hedron` facade for local / Workbench / Connect |
| `PositConfig` / `PositProduct` | Nested frozen product configuration |
| `ConnectConfig` / `ConnectCookieMode` | Native Connect cookies (Supported); bridge enum fails closed |
| `CookieRegistry` / `CookieSpec` | Cookie registry + set/delete lifecycle (#508) |
| `PositContext` / `posit_for(request)` | Request-bound links, redirects, cookies, capabilities (#509) |
| `hands_off` (`PositConfig.hands_off`) | Opt-in same-app URL / redirect / asset adaptation (#510) |
| `DEFAULT_MATRIX` / `run_deployment_matrix` | Deployment-matrix fixtures (#511) |
| `PositDiagnostic` | Proactive mount/redirect/cookie diagnostics (#512) |
| `PositStatus` / `app.posit_status()` | Secret-free diagnostics with an explicit schema |
| `resolve_posit_deployment` / `resolve_product` | Pure product + Workbench resolution |
| `WorkbenchConfig` / Workbench helpers | Delegated Workbench surface |
| `hedron-posit run` / `check` / `check --matrix` / `doctor` | Pre-import launcher, matrix, and diagnostics |

Dependency graph (one-way):

```text
hedron-posit -> hedron + fastapi-workbench
```

The standalone `hedron-workbench` distribution was removed in 1.0.0. Existing
applications should migrate to `HedronPosit`; plain FastAPI applications can use
`fastapi-workbench` directly.

Supported Workbench floor is **2025.05.1**; current verified lane is **2026.07.0**.
