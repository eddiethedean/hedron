---
status: accepted
---

# Live-transport disposition (0.24)

!!! note "Accepted: `polling_only`"

    Phase **0.24** Accepted disposition **`polling_only`** (Disposition B). Polling is the
    Supported production story. Live SSE / WebSocket / streaming / preload helpers remain
    **experimental** (`hedron.experimental`). Prefer
    [polling](../guides/live-interaction.md) in production.
    Pin the living train: see [What’s ready](../guides/whats-ready.md).

**Owning gates:** `DECIDE-024`, `BROWSER-024`, `PERF-024`, `DOCS-024`, `REGRESS-024`,
`PKG-024`. Decision: **D-053** /
[RFC-0056](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0056-PRODUCTION-QUALITY.md).
Machine twin: [`live-disposition-024.toml`](../acceptance/live-disposition-024.toml).

## XOR contract

| Value | Cut meaning |
|---|---|
| `undecided` | Refine / pre-cut only (`--allow-undecided`) — not used after cut |
| `prove_ops` | Disposition **A** — close browser + load/proxy Deferred ops with evidence (not chosen) |
| `polling_only` | Disposition **B** — **Accepted** — polling is the Supported production story |

Exactly one of `prove_ops` | `polling_only` may be Accepted at cut. Cut chose **`polling_only`**.
Do not half-verify both.

Normative per-gate criteria: [ROADMAP §0.24](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md).

## Prior Deferred IDs in scope

| ID | Historical home | 0.24 handling |
|---|---|---|
| `BROWSER-10-001` | `0.10.x` | **Superseded** under B (`BROWSER-024` waive ledger) |
| `PERF-10-001` | `0.10.x` | **Superseded** under B (`PERF-024` waive ledger) |
| `LIVE-011-BROWSER` | `0.11.x` | **Superseded** under B (`BROWSER-024` waive ledger) |

**Not in scope:** `EXPLORER-10-001` remains Deferred on **`0.10.x`** (Explorer live traces).

## Experimental live surfaces

Because disposition **`polling_only`** was Accepted (not `prove_ops`), these remain
**experimental** (see `hedron.live_claims.EXPERIMENTAL_LIVE_SURFACES`):

```text
SseResponse
sse_response
job_status_sse_response
StreamingComponentResponse
stream_tokens
stream_chunked_list
stream_document
accept_page_session_channel
send_region_update
evaluate_preload_request
apply_preload_headers
```

Import path: `hedron.experimental`. Supported production fallback:
**polling** (`SUPPORTED_PRODUCTION_FALLBACK`).

## Doc honesty

Adopter-facing pages listed in `LIVE_CLAIM_DOC_GLOBS` must not call experimental live
transports unqualified **Supported** while disposition is `polling_only`.
Checker: `python scripts/check_docs_024.py` (train SSOT + live-claim honesty).

## Ledgers and evidence

| Gate | Artifact |
|---|---|
| Browser | [`waive-browser-024.toml`](../acceptance/waive-browser-024.toml) |
| Perf | [`waive-perf-024.toml`](../acceptance/waive-perf-024.toml) |

## Locked gate commands

| Gate | Command |
|---|---|
| `DECIDE-024` | `python scripts/check_live_disposition_024.py` |
| `BROWSER-024` | `python scripts/check_browser_024.py` |
| `PERF-024` | `python scripts/check_perf_024.py` |
| `DOCS-024` | `python scripts/check_docs_024.py` |
| `REGRESS-024` | `bash scripts/ci_checks.sh test --python 3.12` |
| `PKG-024` | `python scripts/verify_pkg_24.py` |

Evidence index: [`release-gate-0.24.toml`](../acceptance/release-gate-0.24.toml).
