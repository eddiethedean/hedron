---
status: experimental
---

# Focused streaming


!!! note "Stability"

    Classifications live in [STABILITY.md](STABILITY.md). Focused streaming is **experimental**
    (`hedron.experimental`) under Accepted 0.24 **`polling_only`**
    ([LIVE_DISPOSITION](LIVE_DISPOSITION.md)). Prefer polling in production.

**Status:** Shipped in `0.10.0` (experimental)

Helpers: `StreamingComponentResponse`, `stream_chunked_list`, `stream_document`,
`stream_tokens` — import from `hedron.experimental` (root attribute access remains a compat shim). Core stream models live in `hedron_core.streaming`.

## `StreamingComponentResponse`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `content` | sync/async byte iterator | required | HTML chunks |
| `region_id` | `str` | required | Addressable region id (`X-Hedron-Stream-Region`) |
| `status_code` | `int` | `200` | HTTP status |
| `headers` | mapping | `None` | Extra headers |
| `fallback_html` | `str \| None` | `None` | When set, prefixes the body and sets `X-Hedron-Stream-Fallback: 1` |

`media_type` is `text/html`. Default `Cache-Control` is `no-store`.

## Helpers

```python
from hedron.experimental import stream_chunked_list, stream_document, stream_tokens
from hedron_core.streaming import ChunkedList, StreamedDocument, TokenStream

return stream_tokens(TokenStream(region_id="out", tokens=["a", "b"]))
return stream_chunked_list(
    ChunkedList(items=[1, 2], region_id="rows", item_html=lambda item, i: f"<li>{item}</li>")
)
return stream_document(StreamedDocument(chunks=["<p>…</p>"], region_id="doc"))
```

## Errors

- Empty or incomplete streams still return `200` with whatever chunks were produced; clients
  should keep ordinary HTTP fallbacks.
- Invalid region ids are application-owned; Hedron does not invent fragment allowlists here.

## See also

[Live interaction guide](../guides/live-interaction.md) · [Responses](RESPONSES.md)
