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
