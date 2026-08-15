# Hedron `v0.41` browser composition, state, and navigation acceptance

**Status:** Release candidate implemented and Verified in-tree; intentionally untagged/unpublished.

Phase 0.41 adds allowlisted typed composition, subject-bound bounded draft transfer, progressive
navigation/restoration, content-free traces, and element/region failure isolation while the server
and ordinary links/forms remain authoritative. Owning decision: [D-069](../DECISIONS.md). Design:
[RFC-0060](../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md). Plan:
[HEDRON_COMPOSITION_041](../implementation/HEDRON_COMPOSITION_041.md). Evidence index:
[`release-gate-0.41.toml`](release-gate-0.41.toml). Tracking:
[#96](https://github.com/eddiethedean/hedron/issues/96).

## Release contract

- Baseline Published `v0.40.0`; target coordinated `v0.41.0`.
- Same-origin, allowlisted composition with explicit schema/authz/bounds/fallback.
- Draft-only `sessionStorage` transfer with app/route/contract/schema/subject namespace,
  single-consume, ceilings, expiry, and mandatory clearing.
- Native/HTMX navigation ownership retained; deterministic title/focus/scroll/popstate behavior.
- Optional preload/View Transitions never affect correctness and honor reduced motion.
- Content-free traces and per-element/region failure containment.
- Exact regression packet #70/#74/#85/#98/#103/#106/#135/#149/#150/#185/#186/#200/#202/#207.

## Exact cut matrix

| Lane | Required proof | Planned command |
|---|---|---|
| Composition | Schemas, graph bounds/authz/cancel/fallback | `check_compose_041.py` |
| State | Transfer eligibility, namespace, clearing, rejection, no-storage | `check_state_041.py` |
| Navigation | boost/history/fragment/focus/title/scroll/optional motion | `check_nav_041.py` |
| Trace | content-free schema and privacy-negative corpus | `check_trace_041.py` |
| Fallback | failure/version/storage/timeout isolation | `check_fallback_041.py` |
| Browser | engines/hosts/a11y/perf/privacy/memory | `check_browser_041.py` |
| Regression | exact 14 issues and prior-platform gates | `check_regress_041.py` |
| Packaging | inventory/docs/upgrade/rollback/rehearsal | `verify_pkg_41.py` |

Commands are names reserved by this plan, not implementations.

## Stage 0 entry/exit

- [x] D-069 Accepted and RFC-0060 D-069 answers present
- [x] Release packet, planned gate manifest, implementation plan, upgrade fixture, and review brief
- [x] #96 plus the exact 14-issue regression packet bound to gates
- [x] Published `v0.40.0` remains the living baseline
- [x] Stage 0 itself made no runtime/version/package/generated-asset or issue mutation

## Cut rule

Every 0.41 row is Verified with zero Deferred. The workspace is the untagged `v0.41.0` release
candidate; tagging and publication remain separate explicit actions.
