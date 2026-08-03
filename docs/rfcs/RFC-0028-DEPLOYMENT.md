# RFC-0028: Deployment

**Status:** Proposed

## Production model

Hedron deploys as an ordinary FastAPI ASGI application. Production builds precompile HDN and scoped CSS, fingerprint static assets, validate the registry and OpenAPI document, and emit immutable manifests. Runtime compilation is not required.

The deployment path requires no Node.js process. Browser dependencies are vendored or installed as package assets and served with Starlette `StaticFiles` or an external static host using the same manifest.

## Operational requirements

- Configuration is explicit by environment and never weakens security silently.
- Proxies, root paths, mounts, HTTPS, forwarded headers, and cache headers follow FastAPI/Starlette deployment guidance.
- Multiple workers share no correctness-critical in-process component state.
- Health checks distinguish process health from optional integration readiness.
- Logs and traces redact secrets and include stable route/component identifiers.
- Explorer is absent in production unless deliberately secured and enabled.

## Acceptance criteria

- The reference application runs in a container and behind a path-prefixed reverse proxy.
- Offline startup succeeds with all official assets local.
- Build manifests are reproducible and validate at startup.
- Deployment documentation covers workers, lifespan, static assets, caches, jobs, and graceful shutdown.

