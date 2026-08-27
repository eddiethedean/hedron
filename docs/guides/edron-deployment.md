# Edron deployment

Edron 0.8 adds a read-only deployment check around the native Hedron ASGI application. It validates
declared assumptions before the host starts the app; it does not launch a process, discover cloud
infrastructure, install packages, or import application code.

## Profiles

Use one explicit profile for the deployment boundary:

| Profile | Intended boundary | Default claim |
|---|---|---|
| `local` | Development on a laptop | Non-production, loopback, one worker, process-local state |
| `single-process` | Production behind a local supervisor/proxy | Production, one worker, process-local state unless declared otherwise |
| `reverse-proxy` | Mounted ASGI app behind nginx/Caddy/ALB | Production, explicit root path and proxy trust |
| `container` | A container with a platform-owned edge | Production, explicit external bind, one worker by default |
| `orchestrated` | Kubernetes or another multi-process platform | Production, shared state/job backends required for multiple workers |
| `workbench` | Posit Workbench handoff | ASGI host handoff; launch-time mount supplied by `hedron-posit` |
| `posit-connect` | Posit Connect deployment | ASGI host handoff; durable public URL is explicit and platform-owned |

Environment values use the existing native names where applicable:
`HEDRON_ENV`, `HEDRON_ROOT_PATH`, `HEDRON_BUILD_DIR`, and `HEDRON_SESSION_SECRET`. Edron-specific
aliases include `EDRON_DEPLOYMENT_PROFILE`, `EDRON_EXTERNAL_URL`, `EDRON_WORKERS`, and
`EDRON_TRUST_PROXY`. Explicit CLI values and environment values are both recorded; conflicting
values fail the check instead of being silently resolved.

## Preflight

Run the local profile without importing your app:

```console
edron deploy-check --profile local
```

For production, build the native assets first and inject the session secret at runtime:

```console
hedron build
edron deploy-check --profile reverse-proxy \
  --root-path /sales \
  --build-dir .hedron/build \
  --external-url https://apps.example.test/sales \
  --trust-proxy 10.0.0.10
```

Machine-readable output is suitable for CI:

```console
edron deploy-check --profile reverse-proxy --format json
edron deploy-check --profile reverse-proxy --format sarif
```

The check requires `manifest.json` and an approved runtime secret source for production profiles.
Use `--secret-source` for a non-environment platform reference; the reference is metadata only and
is never read as a secret.

## Multi-worker and recovery boundary

Multiple workers require both `--state-backend shared` and `--job-backend shared`:

```console
edron deploy-check --profile orchestrated --workers 2 \
  --state-backend shared --job-backend shared
```

This declares an operator claim; Edron does not provision or test the backend. The application owns
data migrations, queued work, secrets rotation, external side effects, and user files. Rollback
returns to a prior application artifact and package pin only.

## Host maturity

Edron is ASGI-first. `hedron-posit` may supply a Supported Workbench or Posit Connect handoff when
its native version, lifecycle, mount, cookie, URL, and worker evidence is present. Notebook preview
and remote tooling remain tooling-grade or Experimental. Flask/Django Edron page-class parity is not
part of the 0.8 contract; use their native Hedron adapters and their own host evidence.

## Diagnostics

`doctor` can include the same deployment report while inspecting a trusted app:

```console
edron doctor app:app --profile reverse-proxy --format json
```

The report is bounded and redacted. It distinguishes process-local from shared state/job claims and
never prints secret values, imports arbitrary callbacks, trusts an inbound `Host` header, or probes
external services.
