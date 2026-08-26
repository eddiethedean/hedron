# Edron 0.2 implementation

**Status:** Implemented and verified in-tree

Phase 0.2 is implemented as a thin authoring/tooling layer over the Edron 0.1 runtime and native
Hedron app. `edron.diagnostics` owns only Edron-facing structured records; HTTP, HTMX, routing,
security, rendering, assets, and state remain native Hedron authorities.

Implemented slices:

- source locations attached to descriptors and application explanations;
- bounded Edron diagnostic/report projections with redaction and SARIF output;
- AST-only static checking and explicit trusted registration;
- package capability doctor with no installation side effects;
- minimal, dashboard, and form teaching scaffolds;
- explicit function pages with fresh request ownership; and
- explicit, descriptor-level inheritance via `inherit`/`expose`.

The focused acceptance command is:

```text
.venv/bin/python -m pytest -q tests/unit/test_edron_phase02.py tests/unit/test_edron_runtime.py tests/unit/test_edron_docs_checker.py
.venv/bin/ruff check packages/edron/src/edron tests/unit/test_edron_phase02.py
```

No phase 0.3 data editing API, global session dictionary, whole-script rerun, implicit mutation
button, or runtime package installation is introduced.
