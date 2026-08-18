# HTMX extensions

Phase 0.48 makes official HTMX 2 extensions a **declared** Hedron capability.
Pages name what they need; rendering injects only pinned local assets.

## Declare

Closed public ids: `sse`, `head-support`, `preload`. Morph is Deferred.

```python
from hedron_core.builtins import Page

Page(content, htmx_extensions={"sse", "preload"})
```

- Unset `htmx_extensions` keeps the 0.47 PAGE default (`sse` + `head-support`) and emits
  `HED-EXT-0001`.
- `htmx_extensions=()` or `ExtensionSet.empty()` loads **zero** extension bytes.
- `hx-ext` uses the public id (`sse`, not `htmx-ext-sse`). Writing `hx-ext` in HDJ never
  installs an asset (`HED-JINJA-0030`).

## SSE

Use `SseRegion` / `SseTrigger` with a same-origin `SafeUrl`. Event names are closed tokens.
Keep a `Poll` fallback. Helpers stay on `hedron.experimental`.

## Head-support

When `head-support` is in the compiled plan, PAGE responses may merge admitted `AssetRef`
values. Fragments never invent executable scripts.

## Preload

`HtmxLink(..., preload="mousedown")` is GET-only. It maps to `decide_preload` / `HX-Preloaded`.
Preload never changes authorization or availability.

## Try progressive navigation (simulated)

The links below swap one declared panel in the docs simulation. The Code tab is a complete
Hedron app and keeps each `href` usable as the non-JavaScript fallback. Add
`preload="mousedown"` only after the destination is safe to fetch speculatively.

=== "Demo"

    Choose a destination to swap the main panel while preserving an ordinary href fallback. Docs simulation.

    <!-- hedron-sim:component-htmx-link -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import Fragment, Hedron, HtmxLink, MainPanel, Page, Stack, html, swap

    app = Hedron(
        title="HtmxLink demo",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    panel = app.region("htmx-link-panel")


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                html.div(
                    HtmxLink("Reports", "/reports", target=panel.selector, swap="innerHTML"),
                    HtmxLink("Team", "/team", target=panel.selector, swap="innerHTML"),
                ),
                MainPanel(
                    html.strong("Choose a link"),
                    html.span("HtmxLink keeps href as the progressive-enhancement path."),
                    id=panel.id,
                ),
            ),
            title="HtmxLink",
        )


    @app.fragment("/reports", region=panel)
    def reports():
        return swap(
            Fragment(
                html.strong("Reports"),
                html.span("In-shell navigation with SafeUrl href fallback."),
            )
        )


    @app.fragment("/team", region=panel)
    def team():
        return swap(
            Fragment(
                html.strong("Team"),
                html.span("Ordinary href still works without JavaScript."),
            )
        )
    ```

## Security

Unknown ids, CDN URLs, digest mismatches, and undeclared morph fail closed (`HED-EXT-*`).
Keep `HED-HTMX-0001` / `HED-HTMX-0002`. See [error codes](error-codes.md).
