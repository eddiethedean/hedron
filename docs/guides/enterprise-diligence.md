# Enterprise diligence

Short diligence sheet for security, procurement, and architecture reviewers. Product
fit: [Evaluate Hedron](evaluate.md) · readiness: [What’s ready](whats-ready.md) ·
[Production readiness](production-readiness.md).

## Project facts

| Item | Value |
|---|---|
| License | MIT |
| Published train | **0.10.1** (Beta packages) |
| Scheduled 1.0 / commercial SLA | **None** |
| Support | Community GitHub Issues only — [Support](support.md) |
| Primary maintainer contact | Package author metadata / GitHub org owner |
| Security disclosure | GitHub [security advisories](https://github.com/eddiethedean/hedron/security/advisories/new) (preferred); alternate email in [SECURITY.md](../SECURITY.md) |
| Conduct reports | **Not** security advisories — see [Code of Conduct](../CODE_OF_CONDUCT.md) |

## Trust boundaries

- Hedron provides secure HTML defaults (escaping, CSRF profiles, SafeUrl/TrustedHtml).
- You own authentication, authorization, persistence, and multi-tenant isolation.
- Third-party plugins are out of security scope until you review them
  ([Plugin authoring](plugin-authoring.md)).
- Host-framework CVEs (FastAPI, Django, Flask) are reported upstream.

## Dependency and pin policy

- Coordinate on published trains; pin `hedron` and extras in your lockfile.
- Runtime ranges: [COMPATIBILITY.md](../COMPATIBILITY.md) (FastAPI/Pydantic pins are intentionally tight).
- Supply-chain artifacts for cuts: SBOM / license inventory via maintainer scripts
  ([`scripts/README.md`](https://github.com/eddiethedean/hedron/blob/main/scripts/README.md)).

## Evidence honesty

Live SSE/WebSocket **APIs** ship on FastAPI; full multi-engine live browser matrix and
load/proxy backpressure rows remain **Deferred** in [STATUS](../STATUS.md). Treat
“Supported” in adopter docs as capability claims with the Deferred caveats on
[What’s ready](whats-ready.md) — not as a warranty.

## Flask / Django Supported surface (summary)

| Surface | 0.10 | Planned deeper work |
|---|---|---|
| Portable components + HTMX fragment helpers | Supported matrix | — |
| Official HTMX SSE helpers | FastAPI only | Adapters: polling |
| Django QuerySet as first-party DataSource | Deferred | **0.11** |
| Hedron-owned Django forms depth | Deferred | **0.11** |

## Bus factor

Hedron is a small open-source project. Budget for community response times and pin
versions accordingly. There is no paid support contract.
