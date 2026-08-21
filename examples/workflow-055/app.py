"""Reference list/detail workflow for phase 0.55 (no application JavaScript)."""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse

from hedron import AppShell, Hedron, MasterDetail, Page, Text
from hedron.capabilities import MappingCapabilityProvider
from hedron.csp import CspReporting, ingest_csp_report
from hedron.replay import MemoryReplayStore
from hedron.upload import UploadBudget, materialize_upload
from hedron.workflow import WorkflowManifest

ITEMS = {"1": "Alpha", "2": "Beta"}

app = Hedron(
    title="Workflow 0.55",
    security="standard",
    explorer="off",
    session_secret="workflow-055",
)
app.state.hedron_capabilities = MappingCapabilityProvider({"items.edit"})
app.state.hedron_replay_store = MemoryReplayStore()
app.state.hedron_workflow_manifest = WorkflowManifest(
    app_id="workflow-055",
    layout_regions=("master", "detail"),
    capabilities=("items.edit",),
    action_safety={"revoke": "idempotent:required"},
    migration_status="workflow_055",
)


@app.page("/", fragment_regions=("master", "detail"))
def home(request: Request):
    selection = request.query_params.get("id")
    state = "ready"
    detail = None
    if selection is None:
        state = "empty"
    elif selection not in ITEMS:
        # Do not disclose whether a denied record exists — treat as empty/not-found.
        state = "empty"
    else:
        detail = Text(ITEMS[selection])
    body = MasterDetail(
        Text("\n".join(f"{k}: {v}" for k, v in ITEMS.items())),
        detail,
        selection=selection if selection in ITEMS else None,
        state=state,
        master_id="master",
        detail_id="detail",
    )
    return Page(AppShell(body=body, brand=Text("Workflow 055")), title="Workflow 055")


@app.action("/revoke", capability="items.edit", idempotency="required")
def revoke(request: Request):
    return Text("revoked")


@app.action("/upload", capability="items.edit")
async def upload(request: Request):
    form = await request.form()
    upload_file = form.get("file")
    if upload_file is None:
        return Text("missing")
    raw = await upload_file.read()
    handle = materialize_upload(
        filename=getattr(upload_file, "filename", "upload.bin") or "upload.bin",
        content=raw,
        content_type=getattr(upload_file, "content_type", None),
        budget=UploadBudget(maximum_size=1_000_000, allowed_extensions=(".txt",)),
    )
    try:
        name = handle.filename
    finally:
        handle.cleanup()
    return Text(f"uploaded:{name}")


@app.post("/hedron/csp-report")
async def csp_report(request: Request):
    body = await request.body()
    parsed = ingest_csp_report(
        body,
        content_type=request.headers.get("content-type"),
        reporting=CspReporting(max_body_bytes=4096),
    )
    if parsed is None:
        return PlainTextResponse("dropped", status_code=204)
    return JSONResponse({"ok": True, "report": parsed})
