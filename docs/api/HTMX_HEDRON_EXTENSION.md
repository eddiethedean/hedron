# Hedron HTMX extension

**Status:** Implemented opt-in phase 0.64 contract
**RFC:** [RFC-0091](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0091-HTMX-HEDRON-EXTENSION.md)

Phase 0.64 combines bounded presentation contracts with an explicit `hedron` HTMX extension id,
backed by the locally served and pinned `htmx-ext-hedron` asset. The complete issue inventory and
track boundary are recorded in the [phase 0.64 roadmap](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md#phase-064-refined-scope).

```python
Page(content, htmx_extensions={"hedron"})
```

The extension is intended to project Hedron's server-authored lifecycle into the browser:

- public lifecycle state markers;
- pending, terminal, stale, and superseded presentation;
- busy/disabled/announcement/focus behavior;
- CSP-safe lifecycle registration and cleanup; and
- bounded browser trace facts for Explorer and tests.

The pinned local asset is `/hedron-static/ext/hedron.js` (`htmx-ext-hedron` 0.64.0). Pages that do
not declare the extension continue to work with ordinary HTMX and full-page/full-fragment
fallbacks. Lifecycle behavior is opt-in per host using `data-hedron-state-host="true"`.

The shared Python contract exposes bounded state transitions, generation-aware stale-response
handling, and validated `latest` / `replace` / `queue` / `drop` concurrency attributes.

The extension does not add a client store, virtual DOM, hydration, JSX, response-script execution,
or a replacement for HTMX request and swap semantics.
