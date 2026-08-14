# Human AT protocol — phase 0.39 (scoped)

Representative keyboard and screen-reader sessions for DataTable/DataEditor upgraded state and
JS-off table/summary fallbacks, plus chart-link composition that consumes Published `hedron-chart`.

This packet is **scoped AT evidence** for `A11Y-039` only. It does not claim Supported human AT
(see [#86](https://github.com/eddiethedean/hedron/issues/86) / D-052). Do not block 0.39 on
`SR-021`. Three-engine automated a11y remains required.

## Sessions (planned)

1. Navigate a DataTable with keyboard-only focus after upgrade; confirm row/cell selection is
   announced without hover-only paths.
2. Complete a bounded DataEditor cell edit through proposed → submitted → confirmed; confirm
   conflict and rollback announcements stay bounded.
3. Complete the same inspect path on the JS-off semantic table / summary fallback.

Record outcomes in `ledger/` using the redacted schema from `../ledger.schema.json`.
No sessions are recorded in this Stage 0 refine.
