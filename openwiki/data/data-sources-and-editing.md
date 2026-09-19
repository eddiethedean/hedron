---
type: reference
title: Data Sources and Editing
description: Bounded tabular data, editable grids, transform plans, and optimistic mutation contracts.
tags:
  - data
  - editing
  - contracts
verified:
  - by: openwiki/0.5.2
    at: 2026-09-19T17:40:19.225Z
sources:
  - id: openwiki-source-d1732c0960a3179e34a09e02
    resource: repo://packages/hedron-data/src/hedron_data/editor.py
  - id: openwiki-source-bdfefb142593afda12d7665c
    resource: repo://packages/hedron-data/src/hedron_data/normalize.py
  - id: openwiki-source-054920506656462289f8087f
    resource: repo://packages/hedron-data/src/hedron_data/optimistic.py
  - id: openwiki-source-e22e766e7afdc04cf910b0ae
    resource: repo://packages/hedron-data/src/hedron_data/plans.py
  - id: openwiki-source-5da6490dd627391ec23266d1
    resource: repo://packages/hedron-data/src/hedron_data/sources.py
  - id: openwiki-source-5924e8a68cf24136e5f29de5
    resource: repo://packages/hedron-data/src/hedron_data/table.py
  - id: openwiki-source-de0efe51a033b39eacdf118d
    resource: repo://tests/conformance/test_data_chart_contracts.py
  - id: openwiki-source-5736261fc22d9a4ead25c79d
    resource: repo://tests/integration/test_data_editor_csrf_save.py
generated: { by: "codex", at: "2026-09-19T16:47:17.741Z" }
---

# Data Sources and Editing

The `hedron-data` package separates tabular data contracts from the host
framework that serves them. A component can receive an in-memory collection,
an already fetched `DataPage`, or a source object that owns fetching and
applying changes. That separation keeps paging, validation, authorization, and
serialization decisions on the server side while the browser receives a
bounded representation.

## Queries, pages, and normalization

`DataQuery` is the common request shape for tabular and visualization sources.
It carries offset or cursor pagination, sort directions, filters, projections,
search, and locale. `validated()` rejects malformed values, enforces optional
allowlists for sort/filter/projection fields, caps a requested page to the
configured maximum, and never permits a page larger than the hard limit of 500
rows. `DataPage` returns rows with optional column schema, total, continuation
information, and a version token.

`normalize_rows()` is the boundary for inline data. It handles mappings,
sequences of mappings or Hedron models, and optional Pandas/Polars/PyArrow
objects through Narwhals. It refuses implicit collection of lazy sources and
rejects inline inputs above its 10,000-row budget; callers with larger or
remote data should use a paged source instead. Cells pass through the shared
redaction helper before they become JSON-shaped rows.

## Tables and editors

`DataTable` is a server-rendered accessible table. It resolves columns from a
row model, explicit columns, or the rows, preserves page totals and versions in
HTML data attributes, and offers CSV export. Hidden and secret columns are not
included in CSV, while secret values are masked in the rendered table.

`DataEditor` is an editable grid host. Its source contract is `fetch(query)`
plus `apply(changes)`, with synchronous and asynchronous protocols; async
sources must be fetched explicitly before synchronous component construction.
The server remains authoritative: `filter_writable_changes()` rejects forged
writes to read-only, hidden, or non-writable fields, filters insert fields to
the allowlist, and applies the configured delete policy. Save results carry
accepted changes, normalized rows, field errors, conflicts, and a new version.

## Explicit transforms and optimistic edits

`TransformPlan` makes in-memory execution inspectable. Its steps are limited to
the package's allowlisted filter, sort, project, aggregate, sample, search, and
offset operations. Each plan enforces row and serialized-byte budgets and can
carry tenant, cancellation, and authorization context. `plan_from_query()`
translates a validated `DataQuery` into this bounded execution form.

`OptimisticMutation` is deliberately narrower than a general mutation API. It
requires typed patches, an idempotency key, and (for the phase-0.62 contract) a
base revision. Its state machine distinguishes proposed, submitted, confirmed,
rejected, conflicted, rolled-back, and refetched states. Collection edits,
reversible toggles, and scalar edits are the approved phase inventory; identity,
authorization, payment, secret, publication, destruction, and cross-tenant
risks remain deny-by-default.

The contract fixtures cover query/change shapes, transform budgets, chart/grid
events, and adversarial values. Integration coverage also exercises a
`DataEditor` JSON save with the CSRF cookie/header path, ensuring a forged or
missing token is rejected before an authorized update reaches the source.

See [Requests and Interactions](../architecture/requests-and-interactions.md)
for the request lifecycle and [Security and Request Boundaries](../security/request-boundaries.md)
for the cross-cutting protections around these contracts.
