# Hedron `v0.34` production-grade Gradio acceptance

**Status:** **Published** as `v0.34.0` (2026-08-13).

Phase 0.34 graduates **`hedron-gradio` `0.2.0` Beta** for explicitly declared remote Gradio
endpoints and bounded Hugging Face Space client paths. Baseline: Published `v0.33.0`. Evidence is
indexed by [`release-gate-0.34.toml`](release-gate-0.34.toml). **Zero Deferred:** every 0.34-owned
Gradio gate must be Verified at cut.

Owning decision: [D-062](../DECISIONS.md). Design:
[RFC-0067](../rfcs/RFC-0067-PRODUCTION-GRADE-GRADIO.md) (**Accepted** 2026-08-13). Implementation:
[HEDRON_GRADIO_034](../implementation/HEDRON_GRADIO_034.md). Tracking:
[#90](https://github.com/eddiethedean/hedron/issues/90).

## Release contract

- `hedron-gradio==0.2.*` depends on `hedron-core>=0.34,<0.35`; Alpha `0.1.x` remains the
  upgrade source.
- `hedron[gradio]` extra installs the satellite; absence adds no core dependency or startup cost.
- Supported remote calls require explicit destination allowlist and endpoint declarations.
- Gradio UI runtime embed, share tunnels, and arbitrary caller URLs remain **Excluded**.
- Python 3.11–3.14 remain the supported interpreter matrix.
- Default presentation refresh (`PRESENT-034`) is **optional** and non-blocking for Gradio cut
  (Deferred to 0.35).

## Entry criteria

- [x] `v0.33.0` published; D-061 Accepted; #167 closed
- [x] Gradio Alpha baseline from 0.18 (`GRADIO-018`)
- [x] RFC-0067 Accepted and implementation plan present
- [x] Tracking issue #90 bound to phase 0.34 gate IDs
- [x] Planned release-gate rows and checker ownership reviewed

## Exact cut matrix

Recorded fixtures: [`tests/fixtures/gradio/`](../../tests/fixtures/gradio/).

| Lane | Topology | Required evidence |
|---|---|---|
| Self-hosted HTTPS | Declared allowlisted Gradio server | `EGRESS-034`, `COMPAT-034`, `FILES-034`, `JOBS-034` adversarial + unit suites |
| Public HF Space | Bounded public Space predict path | `VENDOR-034` auth/cold-start/quota fixtures |
| Private HF token | Scoped HF token without log leakage | `VENDOR-034` redaction tests |
| Arbitrary URL | Caller-supplied undeclared host | Fail closed — not Supported |
| Share tunnel / UI runtime | Gradio share links or embedded UI | Excluded — RFC-0049 non-parity |

## Locked evidence gates

| Gate | Owner | Verified means |
|---|---|---|
| `CONTRACT-034` | `hedron-gradio` | Accepted RFC, cut matrix, inventory, implementation plan, and exclusions agree |
| `COMPAT-034` | `hedron-gradio` | Pinned client/server matrix, discovery/schema drift, recorded fixtures, upgrade behavior |
| `EGRESS-034` | `hedron-gradio` | Destination allowlists, redirect/DNS/TLS/SSRF controls, credential scope, redaction |
| `FILES-034` | `hedron-gradio` | File type/size/retention/path and artifact cleanup under malicious/interrupted transfers |
| `JOBS-034` | `hedron-gradio` | Queue/predict/stream timeout, cancel, retry, disconnect, multi-worker polling, outages |
| `VENDOR-034` | `hedron-gradio` | Supported HF paths with auth, cold-start, quota, failure, compatibility evidence |
| `REVIEW-034` | `hedron-gradio` | Independent review with no unresolved critical/high finding at cut |
| `DOCS-034` | `hedron-gradio` | Operator guide, migration, inventory, and Supported/Experimental boundaries |
| `REGRESS-034` | `hedron` | Gradio corpora, upgrade tests, docs strict build |
| `PKG-034` | `hedron` | Clean installs, SBOM/provenance, all gate commands pass with zero Deferred |
| `PRESENT-034` | `hedron-core` | Optional — refreshed default gallery; defer to 0.35 if not green |

## Required adversarial cases

- Undeclared host, private IP, metadata endpoint, redirect chain, DNS rebinding
- Oversized upload/download, path traversal artifact ids, interrupted transfer cleanup
- Job timeout, cancel mid-stream, disconnect without leak, cross-scope job id reuse
- Token/credential substrings in logs and raised errors
- Schema drift vs pinned `gradio_client` matrix

No evidence artifact may contain real HF tokens, raw credentials, or live Space secrets.

## Cut verification

At `v0.34.0` cut (every Gradio row Verified):

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

## Exit

- [x] Exact cut matrix has no `TBD` on Supported lanes
- [x] RFC-0067 Accepted and implementation matches it
- [x] Every 0.34-owned Gradio release-gate row Verified with zero Deferred
- [x] `hedron-gradio` maturity claim matches the inventory
- [ ] Close #90 after release assets are published on GitHub/PyPI
