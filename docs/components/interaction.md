# Interaction

FastAPI and HTMX-oriented request/response components.

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
