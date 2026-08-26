# Edron 0.3 implementation

**Status:** Implemented and verified in-tree

Phase 0.3 is a thin orchestration layer over the Published native `hedron-data` contracts. The
implementation is in `packages/edron/src/edron/data.py`; `Page.data_workspace` and
`Page.data_editor` only fetch one bounded page and append the native table/editor component.

Implemented slices:

- explicit `DataSource` adapters for custom/native, bounded in-memory/dataframe, and SQLAlchemy
  sources;
- allowlisted `DataWorkspace` paging, filtering, sorting, searching, and projection;
- bounded `DataSelection` and current-page CSV export with secret omission/formula hardening;
- typed `CellEdit`/`EditIntent`, deny-by-default `EditPolicy`, native `DataSaveResult` conflicts,
  validation hooks, and value-free `AuditEvent` records;
- explicit `App.data_workspace()` JSON mutation registration through Hedron action/CSRF policy;
- progressive native table/editor rendering and native ordinary-form workspace composition; and
- redacted, non-fetching workspace diagnostics.

Focused verification:

```text
PYTHONPATH=packages/edron/src .venv/bin/python -m pytest -q -n 0 \
  tests/unit/test_edron_phase03.py tests/unit/test_edron_phase02.py \
  tests/unit/test_edron_runtime.py tests/unit/test_edron_docs_checker.py
.venv/bin/ruff check packages/edron/src/edron tests/unit/test_edron_phase03.py
```

Edron remains a separately versioned Beta facade. Persistence, tenant scope, authorization,
transactional audit, and conflict-resolution policy remain application-owned.
