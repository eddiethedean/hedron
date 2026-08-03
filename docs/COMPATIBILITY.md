# Compatibility policy

**Status:** Accepted for the phase 0.0 baseline  
**Reviewed:** 2026-08-02

## Initial runtime ranges

| Dependency | `v0.1.0`/`v0.2.0` baseline | Policy |
|---|---|---|
| Python | CPython 3.11, 3.12, 3.13, and 3.14 | `requires-python = ">=3.11,<3.15"`; 3.15 prereleases are not supported. |
| FastAPI | `>=0.141.1,<0.142` | Required by `hedron`, not `hedron-core`; expand only after adapter conformance. |
| Pydantic | `>=2.13.4,<2.14` | Required by `hedron-core`; Hedron shields public contracts from Pydantic internals. |
| Starlette | FastAPI-managed compatible version | No independent direct pin unless implementation use requires one; test the resolved FastAPI set. |
| HTMX | Bundled 2.0.10; compatible contract `>=2.0,<3.0` | Official assets pin an exact reviewed version and integrity digest per Hedron release. |

Python 3.11 and 3.12 remain supported by upstream security fixes through 2027 and 2028 respectively; 3.13 and 3.14 are in bugfix support. Python 3.15 is prerelease as of this review. FastAPI 0.141.1 and Pydantic 2.13.4 are the latest stable releases reviewed for the baseline. HTMX’s official repository documents 2.0.10, while later major-line work is not used for the initial contract.

The exact lockfile records full transitive versions. Patch releases enter through dependency-update pull requests and must pass the complete compatibility suite before the supported range or bundled asset changes.

Hedron uses documented public upstream APIs. Compatibility shims are isolated by adapter and removed according to the deprecation policy.

## Public stability

- Pre-1.0 APIs may change through accepted RFC revisions and release notes.
- 1.0 public contracts follow semantic versioning.
- Deprecations include diagnostics, replacement guidance, and at least the documented support window.
- Rendered markup, registry metadata, HDN compiled formats, CSS symbol manifests, and plugin protocols each declare whether they are public, versioned artifacts or private details.

## Cross-package compatibility

Every optional package declares compatible Hedron and upstream ranges. The plugin loader rejects incompatible major versions at startup. Pure-Python behavior remains the conformance reference if native acceleration is introduced.

## Browser compatibility

The baseline targets browsers with native ES modules, Custom Elements, CSS custom properties, `fetch`, `AbortController`, and the selected HTMX version. CI tests the current and previous stable Chromium and Firefox channels plus WebKit coverage; Safari current and previous receive release-candidate verification. Internet Explorer is unsupported. Enhanced widgets document additional capabilities and accessible fallbacks.

CPython default builds are normative. Free-threaded CPython and PyPy are informational until separately promoted through the compatibility matrix.

## Release evidence

Compatibility claims require clean-install, package, adapter, browser, OpenAPI, compiled-artifact, and reference-application tests. The matrix above is the initial tested baseline; changing it requires compatibility evidence and an updated decision or RFC.

## Primary sources reviewed

- [Python version status](https://devguide.python.org/versions/)
- [FastAPI package metadata and releases](https://pypi.org/project/fastapi/)
- [Pydantic package metadata and releases](https://pypi.org/project/pydantic/)
- [HTMX official repository](https://github.com/bigskysoftware/htmx)
