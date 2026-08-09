---
status: experimental
---

# Focused streaming

!!! danger "Experimental — prefer polling in production"

    Focused streaming is **experimental** (`hedron.experimental`) under Accepted 0.24
    **`polling_only`** ([LIVE_DISPOSITION](LIVE_DISPOSITION.md)). Classifications:
    [STABILITY.md](STABILITY.md). For Supported live status UX, use
    [Poll](../components/poll.md) + [Jobs](JOBS.md) /
    [Live interaction](../guides/live-interaction.md).

**Shipped (experimental) since** `0.10.0`. This page is a **contract outline**, not a
full production API. Prefer [Autodoc](AUTODOC.md) / `hedron.experimental` signatures for
exact types.

Helpers: `StreamingComponentResponse`, `stream_chunked_list`, `stream_document`,
`stream_tokens` — import from `hedron.experimental` (root attribute access remains a
compat shim). Core stream models live in `hedron_core.streaming`.

## `StreamingComponentResponse`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `content` | sync/async byte iterator | required | HTML chunks |
| `region_id` | `str` | required | Addressable region id (`X-Hedron-Stream-Region`) |
| `status_code` | `int` | `200` | HTTP status |
| `headers` | mapping | `None` | Extra headers |
| `fallback_html` | `str \| None` | `None` | When set, prefixes the body and sets `X-Hedron-Stream-Fallback: 1` |

**Returns:** a streaming HTTP response (`media_type` `text/html`). Default
`Cache-Control` is `no-store`.

## Helpers

| Helper | Input model | Role |
|---|---|---|
| `stream_tokens` | `TokenStream` | Token / LLM-style chunk stream into a region |
| `stream_chunked_list` | `ChunkedList` | Incremental list item HTML |
| `stream_document` | `StreamedDocument` | Chunked document HTML |

```python
from hedron.experimental import stream_chunked_list, stream_document, stream_tokens
from hedron_core.streaming import ChunkedList, StreamedDocument, TokenStream

return stream_tokens(TokenStream(region_id="out", tokens=["a", "b"]))
return stream_chunked_list(
    ChunkedList(items=[1, 2], region_id="rows", item_html=lambda item, i: f"<li>{item}</li>")
)
return stream_document(StreamedDocument(chunks=["<p>…</p>"], region_id="doc"))
```

## Errors and failure modes

| Condition | Behavior |
|---|---|
| Empty or incomplete iterator | Still HTTP `200` with whatever chunks were produced — clients need ordinary HTTP fallbacks |
| Invalid / unauthorized region | Application-owned; declare regions the same way as fragment routes — streaming does not invent allowlists |
| Proxy buffering / timeouts | Common failure in production — why **polling** remains the Supported path |
| Import from root `hedron` | Compat shim only; prefer `hedron.experimental` |

## See also

[Live interaction guide](../guides/live-interaction.md) · [Responses](RESPONSES.md) ·
[What’s ready](../guides/whats-ready.md)
