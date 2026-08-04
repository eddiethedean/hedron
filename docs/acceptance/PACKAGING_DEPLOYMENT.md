# Packaging and deployment acceptance

## Phase 0.1 (`v0.1.0`) subset

- [x] `hedron-core` installs and imports without FastAPI, Flask, or Django.
- [x] Wheel and sdist build with Hatchling; clean-install smoke renders a `Page`.
- [x] Typed marker (`py.typed`), README, changelog, authors, classifiers, and project URLs ship with the distribution.
- [x] Root `LICENSE` and `[project].license` metadata are present (MIT; D-033).
- [x] Release workflow verifies tag/version/changelog sync and refuses publish without a license.

## Packages

- [x] `hedron-core` installs and imports without FastAPI, Flask, or Django.
- [x] `hedron-flask` and `hedron-django` do not install FastAPI, directly or through required
  Explorer/development dependencies. *(ADP-FLK-003 / ADP-DJG-003 / PKG-08-001)*
- [x] Optional integrations import lazily and publish compatibility ranges.
- [x] Wheels and source distributions contain typing metadata, browser assets (HTMX / disclose), and licenses. *(Application CSS ships via project builds; templates remain application source.)*
- [x] Missing extras produce exact install instructions without breaking unrelated imports. *(`hedron[data]` / `hedron-data`; other adapters remain later)*

## Deployment

- [x] The reference FastAPI application runs with multiple workers, in a container, behind a
  prefixed reverse proxy, with external static assets and executable cache/job conformance
  implementations. *(phase 0.7B; OPS-002 / OPS-003)*
- [x] Production startup uses precompiled deterministic manifests and fails closed when missing/invalid (`HED-BUILD-0003`); runtime CSS compile is denied offline. *(phase 0.3)*
- [x] Static assets work through `StaticFiles` (`/hedron-static`, `/hedron-assets`). *(External CDN host configuration remains later.)*
- [x] Lifespan, graceful shutdown, caches, background tasks, and external jobs are documented and
  exercised under termination/degradation. *(phase 0.7B; OPS-004–OPS-007)*
- [x] Explorer is absent from default production routes (`explorer="off"`; verified in FastAPI MVP tests).
- [x] Dependency, browser-asset, and component-package licenses and vulnerabilities are auditable;
  phase 0.8 produces an SBOM, provenance, and retained release evidence bundle.
  *(`SUP-08-*` / `scripts/build_evidence_bundle.py`)*

## Exit

Installation and smoke tests pass on every supported Python/platform target using only released
artifacts. Phase 0.7+ completion requires linked evidence IDs under [EVIDENCE.md](EVIDENCE.md).
