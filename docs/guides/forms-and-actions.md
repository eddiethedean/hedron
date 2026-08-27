# Forms and actions (advanced)

Use this page when you need explicit region allowlists and `InteractionResult` fragments.
For the golden-path form (`@app.action` + `CsrfField` + `save.form()`), start with
[Minimal form POST](minimal-form.md) and the
[Notes + SQLAlchemy recipe](../examples/notes-sqlalchemy.md).

Deep dive: a form that POSTs with HTMX, validates CSRF, and returns either a
validation fragment or a success update—without a client-side SPA.

## What you will build

A page with an invite form. Submitting with invalid input redisplays the form
with errors. A valid submit replaces a result region with a success message.

### Try it (simulated)

=== "Demo"

    Invalid email → FormErrors fragment. Valid email → success region. Docs simulation.

    <!-- hedron-sim:forms-invite -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    from __future__ import annotations

    import json
    import os

    from fastapi import Request
    from pydantic import ValidationError

    from hedron import (
        Field,
        Form,
        FormErrors,
        FormField,
        FormModel,
        Hedron,
        InteractionResult,
        Page,
        Stack,
        SubmitButton,
        Text,
        TextInput,
        html,
    )
    from hedron.security import csrf_token_for_request

    app = Hedron(
        title="Invite",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
    )

    form_region = app.region("invite-form", description="Invite form")


    class InviteMember(FormModel):
        email: str = Field(min_length=3, label="Work email")


    def _csrf(request: Request) -> str:
        return csrf_token_for_request(request, request.app.state.hedron_security)


    def invite_form(*, csrf_token: str, errors: tuple[str, ...] = ()):
        return html.div(
            Form(
                FormErrors(errors),
                html.input(type="hidden", name="csrf_token", value=csrf_token),
                FormField(
                    name="email",
                    label="Work email",
                    control=TextInput(name="email", placeholder="ada@example.com"),
                ),
                SubmitButton("Send invite"),
                **{
                    "hx-post": "/invite",
                    "hx-target": form_region.selector,
                    "hx-swap": "outerHTML",
                    "hx-headers": json.dumps({"X-CSRF-Token": csrf_token}),
                },
            ),
            id=form_region.id,
        )


    @app.page("/")
    def home(request: Request) -> Page:
        return Page(
            Stack(
                invite_form(csrf_token=_csrf(request)),
                Text("Try an empty value, then a real-looking email."),
            ),
            title="Invite",
        )


    @app.action("/invite", method="POST", fragment_regions=(form_region,))
    async def invite(request: Request) -> InteractionResult:
        form = await request.form()
        try:
            data = InviteMember.model_validate({"email": form.get("email", "")})
        except ValidationError:
            return InteractionResult(
                content=invite_form(
                    csrf_token=_csrf(request),
                    errors=("Enter a valid work email.",),
                ),
                status_code=422,
                region_id=form_region.id,
            )
        return InteractionResult(
            content=html.div(
                html.strong("Invite sent"),
                Text(f"Queued for {data.email}."),
                id=form_region.id,
                role="status",
            ),
            region_id=form_region.id,
        )
    ```

Run it:

```bash
uv run uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The GET seeds the
`hedron_csrf` cookie. The form embeds the same value as a hidden `csrf_token`
field and sends `X-CSRF-Token` via HTMX headers. Submit a short email to see
errors; submit a longer email to see the success region.

## Contracts in this loop

| Piece | Role |
|---|---|
| `FormModel` | Validated input shape for the form |
| `Form` / `FormField` | Native progressive-enhancement form with optional HTMX attrs |
| `@app.action(..., method="POST")` | Mutation route; CSRF validated by the security profile |
| `FragmentRegion` | Allowlisted HTMX target for the response |
| `InteractionResult` | Fragment content plus validated HTMX metadata |
| `csrf_token_for_request` | Stable token matching the cookie for this request |

Rendering a form never grants authorization. Persistence, permission checks, and
rate limits remain application code on the handler.

## Progressive enhancement (no-JS POST)

HTMX is optional. Critical mutations must succeed when the browser posts a normal form
**without** `HX-Request` (`PE-019`):

1. Keep a classic `<form method="post" action="…">` (Hedron `Form` does this by default).
2. On the POST handler, branch: if the request is HTMX, return an `InteractionResult`
   fragment; otherwise return a full `Page` or a `RedirectResponse` (303) after success.
3. CSRF still applies under `standard` / `strict` — seed the cookie on GET and include the
   hidden `csrf_token` field even when JS is off.

