# Ship a Hedron app

One landing page for production shipping on the living **0.25** train. Capability maturity
(Supported vs Experimental) lives only on [What’s ready](whats-ready.md).

| Need | Go here |
|---|---|
| **Adopter checklist** (secrets, build, CSRF, Explorer, HA) | [Ship to production](ship-to-production.md) |
| Dockerfile / proxy / host parity | [Deployment](deployment.md) |
| Security defaults | [Security](security.md) · [Threat model](threat-model.md) |
| Compatibility pins & charts packaging | [Compatibility](../COMPATIBILITY.md) |
| Kitchen-sink sample | [Reference app](../examples/reference-app.md) |
| Support / SLA honesty | [Support](support.md) |
| Enterprise diligence | [Enterprise diligence](enterprise-diligence.md) |
| Evaluate fit first | [Evaluate Hedron](evaluate.md) · [What’s ready](whats-ready.md) |

Maintainer trust-program depth (not required to ship an app):

- [Production-quality maturity](production-quality.md)
- [Production readiness](production-readiness.md)
- [Production archetype API](../api/PRODUCTION_ARCHETYPE.md)

**Pin:** `hedron>=0.25.0,<0.26` (and matching adapters/extras) in your lockfile.

This page is the single Ship hub (Guides → Ops). Evaluate links here; it does not
re-home the checklist.
