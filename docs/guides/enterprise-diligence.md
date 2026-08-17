# Enterprise diligence

Short diligence sheet for security, procurement, and architecture reviewers.
**Capability maturity:** [What’s ready](whats-ready.md) (sole source of truth).
**Fit:** [Evaluate Hedron](evaluate.md) · **Ops:** [Ship a Hedron app](ship.md) ·
[Design principles](design-principles.md).

## Project facts

| Item | Value |
|---|---|
| License | MIT |
| Current version | **v0.47.0** in-tree (pin `hedron>=0.47.0,<0.48`; PyPI still `0.46.0`, tag/PyPI deferred) |
| Scheduled 1.0 / commercial SLA | **None** |
| Support | Community GitHub Issues only — [Support](support.md) |
| Primary maintainer contact | Package author metadata / GitHub org owner |
| Security disclosure | GitHub [security advisories](https://github.com/eddiethedean/hedron/security/advisories/new) (preferred); alternate email in [SECURITY.md](../SECURITY.md) |
| Conduct reports | **Not** security advisories — see [Code of Conduct](../CODE_OF_CONDUCT.md) |

## Trust boundaries

- Hedron provides secure HTML defaults (escaping, CSRF profiles, SafeUrl/TrustedHtml).
- **You own** authentication, authorization, persistence, and **multi-tenant isolation**.
- There is **no first-party IdP / managed SSO product** — host frameworks own identity.
  Optional FastAPI helpers (`hedron.oidc`, `hedron.security` login CSRF / session
  stamps / auth rate limit / trusted headers) exist; apps must wire them
  ([Authentication](authentication.md), [Hardened sessions](hardened-sessions.md)).
- Tenant-scoped caches, jobs, and fragment allowlists are application responsibility —
  see [Threat model](threat-model.md), [Cache](../api/CACHE.md), and the
  [multi-tenant cookbook](multi-tenant.md).
- Third-party plugins are out of security scope until you review them
  ([Using plugins](plugin-consumer.md) · [Plugin authoring](plugin-authoring.md)).
- Host-framework CVEs (FastAPI, Django, Flask) are reported upstream.

## Multi-tenant checklist (you own)

- [ ] Cache keys include tenant (or use `no-store` / private per-user scopes)
- [ ] Job backends authorize by tenant before status SSE/poll
- [ ] Fragment regions and OOB targets cannot leak cross-tenant HTML
- [ ] Session cookies and CSRF secrets are per-environment; never shared across tenants

## Dependency and pin policy

- Coordinate on published trains; pin `hedron` and extras in your lockfile.
- Runtime ranges and conflict guidance: [COMPATIBILITY.md](../COMPATIBILITY.md)
  (FastAPI/Pydantic pins are intentionally tight).
- **Patch expectation:** community best-effort; critical security fixes are prioritized on
  the current train. There is **no contractual patch SLA**.

## Claims we never make

Hedron documentation and marketing **do not** claim:

- Commercial SLA, guaranteed patch cadence, or scheduled 1.0
- WCAG / legal / VPAT / ACR certification for your application
- Managed IdP / SSO product (optional helpers only — you own identity)
- SLSA product attestation or commercial compliance certification
- That every `hedron[extras]` widget is production-complete (CodeEditor is a host stub;
  TerminalView / device bridges are Experimental)

Trust-program priorities that close diligence caveats without inventing those claims:
[Production-quality maturity](production-quality.md).

## Compliance positioning (not certification)

Hedron is a library, not a hosted service. For GDPR / SOC 2 / HIPAA-style programs:

| Hedron provides | You own |
|---|---|
| Escaping defaults, CSRF profiles, SafeUrl / TrustedHtml | AuthN/AuthZ, retention, DPIAs, BAAs |
| Secure-defaults docs + optional evidence pack / SBOM scripts | Lockfiles, deploy controls, access reviews |
| Honest maturity labels (Beta, experimental live) | Choosing Supported surfaces and pins |

Hedron is **not** SOC 2 / ISO / HIPAA certified. Slot it into *your* control framework as
third-party open-source software with pinned versions and your own threat model review.

## Supply-chain evidence

Prefer GitHub Release assets for the latest **uploaded** tag **`v0.46.0`** (SBOM / license /
evidence-bundle) when
attached. If assets are missing, regenerate from the tagged checkout — see
[Evidence pack](evidence-pack.md). PyPI remains authoritative for package versions.
Maintainers should attach evidence bundles on release day when publishing a train tag.

## Evidence honesty

Live SSE/WebSocket **APIs** ship on FastAPI; full multi-engine live browser matrix and
load/proxy backpressure rows remain incomplete — see [What's ready](whats-ready.md).
Treat “Supported” as capability claims with those caveats, not as a warranty.

## Accessibility posture

Hedron documents author checklists and component contracts
([Accessibility](accessibility.md)). There is **no WCAG conformance claim** for your
application — you own audits and remediation.

## Bus factor

Expect a small maintainer set. Diligence should assume community-paced response times and
pin versions accordingly.
