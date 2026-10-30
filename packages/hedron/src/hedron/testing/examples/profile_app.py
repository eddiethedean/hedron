"""Synthetic profile-form app for managed Playwright scenarios."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from html import escape
from typing import Annotated

from fastapi import Form as FastAPIForm
from fastapi.responses import HTMLResponse

from hedron import Hedron, Page
from hedron.mount import normalize_mount_path
from hedron_core.builtins.forms import CsrfField, Form, FormField, SubmitButton, TextInput
from hedron_core.html import html
from hedron_core.htmx.attrs import HtmxAttrs


def create_app(config: dict[str, object]) -> Hedron:
    """Build a disposable form app inside the managed ASGI child process."""
    title = config.get("title", "Profile settings")
    if not isinstance(title, str) or not title or len(title) > 80:
        raise ValueError("title must be a non-empty string of at most 80 characters")
    mount_value = config.get("root_path", "")
    if not isinstance(mount_value, str):
        raise ValueError("root_path must be a string")
    root_path = normalize_mount_path(mount_value)

    ready_state = {"ready": False}

    @asynccontextmanager
    async def synthetic_lifespan(app: Hedron) -> AsyncGenerator[None, None]:
        del app
        ready_state["ready"] = True
        try:
            yield
        finally:
            ready_state["ready"] = False

    app = Hedron(
        title=title,
        security="standard",
        session_secret="hedron-ui-synthetic-test-secret",
        explorer="off",
        root_path=root_path,
        lifespan=synthetic_lifespan,
    )

    @app.get("/_ui-testing/ready")
    def ready() -> dict[str, bool]:
        return {"ready": ready_state["ready"]}

    action_path = f"{root_path}/profile" if root_path else "/profile"

    @app.post("/profile")
    def save_profile(
        display_name: Annotated[str, FastAPIForm(min_length=3, max_length=60)],
    ) -> HTMLResponse:
        return HTMLResponse(f"Saved {escape(display_name)}")

    @app.page("/")
    def profile_page() -> Page:
        return Page(
            html.main(
                html.h1(title),
                Form(
                    CsrfField(),
                    FormField(
                        name="display_name",
                        label="Display Name",
                        control=TextInput(name="display_name"),
                        required=True,
                    ),
                    SubmitButton("Save profile"),
                    action=action_path,
                    method="post",
                    hx=HtmxAttrs(
                        method="post",
                        url=action_path,
                        target="#hedron-errors",
                        swap="innerHTML",
                    ),
                    data={"testid": "profile-form"},
                ),
                html.div(
                    "",
                    id="hedron-errors",
                    role="status",
                    aria={"live": "polite"},
                    data={"testid": "profile-status"},
                ),
            ),
            title=title,
            head=html.meta(
                name="htmx-config",
                content=(
                    '{"responseHandling":['
                    '{"code":"204","swap":false},'
                    '{"code":"422","swap":true,"error":true},'
                    '{"code":"[23]..","swap":true},'
                    '{"code":"[45]..","swap":false,"error":true}'
                    "]}"
                ),
            ),
        )

    return app
