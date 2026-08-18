# Explorer architecture and operator-grade development tooling (`v0.50`)

## Purpose

Phase 0.50 focuses on the remaining `hedron-explorer` upgrades and turns the existing
single-module implementation into an operator-grade subsystem with clear service boundaries,
shared query models, and headless/CLI parity.

## Five enhancement issues

1. **Service boundary extraction** — split `router.py` into versioned `services/*` and thin
   transport entrypoints.
2. **Provider protocol v1** — define a versioned provider interface for panel capabilities,
   timeout, ordering, redaction profile, and payload ceilings.
3. **Explorer query resilience** — add bounded search/filter/pagination behavior for large
   apps and deterministic truncation diagnostics.
4. **Headless diagnostics** — align CLI/JSON outputs with browser workflows using shared
   trace/catalog/diff services.
5. **Interaction laboratory + package health slice** — support bounded safe preview operations
   and read-only health diagnostics without elevating authority.

## Stage 0 scope lock

- Existing 0.49 mount paths and compatibility contracts are preserved.
- No change to production opt-out posture (`explorer="off"|"development"|"secured"` semantics).
- Progressive enhancement remains server-authoritative and no-JS fallbacks are maintained.

## Evidence anchors

- API contract: `docs/implementation/WEB_COMPONENT_INTERACTION_CONTRACTS.md`
- Phase plan and milestones are mirrored in `docs/ROADMAP.md`.
- Capability and acceptance tracking are in `docs/acceptance/explorer-capability-inventory-050.toml`
  and `docs/acceptance/RELEASE_0_50.md`.
