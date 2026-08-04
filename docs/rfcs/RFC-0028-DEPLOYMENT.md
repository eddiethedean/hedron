# RFC-0028: Deployment

**Status:** Accepted

**Revision:** 2026-08-03 — D-035 separated portable deployment obligations from ASGI, WSGI, and
framework-specific capabilities.

## Production model

The flagship Hedron application deploys as an ordinary FastAPI ASGI application. Flask and Django
adapters deploy through their host framework's supported WSGI and/or ASGI paths. Production builds
precompile legacy experimental HDN where present and scoped CSS, fingerprint static assets, validate the registry and framework-owned
route metadata, and emit immutable manifests. Runtime compilation is not required.

The deployment path requires no Node.js process. Browser dependencies are vendored or installed as
package assets and served through the host framework's static-file integration or an external static
host using the same manifest.

## Operational requirements

- Configuration is explicit by environment and never weakens security silently.
- Proxies, ASGI `root_path`, WSGI `SCRIPT_NAME`, mounts, HTTPS, forwarded headers, and cache headers
  follow the selected framework and server guidance.
- Multiple workers share no correctness-critical in-process component state.
- Health checks distinguish process health from optional integration readiness.
- Logs and traces redact secrets and include stable route/component identifiers.
- Explorer is absent in production unless deliberately secured and enabled.
- Capability documentation names the reference ASGI/WSGI servers and does not promise request
  disconnect cancellation where the deployment stack cannot expose it.
- External cache and job backends define readiness, failure isolation, serialization/versioning,
  shutdown, and multi-worker correctness contracts.

## Acceptance criteria

- The FastAPI reference application runs with multiple workers in a container and behind a
  path-prefixed reverse proxy with external static assets and cache/job conformance implementations.
- Native Flask and Django reference slices prove their advertised WSGI/ASGI deployment capabilities.
- Offline startup succeeds with all official assets local.
- Build manifests are reproducible and validate at startup.
- Deployment documentation covers workers, lifespan, static assets, caches, jobs, and graceful shutdown.
- Health checks distinguish liveness from readiness and are tested during dependency degradation.
