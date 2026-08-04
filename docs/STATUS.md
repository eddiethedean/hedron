# Specification and implementation status

**Roadmap position:** phase 0.9 implementation on repository `main`.
**Date:** 2026-08-04
**Implementation:** `hedron` / `hedron-core` / `hedron-explorer` / `hedron-sample-kit` /
`hedron-data` / `hedron-charts` / `hedron-flask` / `hedron-django` / `hedron-jinja` `0.9.0`
(MIT licensed, D-033)
**Package maturity:** Beta — `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, `hedron-jinja`; Alpha — `hedron-charts`, `hedron-sample-kit`.

**Phase focus:** replace HDN with HDJ, an optional explicit `.hdj` format over Jinja/HTML/HTMX that
preserves advanced HTML/CSS/JS freedom and Hedron metadata/security integration. Native
Flask/Django depth moves to 0.11; SSE/live transport remains assigned to 0.10.

**Authoring break:** D-041/D-043/RFC-0031 remove HDN in phase 0.9 with no compatibility mode or converter.
The parser, evaluator, formatter, render program, discovery, artifacts, public APIs, CLI/Explorer
paths, examples, and tests are gone. `hedron-jinja` is the optional replacement; typed Python
components remain canonical.

## Phase 0.8 evidence

- Closure index: [release-gate-0.8.toml](acceptance/release-gate-0.8.toml)
  (`Verified` or owned `Deferred`).
- Stability: [api/STABILITY.md](api/STABILITY.md).
- Compatibility / deprecation: [COMPATIBILITY.md](COMPATIBILITY.md).
- Upgrade: [guides/upgrade.md](guides/upgrade.md).
- Threat model: [guides/threat-model.md](guides/threat-model.md).
- Performance budgets: [PERFORMANCE_BUDGETS.md](PERFORMANCE_BUDGETS.md).
- Supply chain: `scripts/build_evidence_bundle.py` (SBOM, licenses, asset audit).
- Current gate: [acceptance/RELEASE_0_9.md](acceptance/RELEASE_0_9.md) and
  [acceptance/release-gate-0.9.toml](acceptance/release-gate-0.9.toml).
- Cut procedure: [RELEASE.md](RELEASE.md) (`## Build and cut v0.9.0`).
