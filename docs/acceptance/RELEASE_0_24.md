# Hedron `v0.24` live-transport production disposition acceptance

Phase 0.24 ends the permanent experimental-live fog: either prove multi-engine browser
and load/proxy backpressure evidence so SSE/WebSocket can graduate under documented ops
constraints, **or** formally document polling-only as the Supported production story.
Evidence is indexed by [`release-gate-0.24.toml`](release-gate-0.24.toml).
**Zero Deferred:** every 0.24-owned gate row must be Verified at cut.
Exactly one disposition may be Accepted — do not half-verify both.

Owning decision: [D-053](../DECISIONS.md). RFC:
[RFC-0056](../rfcs/RFC-0056-PRODUCTION-QUALITY.md).
Prior Deferred IDs in scope: `BROWSER-10-001`, `PERF-10-001`, `LIVE-011-BROWSER`.
Disposition SSOT: [LIVE_DISPOSITION.md](../api/LIVE_DISPOSITION.md) ·
[live-disposition-024.toml](live-disposition-024.toml).

## Spec packet

- [x] ROADMAP §0.24 scope accepted; D-053 / RFC-0056 recorded.
- [x] Packet refine: locked dual-path Verified criteria; XOR disposition contract;
  distinct gate commands.
- [x] Gate checker recognizes `0.24` evidence manifest against the living train:
  `python scripts/check_release_gate.py 0.23.0 --evidence-manifest docs/acceptance/release-gate-0.24.toml --allow-planned`
  (or `python scripts/verify_pkg_24.py --allow-planned`).
- [x] Disposition + waive ledger templates + checkers:
  `python scripts/check_live_disposition_024.py --allow-undecided`,
  `python scripts/check_browser_024.py --allow-undecided`,
  `python scripts/check_perf_024.py --allow-undecided`,
  `python scripts/check_docs_024.py`,
  `python scripts/verify_pkg_24.py --allow-planned`.
- [x] `DECIDE-024` disposition written (`polling_only`) and mirrored in
  What’s ready / STABILITY / LIVE_DISPOSITION.
- [x] `BROWSER-024` / `PERF-024` / `DOCS-024` Verified for `polling_only`
  (waive ledgers + claim honesty).
- [x] `REGRESS-024` / `PKG-024` at cut
  (`bash scripts/ci_checks.sh test --python 3.12`,
  `python scripts/verify_pkg_24.py`).

## Out of 0.24

- Production archetype / load budgets / extras quarantine / charts path → **0.25**
- Alpha charts / notebook / MCP / Gradio / `hedron-native`
- Human AT sessions (`SR-021` / …) remain Planned
- `EXPLORER-10-001` stays Deferred on `0.10.x`

## Exit

- [x] Every 0.24-owned row `Verified` in `release-gate-0.24.toml`
- [x] Prior Deferred live-ops IDs have terminal owner notes
  (`superseded` via waive ledgers under `polling_only`)
