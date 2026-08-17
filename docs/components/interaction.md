# Interaction

FastAPI and HTMX-oriented request/response components.

- [`OobHost`](oob-host.md) — Stable out-of-band swap root with a reserved id.
- [`AttrHost`](attr-host.md) — Stable element that can receive attribute-only OOB updates.
- [`SseRegion`](sse-region.md) — Typed SSE host that registers the sse extension and connects to a same-origin stream.
- [`SseTrigger`](sse-trigger.md) — Listen for a named SSE event and optionally issue a cacheable GET swap.
- [`RefreshButton`](refresh-button.md) — Refresh a target component through a typed reference or safe URL.
- [`Lazy`](lazy.md) — Load a component fragment when its placeholder enters the document.
- [`Poll`](poll.md) — Refresh a fragment at a bounded interval while it remains in the DOM.
- [`InfiniteScroll`](infinite-scroll.md) — Append the next fragment when a pagination sentinel is revealed.
- [`Pagination`](pagination.md) — Render crawlable page links that optionally swap a target through HTMX.
- [`Loading`](loading.md) — Show a polite busy status while a request or deferred component is pending.
- [`ErrorState`](error-state.md) — Present a recoverable request failure and optional HTMX retry.
- [`Dialog`](dialog.md) — Present focused content in a native dialog with an explicit title and close path.
- [`ChatMessage`](chat-message.md) — Render one typed, escaped item in an application-owned chat transcript.
- [`ChatInput`](chat-input.md) — Submit an explicit chat message and optionally an attachment to a typed HTMX target.
