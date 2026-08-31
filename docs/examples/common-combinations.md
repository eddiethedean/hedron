---
description: Standalone Hedron recipes combining authentication, CRUD, validation, dashboards, uploads, jobs, and polling.
search:
  boost: 1.7
---

# Common combination recipes

These are complete single-file learning applications for workflows that are usually needed
together. Copy one recipe into `app.py`, install its listed dependencies, and run
`uvicorn app:app --reload`.

Each recipe labels its local-only substitute. In-memory records and threads make the interaction
easy to inspect; they are not durable or multi-worker production infrastructure.

## Authenticated CRUD

Session login/logout protects a notes workspace. Create, update, and delete are POST actions with
CSRF fields; authentication is a FastAPI dependency rather than a visual component property.

```python title="app.py"
from __future__ import annotations

import os
from typing import Annotated

from fastapi import Depends, Form as FastAPIForm, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from hedron import (
    Alert,
    Card,
    CsrfField,
    Form,
    Heading,
    Hedron,
    Page,
    Stack,
    SubmitButton,
    Text,
    TextInput,
    html,
    redirect_local,
)
from hedron.auth import install_authenticated_from_session

app = Hedron(
    title="Private notes",
    security="standard",
    explorer="off",
    session_secret=os.environ.get(
        "HEDRON_SESSION_SECRET",
        "replace-in-production",
    ),
)
install_authenticated_from_session(app, session_key="username")

USERS = {"ada": "correct-horse"}  # Demo only. Use an IdP/password service.
NOTES: dict[int, str] = {1: "Ship the authenticated CRUD recipe"}
NEXT_ID = 2


def require_user(request: Request) -> str:
    username = request.session.get("username")
    if not isinstance(username, str) or not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sign in required",
        )
    return username


@app.action("/login", method="POST", fallback="/login")
def login(
    request: Request,
    username: str = FastAPIForm(...),
    password: str = FastAPIForm(...),
):
    if USERS.get(username) != password:
        return redirect_local("/login?error=1")
    request.session.clear()
    request.session["username"] = username
    return redirect_local("/")


@app.action("/logout", method="POST", fallback="/login")
def logout(request: Request):
    request.session.clear()
    return redirect_local("/login")


@app.action(
    "/notes",
    method="POST",
    fallback="/",
    dependencies=[Depends(require_user)],
)
def create_note(body: str = FastAPIForm(...)):
    global NEXT_ID
    value = body.strip()
    if not value:
        raise HTTPException(status_code=422, detail="Note cannot be blank")
    NOTES[NEXT_ID] = value[:500]
    NEXT_ID += 1
    return redirect_local("/")


@app.action(
    "/notes/{note_id}",
    method="POST",
    fallback="/",
    dependencies=[Depends(require_user)],
)
def update_note(note_id: int, body: str = FastAPIForm(...)):
    if note_id not in NOTES:
        raise HTTPException(status_code=404, detail="Note not found")
    value = body.strip()
    if not value:
        raise HTTPException(status_code=422, detail="Note cannot be blank")
    NOTES[note_id] = value[:500]
    return redirect_local("/")


@app.action(
    "/notes/{note_id}/delete",
    method="POST",
    fallback="/",
    dependencies=[Depends(require_user)],
)
def delete_note(note_id: int):
    NOTES.pop(note_id, None)
    return redirect_local("/")


@app.page("/login")
def login_page(request: Request, error: str | None = None) -> Page | RedirectResponse:
    if request.session.get("username"):
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    return Page(
        Stack(
            Heading("Sign in", level=1),
            Alert("Invalid credentials", tone="danger") if error == "1" else None,
            Form(
                CsrfField(),
                TextInput("username", required=True),
                TextInput("password", type="password", required=True),
                SubmitButton("Sign in"),
                action="/login",
                method="post",
            ),
        ),
        title="Sign in",
    )


def note_card(note_id: int, body: str) -> Card:
    return Card(
        Stack(
            Form(
                CsrfField(),
                TextInput("body", value=body, required=True),
                SubmitButton("Update"),
                action=f"/notes/{note_id}",
                method="post",
            ),
            Form(
                CsrfField(),
                SubmitButton("Delete"),
                action=f"/notes/{note_id}/delete",
                method="post",
            ),
        ),
        title=f"Note {note_id}",
    )


@app.page("/")
def home(username: Annotated[str, Depends(require_user)]) -> Page:
    cards = [note_card(note_id, body) for note_id, body in sorted(NOTES.items())]
    return Page(
        Stack(
            Heading("Private notes", level=1),
            Text(f"Signed in as {username}"),
            logout.button("Sign out"),
            Form(
                CsrfField(),
                TextInput("body", required=True),
                SubmitButton("Create note"),
                action="/notes",
                method="post",
            ),
            *cards,
        ),
        title="Private notes",
    )
```

