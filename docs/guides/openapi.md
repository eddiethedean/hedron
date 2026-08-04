# OpenAPI and HTML routes

Hedron does not invent a separate schema language. It rides FastAPI’s OpenAPI document
and marks HTML/component routes explicitly.

## What appears in `/docs`

| Route kind | Typical OpenAPI behavior |
|---|---|
| `@app.page` | Included by default (`include_in_schema=True`); response `text/html` |
| `@app.action` | Included by default |
| `@app.component` | **Excluded** by default (`include_in_schema=False`) — internal HTMX resources |
| Ordinary FastAPI JSON routes | Untouched |

Override with `include_in_schema=True/False` on the decorator when you want a fragment
in the schema or a page omitted.

## Practical tips

1. Keep JSON APIs and HTML pages on the same FastAPI app — Hedron only changes HTML
   returns and metadata.
2. Prefer documenting public **pages** and **actions**; leave HTMX fragment routes out of
   the schema unless partners need them.
3. Production generation strips source paths, private Explorer URLs, and sensitive
   examples (`x-hedron-*` extensions are sanitized).

## See also

[Hedron](../api/HEDRON.md) · [Router](../api/ROUTER.md) · [Plain FastAPI](plain-fastapi.md)
