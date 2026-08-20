# Posit lifecycle API

Package: [`hedron-posit`](https://pypi.org/project/hedron-posit/).

**Phase 0.52 public contract:** D-089 / D-090 /
[RFC-0079](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md) /
[#522](https://github.com/eddiethedean/hedron/issues/522). Companions
[#508](https://github.com/eddiethedean/hedron/issues/508)–[#513](https://github.com/eddiethedean/hedron/issues/513).
Living tip is `v0.53.0` (in-tree Published; tag/PyPI deferred). Stage 1 ships the
deployment lifecycle symbols below.

## Shipped 0.52 surface

| Symbol / seam | Role |
|---|---|
| `HedronPosit` | Unified Posit deployment adapter |
| `PositContext` / `posit_for(request)` | Request-bound links, redirects, cookies, capabilities |
| `CookieRegistry` / `CookieSpec` | Cookie registry + set/delete lifecycle; matching create/delete paths |
| `hands_off` (`PositConfig.hands_off`) | Opt-in adaptation of local Hedron/HTMX URLs, `Location`, assets (validated same-app paths only) |
| `href` / `href_for` | App-relative links (query/fragment/durable parity) |
| `redirect` / `redirect_for` | Redirect helpers (query/fragment/durable parity) |
| `browser_url` / `browser_url_for` | Browser-facing URLs |
| `external_url` / `durable_url` (+ `_for`) | External / durable URL helpers |
| `cookie_path_for_mount` | Construction-time cookie Path for mounts |
| `workbenchify` | Owned-cookie Path repair (`session`, `hedron_color_mode`, CSRF) |
| `ConnectCookieMode.NATIVE` | Supported Connect cookie mode |
| `DEFAULT_MATRIX` / `MatrixCase` / `run_deployment_matrix` | Deployment-matrix fixtures |
| `hedron-posit check --matrix` | Matrix checker CLI |
| `PositDiagnostic` | Proactive mount/redirect/cookie diagnostics (stable codes; never log cookie values) |
| `hedron-posit check` / `run` / `doctor` | CLI |

Supported Connect authenticated-header cookie bridge remains
`drop_supported`.

## Gate mapping

| Gate | Public contract |
|---|---|
| `COOKIE-052` (#508) | `CookieRegistry` set/delete; no literal `Path=auto` |
| `CONTEXT-052` (#509) | `PositContext` / `posit_for(request)` |
| `HANDSOFF-052` (#510) | Opt-in `hands_off` adaptation |
| `MATRIX-052` (#511) | Matrix fixtures + `check --matrix` |
| `PDIAG-052` (#512) | `PositDiagnostic` codes; never log cookie values |
| `ROUTEURL-052` (#513) | Query/fragment/durable parity across href/redirect/browser_url/durable_url families |

## Errors / honesty

| Condition | Behavior |
|---|---|
| Literal `Set-Cookie` `Path=auto` | Forbidden; diagnostics must flag |
| Cookie value in logs | Forbidden under `PDIAG-052` |
| Unsupported Connect bridge | Remains dropped; do not market as Supported |
| Unvalidated URL rewrite in hands-off mode | Must not rewrite off-app paths |

See [POSIT_LIFECYCLE_052](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/POSIT_LIFECYCLE_052.md) and
[posit-lifecycle-052.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/posit-lifecycle-052.toml).