Run with `pip install "hedron>=1.0.1,<1.1" "uvicorn[standard]"`. Sign in with
`ada` / `correct-horse`. Replace the credential dictionary and process-local notes with an identity
provider, password hashing/rate limiting where applicable, and transactional durable storage.

## Validation with fragment errors

This form progressively enhances a normal POST. HTMX receives a bounded validation/success
fragment; a browser without JavaScript receives a full error page or a 303 redirect.

```python title="app.py"
from __future__ import annotations

import json
import os

from fastapi import Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ValidationError, field_validator

from hedron import (
    Form,
    FormErrors,
    FormField,
    Hedron,
    InteractionResult,
    Page,
    Stack,
    SubmitButton,
    Text,
    TextInput,
    html,
)
from hedron.htmx import is_htmx_request
from hedron.security import csrf_token_for_request

app = Hedron(
    title="Invitations",
    security="standard",
    explorer="off",
    session_secret=os.environ.get(
        "HEDRON_SESSION_SECRET",
        "replace-in-production",
    ),
)

form_region = app.region("invite-form", description="Invitation form")


class Invite(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or len(normalized) > 254:
            raise ValueError("Enter a valid email address")
        return normalized


def csrf(request: Request) -> str:
    return csrf_token_for_request(request, request.app.state.hedron_security)


def invite_form(request: Request, errors: tuple[str, ...] = ()):
    token = csrf(request)
    return html.div(
        Form(
            FormErrors(errors),
            html.input(type="hidden", name="csrf_token", value=token),
            FormField(
                name="email",
                label="Work email",
                control=TextInput("email", type="email", required=True),
            ),
            SubmitButton("Send invite"),
            action="/invite",
            method="post",
            **{
                "hx-post": "/invite",
                "hx-target": form_region.selector,
                "hx-swap": "outerHTML",
                "hx-headers": json.dumps({"X-CSRF-Token": token}),
            },
        ),
        id=form_region.id,
    )


@app.page("/")
def home(request: Request) -> Page:
    return Page(
        Stack(invite_form(request), Text("Submit an invalid address, then a valid one.")),
        title="Invite member",
    )


@app.action(
    "/invite",
    method="POST",
    fallback="/",
    fragment_regions=(form_region,),
)
async def invite(request: Request) -> InteractionResult | Page | RedirectResponse:
    submitted = await request.form()
    try:
        data = Invite.model_validate({"email": submitted.get("email", "")})
    except ValidationError:
        errors = ("Enter a valid work email.",)
        if is_htmx_request(request):
            return InteractionResult(
                content=invite_form(request, errors),
                status_code=422,
                region_id=form_region.id,
            )
        return Page(invite_form(request, errors), title="Invite member")

    # Persist and authorize the invitation in an application service here.
    if not is_htmx_request(request):
        return RedirectResponse("/?sent=1", status_code=303)
    return InteractionResult(
        content=html.div(
            Text(f"Invite queued for {data.email}"),
            id=form_region.id,
            role="status",
        ),
        region_id=form_region.id,
    )
```

