# Packaging and deployment acceptance

## Phase 0.1 (`v0.1.0`) subset

- [x] `hedron-core` installs and imports without FastAPI, Flask, or Django.
- [x] Wheel and sdist build with Hatchling; clean-install smoke renders a `Page`.
- [x] Typed marker (`py.typed`), README, changelog, authors, classifiers, and project URLs ship with the distribution.
- [x] Root `LICENSE` and `[project].license` metadata are present (MIT; D-033).
- [x] Release workflow verifies tag/version/changelog sync and refuses publish without a license.

## Packages

- [x] `hedron-core` installs and imports without FastAPI, Flask, or Django.
- [ ] `hedron-flask` and `hedron-django` do not install FastAPI. *(phase 0.7)*
- [ ] Optional integrations import lazily and publish compatibility ranges. *(later phases)*
- [x] Wheels and source distributions contain typing metadata, browser assets (HTMX / disclose), and licenses. *(Application HDN/CSS ship via project builds, not the framework wheel.)*
- [ ] Missing extras produce exact install instructions without breaking unrelated imports. *(later — adapters/extras beyond `hedron[dev]`)*

## Deployment

- [ ] The reference FastAPI application runs with multiple workers, in a container, and behind a prefixed reverse proxy. *(later phases)*
- [x] Production startup uses precompiled deterministic manifests and fails closed when missing/invalid (`HED-BUILD-0003`); runtime HDN/CSS compile is denied offline. *(phase 0.3)*
- [x] Static assets work through `StaticFiles` (`/hedron-static`, `/hedron-assets`). *(External CDN host configuration remains later.)*
- [ ] Lifespan, graceful shutdown, caches, background tasks, and external jobs are documented. *(later phases)*
- [x] Explorer is absent from default production routes (`explorer="off"`; verified in FastAPI MVP tests).
- [ ] Dependency, browser-asset, and component-package licenses and vulnerabilities are auditable. *(later phases)*

## Exit

Installation and smoke tests pass on every supported Python/platform target using only released artifacts.

