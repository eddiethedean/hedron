from __future__ import annotations

import os
from typing import Annotated

from fastapi import File, Request, UploadFile

from hedron import FileUpload, Form, Hedron, Page, Stack, SubmitButton, Text, html
from hedron.security import csrf_token_for_request

app = Hedron(
    title="Upload demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

MAX_BYTES = 64 * 1024
ALLOWED = {".txt", ".csv"}


def _csrf(request: Request) -> str:
    return csrf_token_for_request(request, request.app.state.hedron_security)


@app.page("/")
def home(request: Request) -> Page:
    token = _csrf(request)
    return Page(
        Stack(
            Text("Upload a .txt or .csv file (max 64 KiB)"),
            Form(
                html.input(type="hidden", name="csrf_token", value=token),
                FileUpload(name="roster", accept=".txt,.csv"),
                SubmitButton("Upload"),
                action="/upload",
                method="post",
                enctype="multipart/form-data",
            ),
        ),
        title="Upload",
    )


@app.action("/upload", method="POST")
async def upload(roster: Annotated[UploadFile, File()]) -> Page:
    name = roster.filename or "upload"
    suffix = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if suffix not in ALLOWED:
        return Page(Text(f"Rejected type: {name}"), title="Rejected")
    data = await roster.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        return Page(Text("File too large"), title="Rejected")
    preview = data[:200].decode("utf-8", errors="replace")
    return Page(
        Stack(
            Text(f"Received {name} ({len(data)} bytes)"),
            Text(preview or "(empty)"),
        ),
        title="Uploaded",
    )
