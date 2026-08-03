# Engineering baseline

**Status:** Accepted for the phase 0.0 baseline

## Toolchain

- `uv` manages the development workspace, lockfile, environments, and release test installs.
- Hatchling builds wheels and source distributions.
- Ruff provides formatting and linting.
- Pyright runs strict type checking on public packages; documented narrow exceptions require justification.
- pytest, pytest-anyio, httpx, and browser tooling implement the test layers.
- Markdown links and the specification indexes are checked in CI.

These are contributor tools, not runtime dependencies. Application users may install Hedron with any standards-compliant Python package installer.

## CI gates

Every change runs:

1. formatting, lint, and type checks;
2. unit, snapshot, conformance, integration, and security tests relevant to the change;
3. package build and clean-install smoke tests;
4. documentation link, index, terminology, and RFC-status checks;
5. compatibility tests for the supported Python and upstream ranges;
6. browser and accessibility tests when emitted markup or browser assets change;
7. non-blocking benchmark comparison until a release budget becomes normative.

Beginning with the phase 0.6 closure gate, CI status is necessary but not sufficient for a release
claim. Stable evidence IDs map requirements to exact commands, supported matrix dimensions, retained
artifacts, and owners under [acceptance/EVIDENCE.md](acceptance/EVIDENCE.md). Before `v0.7.0`, the
release checker consumes a machine-readable gate manifest and fails closed on missing or unowned
evidence.

The default CPython matrix covers 3.11, 3.12, 3.13, and 3.14. Linux runs the full suite; macOS and Windows run package, core, and representative integration tests. Free-threaded CPython and PyPy are informational until separately promoted.

## Quality policy

- Warnings are not ignored globally; every suppression is scoped and explained.
- Public functions, classes, protocols, decorators, and configuration have typing and documentation.
- Generated artifacts are deterministic or declare their intentional variability.
- Tests do not depend on network access except separately labeled upstream compatibility jobs.
- Security, accessibility, and compatibility regressions block release.
- A framework capability is advertised only when its native framework/server evidence is retained;
  portable conformance cannot manufacture ASGI, WSGI, or framework-specific guarantees.

## Licensing policy

Hedron uses the MIT License (D-033). The repository root and each publishable distribution include `LICENSE`, and package metadata declares `license = "MIT"`. The release workflow refuses to publish when those artifacts are missing.
