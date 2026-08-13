"""Reference app using one HedronPosit object locally and on Workbench."""

from __future__ import annotations

import os
import secrets

from fastapi import Request
from starlette.responses import JSONResponse

from hedron import Page, Stack, Text, redirect_local
from hedron_posit import HedronPosit

app = HedronPosit(
    title="HedronPosit Workbench reference",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET") or secrets.token_urlsafe(32),
)


@app.page("/")
def home(request: Request) -> Page:
    request.session["smoke"] = "ok"
    return Page(
        Stack(Text("Hello from HedronPosit on Workbench")),
        title="Home",
    )


@app.page("/login")
def login() -> Page:
    return Page(Text("Workbench login target"), title="Login")


@app.page("/go")
def go():
    return redirect_local("/login")


@app.get("/workbench-status", include_in_schema=False)
def workbench_status() -> JSONResponse:
    return JSONResponse(app.workbench_status())


@app.get("/posit-status", include_in_schema=False)
def posit_status() -> JSONResponse:
    return JSONResponse(app.posit_status().as_dict())
