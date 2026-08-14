# Rich-surface catalog — phase 0.39

Normative inventory for D-067 / `RICH-039` / `DATA-039` / `CHARTLINK-039`. Optimistic mutation
semantics remain authoritative in
[WEB_COMPONENT_INTERACTION_CONTRACTS.md](WEB_COMPONENT_INTERACTION_CONTRACTS.md) §3.

## First-party surfaces (intended Supported at cut when ABI gates pass)

| Surface | Package | Notes |
|---|---|---|
| `DataTable` | `hedron-data` | Read/paging/selection; SSR table fallback |
| `DataEditor` | `hedron-data` | Bounded cell/row edits; first `OptimisticMutation` proof inventory |
| Chart composition | `hedron-charts` | Consumes Published `hedron-chart` only (`CHARTLINK-039`) |

## Eligible rich adapters (ABI or owned Experimental)

| Surface | Default disposition | Notes |
|---|---|---|
| Map hosts (MapLibre/Folium/PyDeck) | Experimental unless ABI + cleanup proven | Origin/asset bounds under `WORKER-039` |
| Media / capture | Experimental | Stream/object-URL cleanup required |
| Code / text editors | Experimental (`CodeEditor`) | Owned destination until graduated |
| Specialty 3D / GraphViz / Great Tables hosts | Experimental | Payload bounds; #73/#84/#194 owned by REGRESS-039 |

## Experimental exception policy

Every first-party rich surface either:

1. Shares the public element ABI (registry metadata, lifecycle, typed events, SSR fallback,
   disposal), **or**
2. Publishes a machine-visible Experimental exception with **owner** and **destination phase**.

No surface may keep an unowned lifecycle, event, or fallback protocol after `RICH-039` Verified.

## OptimisticMutation first inventory

- **In:** bounded DataEditor / collection cell edits with explicit base revision, idempotency key,
  typed forward patch or canonical refetch, proposed/submitted/confirmed states, rollback, conflict,
  and reconnect.
- **Deny-by-default:** authentication changes, irreversible destruction, payments, secrets, file
  publication, cross-tenant moves, and any mutation lacking idempotency or a recoverable
  inverse/refetch path.

## Chart link

Cross-filtering and rich-surface composition must use the Published 0.38 `ChartSpec` /
`ChartPlan` / `hedron-chart` contract. Creating a second interactive chart renderer is a
non-goal of 0.39.

## Worker / remote bounds (WORKER-039)

Inventory and bound: dedicated workers, WASM modules, object URLs, media streams, observers,
third-party runtimes, remote origins, payload sizes, cancellation, and disconnect cleanup.
Absence remains the default for Supported surfaces.
