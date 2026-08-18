# Hedron `v0.50` Explorer architecture acceptance

**Status:** Planned; implementation artifacts are in draft and begin once tracking and ownership
artifacts are accepted.<br>
**Planning baseline:** Published in-tree `v0.49.1`<br>
**Required predecessor/cut baseline:** Verified `v0.49.1`<br>
**Target:** Hedron `v0.50.0`<br>
**Decision/RFC:** D-085 / RFC-0077 (to be hosted in RFC body and phase lock)

Phase 0.50 implements the five enhancement issues for `hedron-explorer` operator tooling:

1. Service boundary extraction and thin transport layer.
2. `ExplorerProvider` v1 protocol for capabilities, limits, and redaction.
3. Bounded search/filter/pagination and resilient rendering for large registries.
4. Headless and browser output parity for diagnostics, exports, and identities.
5. Interaction laboratory + package health slice for safe preview and read-only integrity checks.

## Entry criteria

- RFC-0077 and D-085 are accepted.
- A tracking issue owns every 0.50 gate row before implementation starts.
- Capabilities, upgrades, and deprecation boundaries are captured in the 0.50 inventory.
- Baseline fixture plan from 0.49.1 mount paths and JSON shapes exists.

## Exit gate

- Public mount/API compatibility for 0.49 consumers remains stable.
- Headless outputs and browser diagnostics share identity, severity, and redaction behavior.
- Large-registry fixture budgets are proven with bounded query latency and memory.
- Provider boundary and failure isolation are covered with acceptance tests.
- Deferred scopes remain explicit; no hidden Deferred claims are introduced.
