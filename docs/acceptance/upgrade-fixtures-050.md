# Phase 0.50 upgrade and rollback fixtures

**Status:** Planned for phase entry planning (0.49.1 baseline)

Required fixture work includes the following five migration paths from `v0.49.1`:

1. Mount-route fixtures for frozen `/hedron-explorer/` prefix and `explorer` setting modes.
2. Provider registry fixture covering at least first-party `data`, `charts`, `maps`, and `extras`
   panels with deterministic fallback behavior.
3. Catalog/manifest/route/service fingerprint fixture set used by diff and headless outputs.
4. Large-app fixture (target: 2,000+ route/component entries) for pagination and resilience.
5. Regression fixture for safe-ops laboratory inputs (exported `AppScenario` and provider failure
   handling).

Baseline JSON shape capture and rollback checks remain read-only to avoid changing public runtime
behavior during phase entry.
