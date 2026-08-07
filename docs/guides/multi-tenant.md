# Multi-tenant isolation

Hedron does **not** provide a multi-tenant product. You own tenancy boundaries for
sessions, caches, jobs, fragments, and data sources. This page lists anti-patterns and
checklists for FastAPI (and portable notes for Flask/Django).

Also: [Enterprise diligence](enterprise-diligence.md) · [Threat model](threat-model.md) ·
[Cache](../api/CACHE.md) · [Jobs](../api/JOBS.md).

## Rules of thumb

1. **Never share** session secrets, CSRF secrets, or cache backends across tenants
   without tenant-prefixed keys.
2. **Authorize before render** — fragment HTML and job status must not leak
   cross-tenant data even when HTMX targets look correct.
3. Prefer `no-store` / private cache for authenticated per-user HTML when unsure.

## Cache keys

```python
# Anti-pattern: global key for authenticated HTML
# cache_key = "dashboard"

# Prefer tenant (and user) in the key space you control
cache_key = f"tenant:{tenant_id}:user:{user_id}:dashboard"
```

When using Hedron cache helpers, include tenant identity in any application-defined
key or tag you pass. Shared Redis without prefixes is a cross-tenant disclosure risk.

## Jobs and status channels

Authorize **before** enqueue and again on every status poll/SSE:

```python
def job_status_for_request(request, job_id: str):
    job = backend.get(job_id)
    if job is None or job.tenant_id != request.state.tenant_id:
        raise HTTPException(status_code=404)
    return job
```

Do not expose raw job IDs from one tenant to another via guessable URLs.

### Try it (simulated)

=== "Demo"

    Same-tenant poll succeeds; other tenant → 404 without leaking. Docs simulation.

    <!-- hedron-sim:tenant-deny -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
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


    @app.fragment("/jobs/{job_id}", region=status)
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
    ```

## Fragments and OOB

- Declare `fragment_regions` per route; unauthorized `HX-Target` → 403.
- Never put another tenant’s HTML into an OOB swap because a client sent a selector.
- Keep region IDs stable within a page; do not encode secrets in region IDs.

## Data sources

For Django QuerySet sources, pass an **already authorized** base QuerySet
(`DjangoQuerySetDataSource(authorized_qs, …)`). Never hand an unscoped model manager
to the data layer and “filter later” in the template.

## Checklist

- [ ] Cache keys / tags include tenant (or disable shared caching for auth HTML)
- [ ] Job submit + status authorize by tenant
- [ ] Fragment/OOB paths cannot emit cross-tenant markup
- [ ] Session cookie domain and CSRF secrets are per environment
- [ ] Object storage / download paths are tenant-scoped and authz-checked

## Related guides

[Authentication](authentication.md) · [Security](security.md) · [Deployment](deployment.md)
