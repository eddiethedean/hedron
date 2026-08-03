# Packaging and deployment acceptance

## Packages

- [ ] `hedron-core` installs and imports without FastAPI, Flask, or Django.
- [ ] `hedron-flask` and `hedron-django` do not install FastAPI.
- [ ] Optional integrations import lazily and publish compatibility ranges.
- [ ] Wheels and source distributions contain typing metadata, HDN/CSS data, browser assets, and licenses.
- [ ] Missing extras produce exact install instructions without breaking unrelated imports.

## Deployment

- [ ] The reference FastAPI application runs with multiple workers, in a container, and behind a prefixed reverse proxy.
- [ ] Production startup uses precompiled deterministic manifests and succeeds offline.
- [ ] Static assets work through `StaticFiles` and an external host configuration.
- [ ] Lifespan, graceful shutdown, caches, background tasks, and external jobs are documented.
- [ ] Explorer is absent from default production routes.
- [ ] Dependency, browser-asset, and component-package licenses and vulnerabilities are auditable.

## Exit

Installation and smoke tests pass on every supported Python/platform target using only released artifacts.

