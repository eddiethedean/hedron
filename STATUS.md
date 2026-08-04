# Specification and implementation status

**Roadmap position:** phase 0.8 **cut-ready** as `0.8.0` on repository `main`
(API freeze and hardening). **PyPI today** publishes the prior train (**0.7.x**) until
`v0.8.0` is tagged.
**Date:** 2026-08-03
**Implementation:** `hedron` / `hedron-core` / `hedron-explorer` / `hedron-sample-kit` /
`hedron-data` / `hedron-charts` / `hedron-flask` / `hedron-django` `0.8.0` (MIT licensed, D-033)
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`; Alpha — `hedron-charts`, `hedron-sample-kit`.

**Feature freeze active:** phase 0.8 adds no new product subsystem, framework adapter, or
transport. SSE live transport and Django QuerySet DataSource remain Deferred (D-036, D-037).

## Phase 0.8 evidence

- Closure index: [release-gate-0.8.toml](docs/acceptance/release-gate-0.8.toml)
  (`Verified` or owned `Deferred`).
- Stability: [docs/api/STABILITY.md](docs/api/STABILITY.md).
- Compatibility / deprecation: [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md).
- Upgrade: [docs/guides/upgrade.md](docs/guides/upgrade.md).
- Threat model: [docs/guides/threat-model.md](docs/guides/threat-model.md).
- Performance budgets: [docs/PERFORMANCE_BUDGETS.md](docs/PERFORMANCE_BUDGETS.md).
- Supply chain: `scripts/build_evidence_bundle.py` (SBOM, licenses, asset audit).
- Cut procedure: [docs/RELEASE.md](docs/RELEASE.md) (`## Cut v0.8.0`).
- After publish: rehearse `1.0.0rcN` via [RELEASE_1_0.md](docs/acceptance/RELEASE_1_0.md) and
  `scripts/rehearse_rc.py`.
