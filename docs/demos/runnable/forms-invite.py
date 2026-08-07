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


@app.component("/invite", methods=["POST"], fragment_regions=(form_region,))
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
