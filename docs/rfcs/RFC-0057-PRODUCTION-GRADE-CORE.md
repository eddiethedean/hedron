# RFC-0057: Production-grade core, FastAPI flagship, and Explorer

**Status:** Accepted
**Phase:** 0.26 (`v0.26.0`)
**Stability:** `beta` (process / package-graduation contract)
**Evidence:** [RELEASE_0_26.md](../acceptance/RELEASE_0_26.md) ·
[release-gate-0.26.toml](../acceptance/release-gate-0.26.toml) ·
[production-grade-inventory-026.toml](../acceptance/production-grade-inventory-026.toml)
**Related:** D-038, D-053, D-054; [RFC-0056](RFC-0056-PRODUCTION-QUALITY.md);
[ROADMAP §0.26](../ROADMAP.md); [STABILITY.md](../api/STABILITY.md);
[STABLE_FACADE.md](../api/STABLE_FACADE.md)

## Summary

Apply the ROADMAP **production-grade package contract (0.26+)** to
`hedron-core`, `hedron`, and `hedron-explorer` for the documented
server-rendered CRUD/admin Supported surface. Baseline train is Published
**`v0.25.2`**. Beta maturity today is not the production-grade label; 0.26 is the
graduation that earns that label for the **declared inventory only**.

## Motivation

Phases 0.21–0.25 (D-053 / RFC-0056) raised adopter trust for the Supported
surface (human-AT protocol, CSRF composition, stable facade, `polling_only`,
production archetype). Remaining work is package-level graduation evidence:
machine-readable inventories, upgrade fixtures from `v0.25.2`, independent
security review of trust boundaries, multi-worker/Explorer operational proof,
and a Verified release packet — without promoting experimental live transports
or scheduling `1.0`.

## Design

### Packages in scope

| Package | Production-grade scope |
|---|---|
| `hedron-core` | Models, components, renderer, registry, security/interaction contracts, polling jobs, cache contracts, stable facade |
| `hedron` | FastAPI pages/components/actions, CSRF/security profiles, build assets, polling status, CLI/scaffolds, testing helpers, production startup gates |
| `hedron-explorer` | Development mode plus authenticated/authorized secured inspection; never public-by-default; never required at runtime |

### Gate IDs

`CONTRACT-026`, `CORE-026`, `FASTAPI-026`, `EXPLORER-026`, `REVIEW-026`,
`REGRESS-026`, `PKG-026`.

### REVIEW-026 bar

Verified means a redacted report plus disposition ledger are attached, every
critical/high finding is fixed, remaining findings have owners and deadlines,
and the adversarial CI suite for ROADMAP trust boundaries is green. The review
may be performed by an external firm **or** a structured maintainer-led review
independent of the feature authoring pass for this packet, provided the
methodology and findings are recorded honestly. Commercial third-party
re-review remains optional follow-up, not a silent substitute for the attached
packet.

### Upgrade fixtures

See [upgrade-fixtures-026.md](../acceptance/upgrade-fixtures-026.md): goldens
from `v0.25.2` identities, diagnostics, manifests, and HTMX interaction results
under `tests/upgrade/`.

### Non-goals

- Promoting SSE, WebSocket, streaming, or preload from `polling_only`
- Claiming every Beta/experimental core symbol is stable
- Making Explorer an unauthenticated production endpoint
- Scheduling `1.0`, SLA, or certification claims

## Acceptance

- Every 0.26-owned gate row Verified with zero Deferred
- Production-grade label used only for declared Supported inventory
- `python scripts/verify_pkg_26.py` passes without `--allow-planned` at cut
