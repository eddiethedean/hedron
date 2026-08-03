# RFC-0010: Data components

**Status:** Accepted

## Scope

`DataTable` presents tabular data; `DataEditor` adds spreadsheet-like interaction with explicit persistence. Both accept lists of mappings, Hedron models, and optional Pandas, Polars, or PyArrow inputs through a normalization layer.

## DataEditor

The browser grid owns selection, keyboard navigation, copy/paste, virtualization, local undo/redo, and pending edits. Hedron owns schemas, typed change sets, endpoints, validation, authorization, concurrency policy, diagnostics, and transport. The application owns transactions and persistence rules.

Typed changes include updated cells, inserted rows, deleted stable row keys, and optional versions. Manual batch save is the default. Server validation remains authoritative and returns row/column error locations without discarding edits. Stale updates return structured conflicts.

The initial default grid adapter is Tabulator. AG Grid Community and separately licensed backends may be optional adapters. Application code depends on Hedron contracts, not backend-specific options.

## Acceptance criteria

- Read-only and unauthorized fields remain immutable under forged requests.
- Large sources use bounded server-side paging, filters, and sorting.
- Changes support CSRF, authorization, optimistic concurrency, and audit hooks.
- Accessible keyboard editing and CSV download are part of the initial component.
