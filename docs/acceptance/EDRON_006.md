# Edron 0.6 acceptance

**Status:** Refined implementation candidate; no availability claim

Phase 0.6 is the proposed reusable composition, typed navigation/layout, reviewed capability
promotion, mixed-surface verification, and package/asset depth slice. This packet freezes the
implementation-entry and release-exit evidence; it does not authorize implementation or
publication until the native contracts and supported package matrix are accepted.

Public contract outline: [Edron release roadmap](../EDRON_ROADMAP.md).

| Gate | Evidence required | State |
|---|---|---|
| `EDR-06-COMP` | atomic feature-package registration, import isolation, duplicate detection, rollback, and provenance | Planned |
| `EDR-06-NAV` | typed navigation/layout composition with authorization, accessibility, root-path, HTTP, and no-JavaScript parity | Planned |
| `EDR-06-PROMO` | reviewed `hedron-*` allowlist, train/version checks, lazy imports, provenance, and native ejection | Planned |
| `EDR-06-EVID` | bounded Edron/native manifests, fingerprints, conformance checks, redaction, and callback-free diagnostics | Planned |
| `EDR-06-PKG` | wheel/sdist metadata, documentation, optional dependency, asset collision/deduplication, and upgrade fixtures | Planned |
| `EDR-06-REGRESSION` | complete Edron 0.5 regression plus Phase 0.6 contract, package, and browser suites | Planned |

Native Hedron remains the authority for route registration, rendering, interaction catalogs,
lifespans, security, package manifests, assets, compatibility, and testing. Edron must not add a
plugin marketplace, arbitrary discovery, a global registry, or a second renderer/router/catalog.
