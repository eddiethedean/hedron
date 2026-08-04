# Hedron `v0.10.0` live interaction acceptance

Phase 0.10 delivers evidence-backed live updates, focused streaming, page/session WebSocket
channels, Chat/Dialog primitives, media chunk transport contracts, HDJ head/streaming, and
opt-in navigation preload while preserving polling and ordinary HTTP fallbacks (RFC-0032).
Evidence is indexed by [`release-gate-0.10.toml`](release-gate-0.10.toml).

## Spec packet

- [x] RFC-0032 accepted; RFCs 0009/0013/0021/0025/0031 revised; D-044/D-045 recorded.
  *(`LIVE-10-001`)*

## Extension assets

- [x] Official `htmx-ext-sse` and `htmx-ext-head-support` pinned with digests, CSP, load order,
  and local `/hedron-static/ext/` serving (PAGE auto-inject). *(`EXT-10-001`)*

## HDJ (closes HDJ-DEF-010)

- [x] Registered fragment head management. *(`HDJ-10-001`)*
- [x] Two-phase template streaming preserving atomic `RenderResult` metadata. *(`HDJ-10-002`)*
- [x] Version-aware HTMX attribute/selector reporting. *(`HDJ-10-003`)*

## Live transports

- [x] Official SSE observation with resume (`Last-Event-ID`), terminal close, and Poll fallback.
  *(`SSE-10-001`)*
- [x] Job SSE preserves `JobBackend` contract; polling remains Supported. *(`JOB-006`)*
- [x] Focused `ChunkedList` / `StreamedDocument` / token streams with fallback prefix and delay.
  *(`STREAM-10-001`)*
- [x] Page/session WebSocket channels with concurrent producer, origin checks, and pong.
  *(`WS-10-001`)*

## UI and media

- [x] `Dialog` with native `<dialog>` a11y contract and modal boot via `hedron-ui.mjs`.
  *(`UI-10-001`)*
- [x] `ChatMessage` / `ChatInput` with a11y smoke (token streams remain helpers). *(`UI-10-002`)*
- [x] Media chunk session transport with duration/cadence/bandwidth budgets (no capture UI).
  *(`MEDIA-10-001`)*

## Navigation and exit

- [x] Opt-in navigation preload with `HX-Preloaded` and private-cache / cancel policy fields.
  *(`PRELOAD-10-001`)*
- [ ] Chromium/Firefox/WebKit full live matrix (reconnect/CSP/proxy/offline) — **Deferred**
  *(`BROWSER-10-001` → 0.10.x)*
- [ ] Load/proxy backpressure beyond in-memory budgets — **Deferred** *(`PERF-10-001` → 0.10.x)*
- [ ] Explorer live traces — **Deferred** *(`EXPLORER-10-001` → 0.10.x)*
- [ ] First-party live example app — **Deferred** *(`EXAMPLES-10-001` → 0.10.x)*
- [x] Full regression suite. *(`REGRESS-10-001`)*
- [x] Packaging rehearsal. *(`PKG-10-001`)*

## Exit

The phase can publish only when live/preload behavior never becomes a hidden correctness
dependency, polling and ordinary navigation remain valid, every release-gate row is `Verified`
or owned `Deferred`, and remaining Deferred browser/load/Explorer/example rows are explicitly
owned. Version stays `0.10.0` until tag/publish.
