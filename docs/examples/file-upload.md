# File upload

CSRF-safe multipart upload with size and type checks in the action handler.

### Try it (simulated)

=== "Demo"

    Allowlisted .txt succeeds; .exe is rejected. Docs simulation (canned files, no disk picker).

    <!-- hedron-sim:file-upload -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
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
    ```

## Run without cloning the monorepo

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install "hedron>=0.46.0,<0.47" "uvicorn[standard]"
curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/file-upload/app.py -o app.py
uvicorn app:app --reload
```

Or paste the Code tab above into `app.py` (same source as the curl URL):

```python title="app.py"
from __future__ import annotations

from fastapi import File, Request, UploadFile

from hedron import FileUpload, Form, Hedron, Page, Stack, SubmitButton, Text, html
from hedron.security import csrf_token_for_request

app = Hedron(
    title="Upload demo",
    security="standard",
    explorer="off",
    session_secret="replace-in-production",
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
```

## Run (monorepo)

```bash
uv sync
uv run uvicorn app:app --app-dir examples/file-upload --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Upload a small `.txt` or `.csv`
(max 64 KiB in this demo).

## What it shows

- `FileUpload` control + `enctype="multipart/form-data"`
- Server-side `UploadFile` validation (type + size)
- CSRF hidden field on the form

Source: [`examples/file-upload`](https://github.com/eddiethedean/hedron/tree/main/examples/file-upload).
Related: [Cookbook — file upload](../guides/cookbook.md) ·
[Media downloads](../guides/media-downloads.md).