### Try it (simulated)

=== "Demo"

    HTMX fragment vs full-page confirmation path (PE-019). Docs simulation.

    <!-- hedron-sim:pe-paths -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from fastapi import Request
    from fastapi.responses import RedirectResponse

    from hedron import Form, Hedron, InteractionResult, Page, Stack, SubmitButton, Text, html
    from hedron.security import csrf_token_for_request

    app = Hedron(
        title="PE paths",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    result = app.region("pe-result", description="HTMX result")


    def _csrf(request: Request) -> str:
        return csrf_token_for_request(request, request.app.state.hedron_security)


    @app.page("/")
    def home(request: Request) -> Page:
        token = _csrf(request)
        return Page(
            Stack(
                Text("Invite note"),
                html.div(id=result.id),
                Form(
                    html.input(type="hidden", name="csrf_token", value=token),
                    html.label("Note", html.input(name="note", value="Ship PE-019")),
                    SubmitButton("Submit with HTMX"),
                    **{
                        "hx-post": "/save",
                        "hx-target": result.selector,
                        "hx-swap": "outerHTML",
                    },
                ),
                Form(
                    html.input(type="hidden", name="csrf_token", value=token),
                    html.label("Note", html.input(name="note", value="Ship PE-019")),
                    SubmitButton("Submit full page"),
                    action="/save",
                    method="post",
                ),
            ),
            title="PE",
        )


    @app.action("/save", method="POST")
    async def save(request: Request):
        form = await request.form()
        note = str(form.get("note") or "")
        if request.headers.get("HX-Request"):
            return InteractionResult(
                content=html.div(
                    html.strong("Fragment path"),
                    html.span(note),
                    id=result.id,
                ),
                region_id=result.id,
            )
        return RedirectResponse(f"/done?note={note}", status_code=303)


    @app.page("/done")
    def done(request: Request) -> Page:
        return Page(Text(f"Full-page confirmation: {request.query_params.get('note', '')}"), title="Done")
    ```

```python
from fastapi.responses import RedirectResponse

@app.action("/invite", method="POST")
async def invite(request: Request):
    # parse form + validate CSRF / FormModel …
    if request.headers.get("HX-Request"):
        return InteractionResult(...)  # fragment path
    return RedirectResponse("/", status_code=303)  # no-JS success
```

See [Minimal form POST](minimal-form.md) and [Accessibility](accessibility.md)
(`PE-019` / landmarks / `Page(scripts=)`).

## AutoForm shortcut

For schema-driven fields without an HTMX `target`, `AutoForm` generates labelled
inputs and a CSRF hidden field from a `FormModel`:

```python
from hedron import AutoForm

AutoForm(
    InviteMember,
    action="/invite",
    csrf_token=csrf_token,
    values=values,
    errors=errors,
    submit_label="Send invite",
)
```

Obtain `csrf_token` with `csrf_token_for_request(request, policy)` after a safe
GET. Prefer the explicit `Form` composition above when you need `hx-target` /
`hx-post` today; see [AutoForm](../components/auto-form.md).

## Test the POST path

```python title="test_invite.py"
from fastapi.testclient import TestClient

from app import app


def test_invite_validation_and_success() -> None:
    with TestClient(app) as client:
        seed = client.get("/")
        assert seed.status_code == 200
        token = client.cookies["hedron_csrf"]

        bad = client.post(
            "/invite",
            data={"email": "ab", "csrf_token": token},
            headers={
                "HX-Request": "true",
                "HX-Target": "#invite-result",
                "X-CSRF-Token": token,
            },
        )
        assert bad.status_code == 200
        assert "invite-result" in bad.text

        ok = client.post(
            "/invite",
            data={"email": "ada@example.com", "csrf_token": token},
            headers={
                "HX-Request": "true",
                "HX-Target": "#invite-result",
                "X-CSRF-Token": token,
            },
        )
        assert ok.status_code == 200
        assert "Invite queued" in ok.text
```

## Where to go next

- [HTMX interactions](htmx-interactions.md) for GET refresh loops
- [Accessibility](accessibility.md) for PE / landmarks / `Page(scripts=)` and claim boundaries
- [Security](security.md) for CSRF profiles and redirects
- [Authentication](authentication.md) to gate pages and actions
- [Reference app walkthrough](../examples/reference-app.md) for a fuller CRUD slice
- [AutoForm component](../components/auto-form.md) for constructor details
