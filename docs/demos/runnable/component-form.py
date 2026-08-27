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
    title="Form demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

region = app.region("demo-form")


class Invite(FormModel):
    email: str = Field(min_length=3, label="Email address")


def _csrf(request: Request) -> str:
    return csrf_token_for_request(request, request.app.state.hedron_security)


def form_body(*, csrf_token: str, errors: tuple[str, ...] = ()):
    return html.div(
        Form(
            FormErrors(errors),
            html.input(type="hidden", name="csrf_token", value=csrf_token),
            FormField(
                name="email",
                label="Email address",
                control=TextInput(name="email", placeholder="ada@example.com"),
            ),
            SubmitButton("Submit"),
            **{
                "hx-post": "/demo",
                "hx-target": region.selector,
                "hx-swap": "outerHTML",
                "hx-headers": json.dumps({"X-CSRF-Token": csrf_token}),
            },
        ),
        id=region.id,
    )


@app.page("/")
def home(request: Request) -> Page:
    return Page(Stack(form_body(csrf_token=_csrf(request))), title="Form")


@app.action("/demo", method="POST", fragment_regions=(region,))
async def submit(request: Request) -> InteractionResult:
    form = await request.form()
    try:
        data = Invite.model_validate({"email": form.get("email", "")})
    except ValidationError:
        return InteractionResult(
            content=form_body(
                csrf_token=_csrf(request),
                errors=("Enter a valid work email.",),
            ),
            status_code=422,
            region_id=region.id,
        )
    return InteractionResult(
        content=html.div(
            html.strong("Submitted"),
            Text(f"Queued for {data.email}."),
            id=region.id,
            role="status",
        ),
        region_id=region.id,
    )
