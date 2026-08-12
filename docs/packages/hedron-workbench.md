# hedron-workbench

Optional Posit Workbench / RStudio Server deployment adapter.

**Package maturity:** Beta (`0.29.0`) · extra `hedron[workbench]` · pin `>=0.29.0,<0.30`

Installing or importing the package does **not** wrap your application.
`RS_SERVER_URL` is discovery-only and never grants trust.

Guide: [Posit Workbench](../guides/posit-workbench.md) · RFC:
[RFC-0062](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0062-POSIT-WORKBENCH-ADAPTER.md)

## Public API

| Symbol | Role |
|---|---|
| `HedronWorkbench` | `Hedron` subclass with opt-in Workbench resolution and path normalization |
| `app.external_url` / `app.external_url_for` | Stable public links for email, OAuth, and callbacks; fail closed without a trusted base |
| `WorkbenchConfig` / `WorkbenchMode` | Immutable config (`auto` / `on` / `off`) |
| `ExternalBase` / Connect URL helpers | Validated public-origin composition; Connect support is Experimental |
| `resolve_deployment` | Side-effect-free resolution |
| `workbenchify` / `WorkbenchPathMiddleware` | Idempotent ASGI wrapper |
| `hedron-workbench run` / `check` | Pre-import launcher and dry-run |

Cookie `Path` is fixed at `Hedron()` construction. The launcher exports
`HEDRON_ROOT_PATH` **before** import. `workbenchify` cannot repair cookies on an
already-built app.

`HedronWorkbench` consumes the launcher's resolved mount before calling
`Hedron.__init__`, supplies a missing ASGI `root_path` from an explicit mount,
and reports redacted state through `workbench_status()`. With no Workbench
signal it preserves ordinary Hedron behavior.

For links that leave the browser, configure `workbench_public_base_url` (or
`external_base_url`) when Workbench discovery returns only a mount. Hedron will
not emit loopback or inbound-`Host` email links. Connect's app-base header is
accepted only when its path matches ASGI `root_path` and Connect's protected
runtime marker is present; this Connect behavior remains Experimental.
