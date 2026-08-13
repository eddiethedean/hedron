# Phase 0.34 implementation plan: production-grade `hedron-gradio`

This plan turns [RFC-0067](../rfcs/RFC-0067-PRODUCTION-GRADE-GRADIO.md) into reviewable work. It is not
authorization to cut until RFC-0067 is Accepted and every gate row is Verified.

## Outcome

Ship `hedron-gradio` `0.2.0` Beta as production-grade for explicitly declared remote Gradio
endpoints and bounded Hugging Face Space client paths. The package leaves Experimental Alpha;
absence of the package adds no core cost.

The phase is complete only when every row in
[`release-gate-0.34.toml`](../acceptance/release-gate-0.34.toml) is Verified.

## Decisions already locked

| Topic | Decision |
|---|---|
| Primary scope | Allowlisted remote predict/stream/file transport; no UI runtime |
| Alpha contract | [RFC-0049](../rfcs/RFC-0049-GRADIO-ADAPTER.md) remains historical product contract |
| Version policy | `0.2.0` Beta at cut; Alpha `0.1.x` upgrade source |
| Presentation cross-cutting | [DEFAULT_PRESENTATION_033_PLUS.md](DEFAULT_PRESENTATION_033_PLUS.md) `PRESENT-034` is **non-blocking** for Gradio cut |
| MCP crossover | `gradio_auto_composition` stays **Excluded** per MCP inventory |

## Stage 0 — contract refine (no behavior change)

**Goal:** locked cut matrix, inventory, RFC draft, gate manifest (Planned).

Deliverables:

- Draft RFC-0067, D-062, this plan, `production-grade-inventory-034.toml`
- `release-gate-0.34.toml` with Planned rows
- `RELEASE_0_34.md` acceptance skeleton
- Tracking [#90](https://github.com/eddiethedean/hedron/issues/90) synced to 0.34 gates

**Exit:** `python scripts/verify_pkg_34.py --allow-planned` green.

## Stage 1 — gate plumbing

Checker scripts under `scripts/check_*_034.py`, `_gate_034.py`, `verify_pkg_34.py`,
`check_release_gate.py` `0.34` mapping.

## Stage 2 — egress and files (`EGRESS-034`, `FILES-034`)

Repository changes:

```text
packages/hedron-gradio/src/hedron_gradio/
  policy.py      # GradioRemoteConfig, URL allowlist, SSRF helpers
  artifacts.py   # bounded file store with TTL cleanup
  client.py      # integrate policy + artifacts
```

Work items:

- `GradioRemoteConfig`: declared `base_url`, allowed hosts/schemes, redirect hop limit, TLS verify, deadlines
- Fail closed when `enabled=True` and destination not allowlisted
- Adversarial corpora under `tests/fixtures/gradio/` and `tests/security/test_gradio_034.py`

## Stage 3 — jobs and compatibility (`JOBS-034`, `COMPAT-034`)

- Real queue/stream semantics via transport injection and optional `gradio_client`
- `GradioJobHandle` with timeout, cancel, disconnect cleanup
- `GradioPollingJobBackend` bridge for Hedron job status polling
- Pinned matrix fixtures; `tests/upgrade/test_0_33_to_0_34_gradio.py`

## Stage 4 — vendor and cut (`VENDOR-034`, `PKG-034`, `REVIEW-034`)

- HF Space token scope helpers in `hf.py`
- `docs/acceptance/security-review-034/BRIEF.md`
- Optional `scripts/realgradio_034_probe.sh` (recorded fixtures first)
- Package bump to `0.2.0` Beta; docs and inventory alignment

## Supported topology matrix

| Topology | Supported at cut? | Evidence |
|---|---|---|
| Declared self-hosted Gradio HTTPS | Yes (primary) | Recorded fixtures + unit/adversarial suites |
| Public Hugging Face Space | Yes (bounded) | `VENDOR-034` auth/cold-start/quota fixtures |
| Private HF with token | Yes | Credential scope + redaction tests |
| Arbitrary caller URL | No | Fail closed (`EGRESS-034`) |
| Gradio share tunnels / UI runtime embed | Excluded | RFC-0049 non-parity |

## Test locations

- `tests/unit/test_phase18_gradio.py` (baseline)
- `tests/unit/test_gradio_034.py`
- `tests/security/test_gradio_034.py`
- `tests/upgrade/test_0_33_to_0_34_gradio.py`

## Cut verification

At `v0.34.0` cut:

```bash
python scripts/verify_pkg_34.py
python scripts/check_release_gate.py 0.34.0 --execute-verified
```

During packet refine:

```bash
python scripts/verify_pkg_34.py --allow-planned
python scripts/check_release_gate.py 0.34.0 \
  --evidence-manifest docs/acceptance/release-gate-0.34.toml \
  --allow-planned
```
