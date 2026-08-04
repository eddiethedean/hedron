# RFC-0032: Live transport, focused streaming, and navigation preload

**Status:** Accepted
**Phase:** 0.10 (`v0.10.0`)
**Decisions:** D-037 (revised), D-044, D-045

## Summary

Phase 0.10 adds evidence-backed live observation (official HTMX SSE), focused streaming
primitives, page/session WebSocket channels for accepted bidirectional cases, Chat/Dialog
interaction components, timed media chunk transport contracts, and opt-in navigation preload.
Polling and ordinary HTTP/HTML navigation remain Supported fallbacks and never become hidden
correctness dependencies.

HDJ composes with these transports without new template syntax (RFC-0031 / D-041).

## Model

| Layer | Ownership |
|---|---|
| Portable framing, budgets, observation contracts | `hedron-core` (no FastAPI/ASGI imports) |
| FastAPI SSE/WS/stream routes and response helpers | `hedron` |
| Official HTMX extension assets | Pinned local files under `/hedron-static/ext/` |
| Flask/Django live hosts | Capability labels only in 0.10; native depth remains 0.11 |

## SSE

- Official `htmx-ext-sse` is pinned with digest, CSP, and load order.
- Job status and generic region updates may use `text/event-stream` with auth,
  `Last-Event-ID` resume, bounded retry, cancellation, and terminal-state stop.
- `JobBackend` state machine is unchanged; SSE is a replaceable observation transport.
- Bounded polling (`Retry-After` + `Poll`/`Status`) remains Supported (JOB-004).

## Focused streaming

- Explicit APIs only: `ChunkedList`, `StreamedDocument`, `TokenStream`, and
  `StreamingComponentResponse`.
- Ordinary `Component.render()` stays non-streaming (D-019).
- Streams preserve addressable region IDs, deadlines, disconnect cancellation, and a
  non-streaming fallback page/fragment.

## WebSocket channels

Accepted use cases only:

1. Stream intermediate updates to **declared** fragment regions.
2. Read current values only from **declared** client components.
3. Run bounded persistent producers with authenticated reconnect, batching/debounce,
   disconnect cancellation, resource budgets, and accessible HTTP/SSE/polling fallback.

No general pub/sub bus. FastAPI is the Supported host in 0.10.

## Navigation preload

- Opt-in safe GET only.
- Cache correctness and private authenticated cache rules from the 0.8 matrix apply.
- Speculative traffic is bounded; cancellation is required; `HX-Preloaded` is observable.
- Disabled by default until performance evidence justifies enabling a policy.

## HDJ (closes HDJ-DEF-010)

- Registered fragment head management via pinned `htmx-ext-head-support`.
- Explicit two-phase template streaming that finalizes atomic `RenderResult` metadata before
  or as a documented preamble to body chunks.
- Version-aware HTMX attribute/selector reporting against the installed HTMX pin.
- Browser modules initialize idempotently on HTMX load/swap and clean up before swap-out.

## UI primitives

- `Dialog`: native `<dialog>`, focus trap/restore, Escape/close, background inertness,
  fragment-addressable content; no application-wide rerun scope.
- `ChatMessage` / `ChatInput`: typed transcript items, explicit submit, optional attachments,
  accessible status, bounded token streams over Poll/SSE/stream; history is application-owned.

## Media chunk transport

- Timed camera/microphone image/audio **session contracts** and chunked A/V generator output
  with permission, duration/cadence, codec/bandwidth budgets, backpressure, origin, reconnect,
  cancel, teardown, and non-streaming fallback.
- First-party capture UI components remain phase 0.15.

## Security

CSRF, auth, CSP, safe URLs, private cache, and origin checks apply to live paths (D-013).
SSE subscribe uses cookie auth with same-origin defaults; unsafe mutations remain non-GET.

## Accessibility

Live regions announce status updates politely. Dialog restores focus. Chat streams expose
status without trapping keyboard users. Reduced-motion preferences are respected for
non-essential motion.

## Performance

Each enabled transport or preload policy requires load/backpressure evidence and bounded
resource budgets (`PERF-10-001`).

## Acceptance

Indexed by [`release-gate-0.10.toml`](../acceptance/release-gate-0.10.toml) and
[`RELEASE_0_10.md`](../acceptance/RELEASE_0_10.md). Exit requires Chromium, Firefox, and
WebKit matrices plus polling/navigation fallbacks remaining valid.

## Migration

Applications on 0.9 continue to work with polling. Enabling SSE/WS/preload is opt-in via
documented assets, routes, and configuration. No HDJ syntax break.
