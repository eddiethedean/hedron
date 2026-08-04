# Specification and implementation status

**Roadmap position:** phase 0.9 implementation on repository `main`.
**Date:** 2026-08-04
**Implementation:** `hedron` / `hedron-core` / `hedron-explorer` / `hedron-sample-kit` /
`hedron-data` / `hedron-charts` / `hedron-flask` / `hedron-django` / `hedron-jinja` `0.9.0`
(MIT licensed, D-033)
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`; Alpha — `hedron-charts`, `hedron-sample-kit`.

**Phase focus:** replace HDN with optional strict Jinja authoring. Native Flask/Django depth moves to
0.11; SSE/live transport remains assigned to 0.10.

**Authoring break:** D-041/RFC-0031 remove HDN in phase 0.9 with no compatibility mode or converter.
The parser, evaluator, formatter, render program, discovery, artifacts, public APIs, CLI/Explorer
paths, examples, and tests are gone. `hedron-jinja` is the optional replacement; typed Python
components remain canonical.

## Phase 0.8 evidence

- Closure index: [release-gate-0.8.toml](docs/acceptance/release-gate-0.8.toml)
  (`Verified` or owned `Deferred`).
- Stability: [docs/api/STABILITY.md](docs/api/STABILITY.md).
- Compatibility / deprecation: [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md).
- Upgrade: [docs/guides/upgrade.md](docs/guides/upgrade.md).
- Threat model: [docs/guides/threat-model.md](docs/guides/threat-model.md).
- Performance budgets: [docs/PERFORMANCE_BUDGETS.md](docs/PERFORMANCE_BUDGETS.md).
- Supply chain: `scripts/build_evidence_bundle.py` (SBOM, licenses, asset audit).
- Current gate: [RELEASE_0_9.md](docs/acceptance/RELEASE_0_9.md) and
  [release-gate-0.9.toml](docs/acceptance/release-gate-0.9.toml).
- Cut procedure: [docs/RELEASE.md](docs/RELEASE.md) (`## Build and cut v0.9.0`).
