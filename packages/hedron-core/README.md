# hedron-core

Framework-neutral typed rendering core for Hedron (`0.1.0`).

Defines models, security boundary types, components, the HTML serializer, and
the public `render(...) -> RenderResult` API with **no** FastAPI, Flask, Django,
ASGI, or WSGI dependency.

## Install

```bash
pip install hedron-core
# or
uv add hedron-core
```

Requires Python 3.12, 3.13, or 3.14.

## Quick start

```python
from hedron_core import Page, RenderContext, RenderMode, Text, render

result = render(
    Page(Text("Hello, Hedron"), title="Demo"),
    context=RenderContext.standalone(locale="en"),
    mode=RenderMode.PAGE,
)
print(result.html)
```

## What this package includes

- `Model`, `Props`, `FormModel`, `EventPayload`, and `Field`
- Trust boundary types: `Secret`, `TrustedHtml`, `SafeUrl`, `UrlPurpose`
- Component protocol, registry, diagnostics, and deterministic identity
- Context-aware HTML serializer and `render(...) -> RenderResult`
- Phase 0.1 built-ins for pages, forms, layout, landmarks, and content

## What it does not include

- HTTP routing, FastAPI/Flask/Django adapters, HTMX request handling
- HDN, scoped CSS, CLI, Component Explorer, charts, or data grids

Those arrive in later Hedron phases. See the [project README](https://github.com/eddiethedean/hedron)
and [roadmap](https://github.com/eddiethedean/hedron/blob/main/ROADMAP.md).

## License

No open-source license has been selected yet (decision D-030). Until one is
added, public redistribution as an open-source package is not authorized.
