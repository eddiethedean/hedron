"""File upload demo with size/type checks. Local learning only."""

from __future__ import annotations

from fastapi import File, UploadFile

from hedron import CsrfField, FileUpload, Form, Hedron, Page, Stack, SubmitButton, Text

app = Hedron(
    title="Upload demo",
    security="standard",
    explorer="off",
    session_secret="replace-in-production",
)

MAX_BYTES = 64 * 1024
ALLOWED = {".txt", ".csv"}


@app.command("/upload", fallback="/")
async def upload(roster: UploadFile = File(...)) -> Page:
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


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Text("Upload a .txt or .csv file (max 64 KiB)"),
            Form(
                CsrfField(),
                FileUpload(name="roster", accept=".txt,.csv"),
                SubmitButton("Upload"),
                action=upload,
                enctype="multipart/form-data",
            ),
        ),
        title="Upload",
    )
