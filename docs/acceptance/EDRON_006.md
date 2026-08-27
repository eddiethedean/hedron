# Edron 0.6 acceptance

**Status:** Implemented in-tree; release verification complete; publication pending

Phase 0.6 is the reusable composition, typed navigation/layout, reviewed capability promotion,
mixed-surface verification, and package/asset depth slice. Its native lowering and bounded
acceptance evidence are implemented in the Edron 0.6.0 tree; publication remains a separate release
operation.

Public contract outline: [Edron release roadmap](../EDRON_ROADMAP.md).

| Gate | Evidence required | State |
|---|---|---|
| `EDR-06-COMP` | atomic feature-package registration, import isolation, duplicate detection, rollback, and provenance | Verified — `tests/unit/test_phase06_edron.py` |
| `EDR-06-NAV` | typed navigation/layout composition with authorization, accessibility, root-path, HTTP, and no-JavaScript parity | Verified — `tests/unit/test_phase06_edron.py` |
| `EDR-06-PROMO` | reviewed `hedron-*` allowlist, train/version checks, lazy imports, provenance, and native ejection | Verified — `tests/unit/test_phase06_edron.py` |
| `EDR-06-EVID` | bounded Edron/native manifests, fingerprints, conformance checks, redaction, and callback-free diagnostics | Verified — `tests/unit/test_phase06_edron.py` |
| `EDR-06-PKG` | wheel/sdist metadata, documentation, optional dependency, asset collision/deduplication, and upgrade fixtures | Verified — package build and metadata checks |
| `EDR-06-REGRESSION` | complete Edron 0.5 regression plus Phase 0.6 contract, package, and browser suites | Verified — targeted and full regression suites |

Native Hedron remains the authority for route registration, rendering, interaction catalogs,
lifespans, security, package manifests, assets, compatibility, and testing. Edron must not add a
plugin marketplace, arbitrary discovery, a global registry, or a second renderer/router/catalog.
