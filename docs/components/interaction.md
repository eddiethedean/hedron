# Interaction

FastAPI and HTMX-oriented request/response components.

- [`RefreshButton`](refresh-button.md) — Refresh a target component through a typed reference or safe URL.
- [`Lazy`](lazy.md) — Load a component fragment when its placeholder enters the document.
- [`Poll`](poll.md) — Refresh a fragment at a bounded interval while it remains in the DOM.
- [`InfiniteScroll`](infinite-scroll.md) — Append the next fragment when a pagination sentinel is revealed.
- [`Pagination`](pagination.md) — Render crawlable page links that optionally swap a target through HTMX.
- [`Loading`](loading.md) — Show a polite busy status while a request or deferred component is pending.
- [`ErrorState`](error-state.md) — Present a recoverable request failure and optional HTMX retry.
