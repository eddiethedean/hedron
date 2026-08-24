# Hedron HTMX extension

**Status:** Proposed phase 0.64 contract  
**RFC:** [RFC-0091](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0091-HTMX-HEDRON-EXTENSION.md)

Phase 0.64 proposes the explicit `hedron` HTMX extension id, backed by the locally served and
pinned `htmx-ext-hedron` asset.

```python
Page(content, htmx_extensions={"hedron"})
```

The extension is intended to project Hedron's server-authored lifecycle into the browser:

- public lifecycle state markers;
- pending, terminal, stale, and superseded presentation;
- busy/disabled/announcement/focus behavior;
- CSP-safe lifecycle registration and cleanup; and
- bounded browser trace facts for Explorer and tests.

The names and schemas are provisional until the 0.64 Stage 0 contract lock. Pages that do not
declare the extension must continue to work with ordinary HTMX and full-page/full-fragment
fallbacks.

The extension does not add a client store, virtual DOM, hydration, JSX, response-script execution,
or a replacement for HTMX request and swap semantics.
