# Security review — phase 0.40 authoring and interoperability (redacted)

**Cut target:** Hedron `v0.40.0` (in-tree cut; tag/PyPI deferred)  
**Owning RFC / decision:** RFC-0060 / D-068  
**Tracking:** #95  
**Baseline:** Published `v0.39.0`

## Scope exercised

- Public author kit + `hedron new element` scaffold (no private registry imports).
- External `PluginContext` element registration (`first_party=False`).
- HDJ element prologue declarations fail closed on unknown keys / missing feature.
- Explorer element inspection and fallback failure simulation.
- `@hedron/elements` modules/types mirror content identity with wheel static assets.
- Experimental React-island reference outside `hedron-elements` (no HTMX region ownership).
- Remediation packet #162/#203/#204/#219/#220/#222.

## Findings

| ID | Severity | Gate | Finding | Disposition |
|---|---|---|---|---|
| REV-040-001 | Low | MIGRATE-040 | Experimental island assets are docs/reference and disposable | Accepted residual — documented removal ledger |
| REV-040-002 | Info | AUTHOR-040 | `hedron-elements` remains Alpha/incubator until 0.42 | Accepted — production-grade inventory |

No unresolved critical or high findings.

## Residual risk

React islands must not be marketed as Supported. Human AT sessions (`SR-021`) remain Planned.
Python consumers remain no-Node; npm mirror is optional modules/types only.
