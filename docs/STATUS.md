# Specification and implementation status

**Roadmap position:** phase 0.8 **cut-ready** as `0.8.0` on repository `main`
(hardening and compatibility baseline). **PyPI today** publishes the prior train (**0.7.x**) until
`v0.8.0` is tagged.
**Date:** 2026-08-03
**Implementation:** `hedron` / `hedron-core` / `hedron-explorer` / `hedron-sample-kit` /
`hedron-data` / `hedron-charts` / `hedron-flask` / `hedron-django` `0.8.0` (MIT licensed, D-033)
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`; Alpha — `hedron-charts`, `hedron-sample-kit`.

**Next capability phase:** 0.9 deepens native Flask/Django integration and promotes a bounded
QuerySet DataSource if its gate passes. SSE/live transport remains assigned to 0.10 (D-037/D-038).

**Authoring direction:** D-040/RFC-0031 select a separate, optional `hedron-jinja` integration for
trusted application templates in phase 0.11. Typed Python components remain canonical, and Jinja is
not shipped on the current train. The experimental HDN language, `RenderProgram`, and compile/load/
run APIs remain available only for critical fixes and migration before staged removal in 0.13.

## Phase 0.8 evidence

- Closure index: [release-gate-0.8.toml](acceptance/release-gate-0.8.toml)
  (`Verified` or owned `Deferred`).
- Stability: [api/STABILITY.md](api/STABILITY.md).
- Compatibility / deprecation: [COMPATIBILITY.md](COMPATIBILITY.md).
- Upgrade: [guides/upgrade.md](guides/upgrade.md).
- Threat model: [guides/threat-model.md](guides/threat-model.md).
- Performance budgets: [PERFORMANCE_BUDGETS.md](PERFORMANCE_BUDGETS.md).
- Supply chain: `scripts/build_evidence_bundle.py` (SBOM, licenses, asset audit).
- Cut procedure: [RELEASE.md](RELEASE.md) (`## Cut v0.8.0`).
- After publish: enter phase 0.9 via [acceptance/RELEASE_0_9.md](acceptance/RELEASE_0_9.md).
