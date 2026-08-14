# Security review — phase 0.39 rich data and OptimisticMutation (redacted)

**Cut target:** Hedron `v0.39.0`  
**Owning RFC / decision:** RFC-0060 / D-067  
**Tracking:** #94  
**Baseline:** Published `v0.38.0`

## Scope exercised

- DataEditor ABI markup (`data-hedron-abi` / `data-hedron-element`), typed events, SSR fallback retention.
- OptimisticMutation allowlists, deny-by-default risk classes, idempotency keys, conflict rebase (#121).
- Chartlink consumes Published `hedron-chart` events only (`compose_chartlink_039`).
- Worker/object-URL/abort cleanup on DataEditor dispose; workers/WASM absent by default.
- Spreadsheet formula/control/decompression bounds; Three.js path traversal; media Range streaming;
  zip unique member names.

## Findings

| ID | Severity | Gate | Finding | Disposition |
|---|---|---|---|---|
| REV-039-001 | Low | OPTIMISTIC-039 | Pending optimistic state is disposable browser UX; reconnect must refetch | Accepted residual — documented in interaction contracts |
| REV-039-002 | Info | RICH-039 | Map/media/editor/specialty remain Experimental with owned destinations | Accepted — inventory exceptions |

No unresolved critical or high findings.

## Residual risk

Experimental adapters (MapLibre/Folium/PyDeck/AG Grid/CodeEditor) remain opt-in and non-transitive.
Supported path remains server-confirmed authz with bounded DataEditor optimism only.
