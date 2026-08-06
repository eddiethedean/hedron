# RFC-0041: PropertyPatch, CollectionPatch, and structured collections

**Status:** Accepted
**Phase:** 0.17 (`v0.17.0`)
**Stability:** `beta`
**Evidence:** `PATCH-017` (also consumed by `XFILTER-017` / `GRAPH-017`)
**Related:** RFC-0008, RFC-0010, RFC-0011, RFC-0026, RFC-0040; Dash `Patch` / pattern-matching IDs

## Summary

Define versioned, bounded `PropertyPatch` and `CollectionPatch` operations for declared chart,
table, store, and component state, plus stable structured collection identities and typed
selectors (map, gather, broadcast, exact-member, ordered-range). Arbitrary browser-object or DOM
mutation is prohibited; full-fragment fallback is mandatory when patches cannot apply safely.

## Motivation and background

Dash `Patch` / `set_props` and pattern-matching IDs (`ALL`, `MATCH`, `ALLSMALLER`) deliver useful
incremental-update and dynamic-component outcomes. Hedron must adopt those outcomes with schema,
version/precondition, authorization, operation/payload caps, conflict/rollback behavior, and
inspectable selector resolution — without making undeclared mutation or DOM selectors into
authorization boundaries.

## Proposed design

### PropertyPatch / CollectionPatch

Supported operation families (explicitly typed):

- assign / merge
- append / prepend / extend / insert
- remove / delete / clear
- reorder / reverse
- explicitly typed numeric ops (increment/decrement/clamp) where declared

Mandatory controls: schema validation, operation count caps, payload size caps, version or
precondition checks, target authorization, conflict detection, rollback or fail-closed rejection,
and full-fragment fallback. Intermediate updates are allowed only for registered, inspectable
targets (no Dash-style undeclared `set_props`).

### Collection identities and selectors

- Stable structured identities for repeated/dynamic components.
- Selectors: map, gather, broadcast, exact-member, ordered-range.
- Fragment insertion/removal updates the registry safely; teardown cleans event membership.
- Selector resolution is inspectable in Explorer/diagnostics and never substitutes for tenant or
  object authorization.

### Integration

Patches may be returned from dashboard actions (RFC-0040) or ordinary handlers. Invalid, stale,
unauthorized, or oversized patches fail closed and may trigger a declared full-region refresh.

## Alternatives considered

1. **Full-fragment only forever.** Rejected — cross-filter dashboards need bounded incremental
   updates with evidence.
2. **Arbitrary JSON Merge Patch on any component prop.** Rejected — too broad; no schema/authz.
3. **DOM CSS-selector targeting.** Rejected — not an authorization boundary.

## Security implications

Every patch rechecks target authorization and tenant scope. Version/precondition mismatches must
not leak existence of unauthorized objects. Caps prevent DoS via operation floods.

## Accessibility implications

Partial updates must preserve focus and announce meaningful changes; when falling back to full
fragments, reuse existing HTMX/region a11y contracts.

## Performance implications

Operation and payload budgets; coalesce with TriggerContext debounce; measure patch vs full-fragment
paths in Explorer timing overlays.

## Testing strategy

Schema/precondition/conflict unit tests; adversarial oversized and unauthorized patches; dynamic
collection insert/remove; browser suites for patch conflict and fallback. Gate: `PATCH-017`.

## Compatibility and migration

Additive. Existing `InteractionResult` region updates remain valid. Dash migration maps `Patch` →
this contract (`MIGRATE-017`).

## Open questions

None blocking Acceptance.

## Acceptance criteria

- Invalid patches fail closed with diagnostics; successful patches never mutate undeclared targets.
- Dynamic collections update registry membership without leaking stale event handlers.
- Full-fragment fallback remains functional for no-JavaScript and conflict paths.
