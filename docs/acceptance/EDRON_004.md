# Edron 0.4 acceptance

**Status:** Implemented and verified in-tree; publication pending

Phase 0.4 adds visualization and media composition without creating a second renderer, browser
runtime, or state authority. The focused commands in this packet must pass before a future
`edron-v0.4.0` release gate is opened.

| Gate | Evidence | State |
|---|---|---|
| `EDR-04-VIS` | native chart specification and map composition with accessible fallbacks | Verified |
| `EDR-04-LINK` | typed chart/map interactions lower to registered native action handles | Verified |
| `EDR-04-ALT` | text/static alternatives, required image alt text, and validated media tracks | Verified |
| `EDR-04-MEDIA` | safe native image/audio/video composition and existing download authority | Verified |
| `EDR-04-EXPLAIN` | bounded visualization interaction projections in `App.explain()` | Verified |
| `EDR-04-REGRESSION` | Edron 0.2/0.3/runtime suites remain green | Verified |

The phase keeps chart/map selections typed and bounded by the owning native interaction contracts.
Applications continue to own data selection, authorization, persistence, transactions, and media
storage; optional adapters remain lazy and directly installed.
