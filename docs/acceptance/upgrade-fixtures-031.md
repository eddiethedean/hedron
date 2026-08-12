# Upgrade fixtures plan (0.31 tooling + migrator cut)

**Baseline:** Published **`v0.30.0`**.
**Owning gates:** `REGRESS-031`, `PKG-031`, `MIGRATE-031`, tooling `*-031`
**RFCs:** [RFC-0064](../rfcs/RFC-0064-PRODUCTION-GRADE-TOOLING.md) ·
[RFC-0061](../rfcs/RFC-0061-STREAMLIT-AST-MIGRATOR.md).

## Capture set

### Tooling packages (`0.30` → tooling-grade `0.31`)

1. **Conformance corpus** (`conf_portable_v1.json`) — fixture IDs and
   `CONTRACT_VERSION` / `FIXTURE_VERSION` negotiation remain stable; unknown
   major contract versions refuse with actionable diagnostics.
2. **Sample-kit consumer** (`sample_kit_consumer.json`) — wheel install discovers
   the `hedron.plugins` entry point; disable/uninstall removes Explorer panel and
   diagnostics owner without leaving assets registered.
3. **Sim HTMX subset** (`sim_subset.json`) — declared allowlist bytes match
   `hedron-sim.js`; unsupported verbs/targets fail loudly.
4. **Notebook loopback** (`notebook_loopback.json`) — Supported preview API
   refuses non-loopback bind; localhost start/stop cleanup remains idempotent.

### Streamlit migrator

1. **Sales-dashboard golden** (`migrate_sales_dashboard.json`) — analyze + generate
   from the locked Streamlit fixture; report dispositions cover every `st.*` call;
   generated scaffold runs TestClient smoke without a Streamlit dependency.
2. **No-drop corpus** (`migrate_nodrop.json`) — every Supported mapping-catalog
   symbol receives `translated`, `scaffolded`, `report_only`, or `unsupported`.
3. **Pin continuity** (`migrate_pins.json`) — generated `pyproject.toml` uses the
   living train pin floor from `docs/release.toml`.

## Location

- Plan SSOT: this file
- Fixtures: `tests/fixtures/migrate_streamlit/`, `examples/sample-kit-consumer/`
- Gate drivers: `scripts/check_*_031.py`

## Pass criteria

Silent drift in golden dispositions, inventory keys, or Supported subset docs fails
CI. Intentional breaks require a changelog note and golden update in the same PR.
