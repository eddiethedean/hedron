# Edron 0.8 acceptance

**Status:** Implemented and release-verified in-tree; publication pending

**Package:** `edron==0.8.0` · compatible Hedron train `0.66.x`

Phase 0.8 is the Edron deployment and host-integration slice. It makes deployment assumptions
explicit and reviewable without adding a process supervisor, cloud provisioner, secret manager, or
second runtime authority. Profile resolution is read-only and does not import or execute the target
application.

Public contract outline: [Edron release roadmap](../EDRON_ROADMAP.md) ·
[deployment guide](../guides/edron-deployment.md) ·
[upgrade fixtures](upgrade-fixtures-08.md).

| Gate | Evidence required | State |
|---|---|---|
| `EDR-08-PROFILE` | Versioned local, single-process, reverse-proxy, container, orchestrated, Workbench, and Posit Connect profiles with deterministic precedence and refusal diagnostics | Implemented |
| `EDR-08-EDGE` | Mounted-path URL, redirect, cookie, CSRF, CSP, static asset, build-manifest, cache, HTTP, HTMX, and no-JavaScript contract | Implemented |
| `EDR-08-HOST` | Explicit ASGI-first and conditional host maturity matrix with launch order, version floors, limits, fallback, and ejection paths | Implemented |
| `EDR-08-OPS` | Bounded profile-aware checks for secrets, readiness, workers, graceful shutdown, state/job durability, proxy trust, and redacted remediation | Implemented |
| `EDR-08-SUPPLY` | Deterministic artifact records, wheel/sdist coverage, offline-install checks, dependency/license/SBOM/provenance evidence, and exact verification commands | Implemented |
| `EDR-08-UPGRADE` | Pinned-train preflight, manifest rebuild, two-version upgrade, stale-asset, failed-start, rollback, and application-owned migration boundaries | Implemented |
| `EDR-08-REGRESSION` | Edron 0.7 regression plus phase 0.8 profile, proxy, host, artifact, security, and recovery tests | Implemented |

The packet does not authorize a cloud deployment service, Docker/Kubernetes/Workbench operator,
runtime package installation, arbitrary forwarded-header trust, Flask/Django Edron page-class
parity, notebook production hosting, or automatic reversal of application-owned data migrations.
