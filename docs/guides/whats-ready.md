# What’s ready today

Operator-facing snapshot of published **0.11.0**. Maintainer evidence tables live in
the repository [`docs/STATUS.md`](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md).

## How to read this page

Hedron **0.11.0** packages are **Beta**. There is no scheduled 1.0; expect occasional
breaking changes on `0.x` under the [compatibility policy](../COMPATIBILITY.md).

| Label | Meaning |
|---|---|
| **Supported** | Capability claimed working with pinned versions for the stated host |
| **API Supported / ops evidence incomplete** | Public API shipped; full browser/load/proxy proof still Deferred in STATUS |
| **Alpha** | Available on PyPI; pin and expect churn |
| **Deferred** | Documented, not ready — do not treat as Supported |

## Supported capabilities (Beta packages)

| Capability | Package / surface | Evidence note |
|---|---|---|
| Typed pages, fragments, built-ins | `hedron` + `hedron-core` | Supported |
| FastAPI routing, CSRF profiles, CLI, testing helpers | `hedron` | Supported |
| HTMX fragment loops, `InteractionResult` | `hedron` | Supported |
| Live interaction: SSE, streaming, WebSocket channels, Chat/Dialog, opt-in preload | `hedron` (FastAPI flagship) | **API Supported**; full multi-engine live browser matrix and load/proxy backpressure evidence are **Deferred** (`BROWSER-10-001`, `PERF-10-001`). Prefer polling when ops proof is required before those rows are Verified. |
| Flask Blueprint / `init_app` + live helpers | `hedron-flask` | Supported; WSGI buffering limits documented; polling Supported fallback |
| Django AppConfig, forms bridge, QuerySet DataSource | `hedron-django` + `hedron-data` | Supported under D-046 |
| Portable adapter test harness | `hedron.testing.adapters` | Supported |
| Optional HDJ (`.hdj`) templates + dynamic manifests / CSP inventory | `hedron[jinja]` | Supported |
| Celery / RQ `JobBackend` bridges | `hedron_core.jobs_celery` / `jobs_rq` | Supported optional bridges |
| Auto (inspectable object rendering) | Core (`hedron`) — no extra | Supported |
| DataTable / DataEditor | `hedron[data]` | Supported |
| Component Explorer (dev) | `hedron[dev]` | Supported for local diagnostics; some live traces Deferred (`EXPLORER-10-001`) |

Pin package versions in production. “Supported” does not mean a commercial SLA or
guaranteed multi-worker live-transport proof — see [STATUS](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md) Deferred rows.

## Supported examples

- Live interaction sample (poll + token stream + SSE + Job SSE + WebSocket accept +
  preload):
  [`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction).
  Prefer polling behind load balancers until your own ops evidence covers SSE/WS
  backpressure ([live interaction guide](live-interaction.md)).
- FastAPI / Flask / Django reference apps — [runnable examples](../examples/runnable.md)

## Treat as Alpha / more volatile

- `hedron-charts` and chart backends
- `hedron-sample-kit` (plugin sample)

## Deferred (do not market as Supported)

- First-party camera/microphone capture UI → **0.15**
- Full multi-engine adapter live browser matrix → owned `0.11.x` Deferred (`LIVE-011-BROWSER`)
- Full multi-engine FastAPI live browser matrix and some Explorer live traces → owned `0.10.x` Deferred rows in STATUS
- Load/proxy backpressure evidence for live transports → `PERF-10-001`

## Recommended install

```bash
pip install "hedron>=0.11.0" "uvicorn[standard]"
hedron new my-app
cd my-app
pip install -e .   # or: uv sync
uvicorn app:app --reload
```

Extras: `"hedron[data]"`, `"hedron[charts]"` (Alpha), `"hedron[jinja]"`, `"hedron[dev]"`.

## Next reading

- [Upgrade](upgrade.md) · [Evaluate](evaluate.md) · [Roadmap](roadmap.md) · [Live interaction](live-interaction.md)
