# Enterprise diligence

Short diligence sheet for security, procurement, and architecture reviewers. Product
fit: [Evaluate Hedron](evaluate.md) · readiness: [What’s ready](whats-ready.md) ·
[Production readiness](production-readiness.md) · [Design principles](design-principles.md).

## Project facts

| Item | Value |
|---|---|
| License | MIT |
| Published train | **0.11.0** (Beta packages) |
| Scheduled 1.0 / commercial SLA | **None** |
| Support | Community GitHub Issues only — [Support](support.md) |
| Primary maintainer contact | Package author metadata / GitHub org owner |
| Security disclosure | GitHub [security advisories](https://github.com/eddiethedean/hedron/security/advisories/new) (preferred); alternate email in [SECURITY.md](../SECURITY.md) |
| Conduct reports | **Not** security advisories — see [Code of Conduct](../CODE_OF_CONDUCT.md) |

## Trust boundaries

- Hedron provides secure HTML defaults (escaping, CSRF profiles, SafeUrl/TrustedHtml).
- **You own** authentication, authorization, persistence, and **multi-tenant isolation**.
- Tenant-scoped caches, jobs, and fragment allowlists are application responsibility —
  see [Threat model](threat-model.md) and [Cache](../api/CACHE.md).
- Third-party plugins are out of security scope until you review them
  ([Plugin authoring](plugin-authoring.md)).
- Host-framework CVEs (FastAPI, Django, Flask) are reported upstream.

## Multi-tenant checklist (you own)

- [ ] Cache keys include tenant (or use `no-store` / private per-user scopes)
- [ ] Job backends authorize by tenant before status SSE/poll
- [ ] Fragment regions and OOB targets cannot leak cross-tenant HTML
- [ ] Session cookies and CSRF secrets are per-environment; never shared across tenants

## Dependency and pin policy

- Coordinate on published trains; pin `hedron` and extras in your lockfile.
- Runtime ranges: [COMPATIBILITY.md](../COMPATIBILITY.md) (FastAPI/Pydantic pins are intentionally tight).
- **Patch expectation:** community best-effort; critical security fixes are prioritized on
  the current train. There is **no contractual patch SLA**.

## Supply-chain evidence (consume)

Maintainer scripts produce SBOM / license inventory / evidence bundles at cut time:

| Artifact | How to obtain |
|---|---|
| SBOM | [`scripts/generate_sbom.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/generate_sbom.py) / release evidence |
| License inventory | [`scripts/license_inventory.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/license_inventory.py) |
| Evidence bundle | [`scripts/build_evidence_bundle.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/build_evidence_bundle.py) |
| Script index | [`scripts/README.md`](https://github.com/eddiethedean/hedron/blob/main/scripts/README.md) |

Consume from published GitHub Releases when attached; otherwise regenerate from a tagged
checkout. Formats are maintainer-oriented (not a marketed SLSA attestation product).

## Evidence honesty

Live SSE/WebSocket **APIs** ship on FastAPI; full multi-engine live browser matrix and
load/proxy backpressure rows remain **Deferred** in [What's ready](whats-ready.md). Treat
“Supported” in adopter docs as capability claims with the Deferred caveats on
[What’s ready](whats-ready.md) — not as a warranty.

## Flask / Django Supported surface (summary)

| Surface | 0.11 | Notes |
|---|---|---|
| Portable components + HTMX fragment helpers | Supported matrix | — |
| Official HTMX SSE helpers | FastAPI only | Adapters: polling |
| Django QuerySet as first-party DataSource | Supported (D-046) | App-owned authorized base QS |
| Django forms bridge | Supported (D-046) | Widgets / CSRF / errors |

## Accessibility posture

Hedron documents author checklists and component contracts
([Accessibility](accessibility.md)). There is **no WCAG conformance claim** for your
application — you own audits and remediation.

## Bus factor

Hedron is a small open-source project. Budget for community response times and pin
versions accordingly. There is no paid support contract or succession SLA.
