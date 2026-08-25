# File upload

Secure upload composition with `UploadFlow`. Limits, cleanup, and authorization stay
explicit — Hedron does not own storage or malware scanning.

### Try it (simulated)

=== "Demo"

    Allowlisted .txt succeeds; .exe is rejected. Docs simulation (canned files, no disk picker).

    <!-- hedron-sim:file-upload -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
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
    ```

## Run without cloning the monorepo

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install "hedron>=0.64.0,<0.65" "uvicorn[standard]"
curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/file-upload/app.py -o app.py
uvicorn app:app --reload
```

Or paste the Code tab above into `app.py`.

## Run (monorepo)

```bash
uv sync
uv run uvicorn app:app --app-dir examples/file-upload --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Upload a small `.txt` or `.csv`
(max 64 KiB in this demo).

## What it shows

- `UploadFlow` with explicit `authorize` / `store` / `result` callbacks
- `UploadField` + `UploadBudget` (display and enforcement stay aligned)
- Application-owned storage (no inferred filesystem layout)

## Advanced — explicit `@app.command` / FileUpload

Lower to `FileUpload`, `Form(enctype="multipart/form-data")`, and `@app.command` when
ejecting. See [What’s new in 0.60](../guides/whats-new-0.60.md).

Source: [`examples/file-upload`](https://github.com/eddiethedean/hedron/tree/main/examples/file-upload).
