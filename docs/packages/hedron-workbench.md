# hedron-workbench

Optional Posit Workbench / RStudio Server deployment adapter.

**Package maturity:** Beta (`0.30.0`) · extra `hedron[workbench]` · pin `>=0.31.0,<0.32`

Installing or importing the package does **not** wrap your application.
`RS_SERVER_URL` is discovery-only and never grants trust.

Guide: [Posit Workbench](../guides/posit-workbench.md) · RFC:
[RFC-0062](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0062-POSIT-WORKBENCH-ADAPTER.md)

## Public API

| Symbol | Role |
|---|---|
| `HedronWorkbench` | `Hedron` subclass with opt-in Workbench resolution and path normalization |
| `app.browser_url*` / `app.external_url*` | Explicit ephemeral-browser versus durable email/OAuth URL contracts |
| `app.href_for` / `app.redirect_for` | Mount-aware local route helpers |
| `app.deployment_capabilities` | Typed platform/link/transport capability report |
| `WorkbenchConfig` / `WorkbenchMode` / `WorkbenchTopology` | Immutable mode and topology config |
| `ExternalBase` / Connect URL helpers | Validated public-origin composition; Connect support is Experimental |
| `resolve_deployment` | Side-effect-free resolution |
| `workbenchify` / `WorkbenchPathMiddleware` | Idempotent ASGI wrapper |
| `hedron-workbench run` / `check` / `doctor` | Pre-import launcher, dry-run, and live probe |

The launcher exports `HEDRON_ROOT_PATH` **before** import. When a trusted ASGI
mount only arrives at request time, the outer response boundary repairs
Hedron-owned cookies and safe local redirect/HTMX headers; third-party cookies
remain application-owned.

`HedronWorkbench` consumes the launcher's resolved mount before calling
`Hedron.__init__`, supplies a missing ASGI `root_path` from an explicit mount,
and reports redacted state through `workbench_status()`. With no Workbench
signal it preserves ordinary Hedron behavior.

For links that leave the browser, configure a stable `external_base_url` or use
Posit Connect. Workbench session mounts are deliberately browser-only and are
rejected by the durable URL API. Hedron will not emit loopback or inbound-`Host`
email links. Connect's app-base header is
accepted only when its path matches ASGI `root_path` and Connect's protected
runtime marker is present; this Connect behavior remains Experimental.
