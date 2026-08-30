# Mutations with `@app.action`

Hedron has two common ways to handle unsafe HTTP methods (POST/PUT/PATCH/DELETE).
Pick one deliberately — do not mix them on the same form without understanding the
difference.

## Decision table

| You need… | Use | Why |
|---|---|---|
| Classic form POST that returns a **full page** (redirect or confirmation `Page`) | `@app.action("/…")` | Simplest CSRF-safe mutation; optional `fragment_regions` if HTMX also targets a region |
| HTMX POST that swaps a **declared region** / returns `InteractionResult` | `@app.action("/…", fragment_regions=(…,))` | Canonical mutation route with a region allowlist |
| DELETE/PUT with CSRF and a fragment body | `@app.action(..., method="DELETE", fragment_regions=…)` | Same allowlist contract |

`@app.action` **does** accept `fragment_regions`. Declare the swap host so HTMX `HX-Target`
is authorized (fail-closed 403 otherwise).

### Try it (simulated)

=== "Demo"

    HTMX fragment POST — submit swaps the declared result region. Docs simulation.

    <!-- hedron-sim:mutations-htmx -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    from __future__ import annotations

    import os
    from typing import Annotated

    from fastapi import Form, Request

    from hedron import Hedron, Page, Stack, SubmitButton, Text, TextInput, html
    from hedron.security import csrf_token_for_request

    app = Hedron(
        title="Mutations HTMX",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    result = app.region("save-result", description="Save result")


    def _csrf(request: Request) -> str:
        return csrf_token_for_request(request, request.app.state.hedron_security)


    @app.page("/")
    def home(request: Request) -> Page:
        token = _csrf(request)
        return Page(
            Stack(
                html.form(
                    html.input(type="hidden", name="csrf_token", value=token),
                    TextInput(name="note", value="Ship the docs demo"),
                    SubmitButton("Save"),
                    method="post",
                    **{
                        "hx-post": "/save",
                        "hx-target": result.selector,
                        "hx-swap": "innerHTML",
                    },
                ),
                html.div(id=result.id, role="status", aria={"live": "polite"}),
            ),
            title="Mutations",
        )


    @app.action("/save", method="POST", fragment_regions=(result,))
    def save(note: Annotated[str, Form()] = "") -> object:
        return html.div(html.strong("Saved in region"), Text(note))
    ```

## Classic form → `@action`

See the full pasteable sample in [Minimal form POST](minimal-form.md).

```python
@app.action("/save")
def save(request: Request, note: Annotated[str, Form()]) -> Page:
    return Page(Text(f"Saved: {note}"), title="Saved")
```

## HTMX fragment → `@app.action` POST

See [Forms and actions](forms-and-actions.md) for validation fragments.

```python
from hedron import FragmentRegion, InteractionResult

FORM = FragmentRegion(id="note-form", selector="#note-form")


@app.action("/save", method="POST", fragment_regions=(FORM,))
def save_fragment(...) -> InteractionResult:
    return InteractionResult(content=..., region_id=FORM.id, explanation="...")
```

## CSRF

Both paths require CSRF when security profiles enable it for unsafe methods. Seed the
cookie on a safe GET and send `csrf_token` (form field) or `X-CSRF-Token` (header).

## See also

[Action API](../api/ACTION.md) · [Interaction](../api/INTERACTION.md) ·
[Hedron methods](../api/HEDRON.md)