Run with the base Hedron/Uvicorn dependencies. A production handler must authenticate, authorize
the target organization, persist transactionally, and rate-limit invitations.

## Filtered paginated dashboard

Filters and pagination are safe GETs. Every link has a full-page `href` and an HTMX fragment URL,
so the app remains navigable without JavaScript and swaps only the results with HTMX.

```python title="app.py"
from __future__ import annotations

import os
from typing import Literal

from hedron import Heading, Hedron, Page, SafeUrl, Stack, Table, Text, UrlPurpose, html

app = Hedron(
    title="People dashboard",
    security="standard",
    explorer="off",
    session_secret=os.environ.get(
        "HEDRON_SESSION_SECRET",
        "replace-in-production",
    ),
)

Role = Literal["all", "admin", "member"]
PEOPLE = [
    ("1", "Ada", "admin"),
    ("2", "Grace", "member"),
    ("3", "Alan", "member"),
    ("4", "Katherine", "admin"),
    ("5", "Edsger", "member"),
    ("6", "Margaret", "admin"),
    ("7", "Barbara", "member"),
]
PAGE_SIZE = 3
results = app.region("people-results", description="Filtered people")


def normalized_page(page: int, total: int) -> int:
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    return min(max(page, 1), pages)


def link(label: str, *, role: Role, page: int, current: bool = False):
    full_url = f"/?role={role}&page={page}"
    fragment_url = f"/people?role={role}&page={page}"
    return html.a(
        label,
        href=SafeUrl.parse(full_url, purpose=UrlPurpose.NAVIGATION),
        aria={"current": "page"} if current else {},
        **{
            "hx-get": fragment_url,
            "hx-target": results.selector,
            "hx-swap": "innerHTML",
        },
    )


def results_content(role: Role, page: int):
    filtered = [row for row in PEOPLE if role == "all" or row[2] == role]
    page = normalized_page(page, len(filtered))
    start = (page - 1) * PAGE_SIZE
    rows = filtered[start : start + PAGE_SIZE]
    pages = max(1, (len(filtered) + PAGE_SIZE - 1) // PAGE_SIZE)
    return Stack(
        html.nav(
            link("All", role="all", page=1, current=role == "all"),
            link("Admins", role="admin", page=1, current=role == "admin"),
            link("Members", role="member", page=1, current=role == "member"),
            aria={"label": "Role filter"},
        ),
        Text(f"{len(filtered)} matching people"),
        Table(
            headers=("ID", "Name", "Role"),
            rows=rows,
            caption="People",
        ),
        html.nav(
            *[
                link(str(number), role=role, page=number, current=number == page)
                for number in range(1, pages + 1)
            ],
            aria={"label": "Results pages"},
        ),
    )


@app.page("/")
def dashboard(role: Role = "all", page: int = 1) -> Page:
    return Page(
        Stack(
            Heading("People dashboard", level=1),
            html.section(
                results_content(role, page),
                id=results.id,
                role="region",
                aria={"label": "People results", "live": "polite"},
            ),
        ),
        title="People dashboard",
    )


@app.view("/people", fragment_regions=(results,))
def people(role: Role = "all", page: int = 1):
    return results_content(role, page)
```

Replace the list slice with a bounded database query that applies authorization and tenant filters
before `LIMIT`/`OFFSET`. Keep filter values allowlisted and include all active filters in every
pagination URL.

## Upload, background job, and polling

The upload action enforces filename/type/size limits, submits a scoped job, and redirects to a page
that polls until a terminal result. The in-memory backend and thread are local-learning substitutes
for Redis plus Celery/RQ or another durable worker.

