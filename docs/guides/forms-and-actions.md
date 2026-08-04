# Forms and actions

Deep dive: typed form that POSTs with HTMX, validates CSRF, and returns either a
validation fragment or a success update—without a client-side SPA.

If you have not yet shipped a classic POST, start with
[Minimal form POST](minimal-form.md). For GET-only fragment refresh, see
[HTMX interactions](htmx-interactions.md).

## What you will build

A page with an invite form. Submitting with invalid input redisplays the form
with errors. A valid submit replaces a result region with a success message.

```python title="app.py"
from __future__ import annotations

import json

from fastapi import Request
from pydantic import ValidationError

from hedron import (
    Field,
    Form,
    FormErrors,
    FormField,
    FormModel,
    FragmentRegion,
    Hedron,
    InteractionResult,
    Page,
    SafeUrl,
    Stack,
    SubmitButton,
    Text,
    TextInput,
    UrlPurpose,
    html,
)
from hedron.security import SecurityPolicy, csrf_token_for_request

app = Hedron(
    title="Invite",
    security="standard",
    session_secret="replace-in-production",
)

RESULT_REGION = FragmentRegion(
    id="invite-result",
    selector="#invite-result",
    description="Invite form result",
)


class InviteMember(FormModel):
    email: str = Field(min_length=3, label="Work email")


def _policy(request: Request) -> SecurityPolicy:
    return getattr(
        request.app.state,
        "hedron_security",
        SecurityPolicy.from_name("standard"),
    )


def _csrf(request: Request) -> str:
    return csrf_token_for_request(request, _policy(request))


def invite_form(
    *,
    csrf_token: str,
    values: dict[str, str] | None = None,
    errors: tuple[str, ...] = (),
):
    values = values or {}
    htmx_attrs: dict[str, str] = {
        "hx-post": "/invite",
        "hx-target": RESULT_REGION.selector,
        "hx-swap": "innerHTML",
        "hx-headers": json.dumps({"X-CSRF-Token": csrf_token}),
    }
    return Form(
        FormErrors(errors),
        html.input(type="hidden", name="csrf_token", value=csrf_token),
        FormField(
            name="email",
            label="Work email",
            control=TextInput(
                "email",
                value=values.get("email", ""),
                type="email",
                required=True,
            ),
            required=True,
        ),
        SubmitButton("Send invite"),
        action=SafeUrl.parse("/invite", purpose=UrlPurpose.FORM_ACTION),
        method="post",
        **htmx_attrs,
    )


@app.page("/")
def home(request: Request) -> Page:
    token = _csrf(request)
    return Page(
        Stack(
            Text("Invite a teammate"),
            html.div(invite_form(csrf_token=token), id=RESULT_REGION.id),
        ),
        title="Invite",
    )


@app.component("/invite", methods=["POST"], fragment_regions=(RESULT_REGION,))
async def invite(request: Request) -> InteractionResult:
    token = _csrf(request)
    form = await request.form()
    raw = {"email": str(form.get("email") or "")}
    try:
        data = InviteMember.model_validate(raw)
    except ValidationError as exc:
        messages = tuple(err["msg"] for err in exc.errors())
        return InteractionResult(
            content=html.div(
                invite_form(csrf_token=token, values=raw, errors=messages),
                id=RESULT_REGION.id,
            ),
            region_id=RESULT_REGION.id,
            explanation="Redisplay invite form with validation errors",
        )

    return InteractionResult(
        content=html.div(
            Text(f"Invite queued for {data.email}"),
            id=RESULT_REGION.id,
            role="status",
        ),
        region_id=RESULT_REGION.id,
        explanation="Confirm invite acceptance",
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
| `FormModel` | Typed, validated input shape for the form |
| `Form` / `FormField` | Native progressive-enhancement form with optional HTMX attrs |
| `@app.component(..., methods=["POST"])` | Mutation fragment route; CSRF validated by the security profile |
| `FragmentRegion` | Allowlisted HTMX target for the response |
| `InteractionResult` | Typed fragment content plus validated HTMX metadata |
| `csrf_token_for_request` | Stable token matching the cookie for this request |

Rendering a form never grants authorization. Persistence, permission checks, and
rate limits remain application code on the handler.

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
- [Security](security.md) for CSRF profiles and redirects
- [Authentication](authentication.md) to gate pages and actions
- [Reference app walkthrough](../examples/reference-app.md) for a fuller CRUD slice
- [AutoForm component](../components/auto-form.md) for constructor details
