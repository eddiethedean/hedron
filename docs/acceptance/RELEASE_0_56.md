# Hedron `v0.56` security control plane acceptance

**Status:** Published in-tree as `v0.56.0` (all thirteen gates Verified; tag/PyPI deferred)<br>
**Planning baseline:** Published in-tree `v0.55.0`<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.55.0`<br>
**Target:** Hedron `v0.56.0`<br>
**Decision/RFC:** D-097 / D-098 / [RFC-0083](../rfcs/RFC-0083-SECURITY-CONTROL-PLANE.md)<br>
**Tracking:** [#550](https://github.com/eddiethedean/hedron/issues/550)–[#557](https://github.com/eddiethedean/hedron/issues/557)

Stage 0 freezes the 0.56 gates and shipped 0.55 seams. Stage 1 implements the
control-plane slices, Verifies all thirteen gates, and cuts the in-tree tip to
`v0.56.0`. **Do not tag yet.**

## Exact gate matrix

| Gate | State | Evidence command |
|---|---|---|
| `CONTRACT-056` | Verified | `python scripts/check_contract_056.py` |
| `CONFORM-056` | Verified | `python scripts/check_conform_056.py` |
| `SENS-056` | Verified | `python scripts/check_sens_056.py` |
| `CTX-056` | Verified | `python scripts/check_ctx_056.py` |
| `POSTURE-056` | Verified | `python scripts/check_posture_056.py` |
| `SINK-056` | Verified | `python scripts/check_sink_056.py` |
| `EGRESS-056` | Verified | `python scripts/check_egress_056.py` |
| `INTENT-056` | Verified | `python scripts/check_intent_056.py` |
| `BUDGET-056` | Verified | `python scripts/check_budget_056.py` |
| `ADVERSARY-056` | Verified | `python scripts/check_adversary_056.py` |
| `PERF-056` | Verified | `python scripts/check_perf_056.py` |
| `REGRESS-056` | Verified | `python scripts/check_regress_056.py` |
| `PKG-056` | Verified | `python scripts/check_pkg_056.py` |

## Stage 0 checklist

- [x] D-097 and RFC-0083 own 0.56 security control plane.
- [x] D-098 names actual Published in-tree `v0.55.0` seams.
- [x] Tracking #550–#557 is bound.
- [x] Gate index and acceptance locks are Planned.
- [x] 0.55 gates remain Verified and are not reopened.
- [x] No runtime, package-version, or living-tip change.

## Stage 1 checklist

- [x] Issue workstreams Verified with executable evidence.
- [x] `CONTRACT-056` / `ADVERSARY-056` / `PERF-056` / `REGRESS-056` / `PKG-056` Verified.
- [x] Acceptance locks flipped to Verified.
- [x] Package versions cut to `0.56.0` (in-tree tip; no Git tag yet).

## Cut checklist

- [x] Train packages + workspace bumped to `0.56.0`.
- [x] `docs/release.toml` tip honesty with `registry_status = "deferred"`.
- [x] CI `HEDRON_GATE_VERSION=0.56.0`.
- [x] Docs / SECURITY / STATUS / ROADMAP tip honesty.
- [ ] Git tag `v0.56.0` — **not yet**.