```python title="app.py"
from __future__ import annotations

import os
import threading
import time

from fastapi import File, HTTPException, Request, UploadFile

from hedron import (
    ComponentRef,
    CsrfField,
    FileUpload,
    Form,
    Heading,
    Hedron,
    Page,
    Poll,
    Stack,
    Status,
    SubmitButton,
    Text,
    redirect_local,
)
from hedron.builtins.files import validate_upload_filename
from hedron.jobs import enqueue_durable, job_status_response
from hedron_core.jobs import InMemoryJobBackend, JobState

backend = InMemoryJobBackend()

app = Hedron(
    title="CSV jobs",
    security="standard",
    explorer="off",
    session_secret=os.environ.get(
        "HEDRON_SESSION_SECRET",
        "replace-in-production",
    ),
    job_backend=backend,
)

MAX_BYTES = 256 * 1024
STATUS_PATH = "/jobs/{job_id}/status"


def scope(request: Request) -> dict[str, str]:
    subject = request.session.get("auth_subject")
    if not isinstance(subject, str) or not subject:
        subject = "local-demo-user"
        request.session["auth_subject"] = subject
    return {"auth_subject": subject, "tenant_id": "local-demo-tenant"}


def process_csv(job_id: str, data: bytes) -> None:
    backend.mark(job_id, JobState.RUNNING)
    time.sleep(0.5)
    row_count = max(0, len(data.decode("utf-8", errors="replace").splitlines()) - 1)
    backend.mark(job_id, JobState.SUCCEEDED, result={"rows": row_count})


@app.action("/upload", method="POST", fallback="/")
async def upload(request: Request, roster: UploadFile = File(...)):
    try:
        filename = validate_upload_filename(roster.filename or "")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Unsafe filename") from exc
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=415, detail="Upload a CSV file")
    data = await roster.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 256 KiB")

    owner = scope(request)
    job_id = enqueue_durable(
        "csv.row-count",
        {"filename": filename, "bytes": len(data)},
        **owner,
    )
    threading.Thread(
        target=process_csv,
        args=(job_id, data),
        daemon=True,
    ).start()
    return redirect_local(f"/jobs/{job_id}")


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Heading("Process a CSV", level=1),
            Form(
                CsrfField(),
                FileUpload(
                    name="roster",
                    accept=".csv,text/csv",
                    maximum_size=MAX_BYTES,
                ),
                SubmitButton("Start job"),
                action="/upload",
                method="post",
                enctype="multipart/form-data",
            ),
        ),
        title="CSV jobs",
    )


@app.page("/jobs/{job_id}")
def job_page(job_id: str, request: Request) -> Page:
    owner = scope(request)
    if backend.get(job_id, **owner) is None:
        raise HTTPException(status_code=404, detail="Job not found")
    ref = ComponentRef(
        logical_id=f"job-status-{job_id}",
        path=STATUS_PATH.format(job_id=job_id),
        method="GET",
    )
    return Page(
        Stack(
            Heading("CSV processing", level=1),
            Text(f"Job {job_id}"),
            Poll(
                ref=ref,
                interval_ms=1000,
                content=Status("Queued…", variant="activity"),
            ),
        ),
        title="Job status",
    )


@app.get("/jobs/{job_id}/status", include_in_schema=False)
def status_response(job_id: str, request: Request):
    owner = scope(request)
    current = backend.get(job_id, **owner)
    if current is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_status_response(current, **owner)
```

Run with `pip install "hedron>=1.0.1,<1.1" "uvicorn[standard]" "python-multipart"`.
In production, submit only serializable metadata to a durable backend, put the upload in authorized
object storage, have every worker use the same scope/keyspace, and configure cleanup/retention.

## Verify any recipe

```bash
python -m hedron --app app:app routes
python -m hedron --app app:app check
```

Then add `TestClient` coverage for the full page, authentication/authorization failures, the CSRF
POST, the authorized HTMX target, and each terminal outcome. Before deployment, follow
[Ship a Hedron app](../guides/ship.md).
