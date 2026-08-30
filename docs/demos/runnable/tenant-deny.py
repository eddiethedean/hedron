import os

from fastapi import HTTPException, Request

from hedron import Hedron, Page, Stack, html, swap

app = Hedron(
    title="Tenant isolation",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

status = app.region("job-status", description="Job status")

# Demo store — real apps authorize against the job backend + session tenant.
JOBS = {
    "42": {"tenant_id": "A", "state": "Running"},
    "99": {"tenant_id": "B", "state": "Running"},
}


def current_tenant(request: Request) -> str:
    return str(request.session.get("tenant_id") or "A")


@app.page("/")
def home(request: Request) -> Page:
    request.session["tenant_id"] = "A"
    return Page(
        Stack(
            html.div(
                html.strong("Job status"),
                html.span("Authorize before every poll."),
                id=status.id,
            ),
            html.button(
                "Poll (same tenant)",
                type="button",
                **{"hx-get": "/jobs/42", "hx-target": status.selector, "hx-swap": "outerHTML"},
            ),
            html.button(
                "Poll (other tenant)",
                type="button",
                **{"hx-get": "/jobs/99", "hx-target": status.selector, "hx-swap": "outerHTML"},
            ),
        ),
        title="Tenant",
    )


@app.view("/jobs/{job_id}", fragment_regions=(status,))
def job_status(request: Request, job_id: str):
    job = JOBS.get(job_id)
    if job is None or job["tenant_id"] != current_tenant(request):
        raise HTTPException(status_code=404, detail="Not found")
    return swap(
        html.div(
            html.strong(job["state"]),
            html.span(f"tenant {job['tenant_id']} · job {job_id}"),
            id=status.id,
        )
    )
