---
description: A practical go/no-go checklist for evaluating Hedron in production.
---

# Production adoption checklist

Hedron is a beta project. Treat adoption as an explicit engineering decision and pin
the complete dependency set.

## Recommended scope

Hedron is a reasonable candidate for internal CRUD tools, admin applications, forms,
dashboards, and server-rendered workflows when your team owns the application’s
authentication, persistence, tenancy, deployment, and operational controls.

Prefer polling for live status. SSE and WebSocket helpers are experimental.

## Go/no-go checks

- [ ] The application uses the latest installable PyPI pin from [Current release](current-release.md).
- [ ] Python, FastAPI, Pydantic, and optional package versions are pinned.
- [ ] Authentication and authorization are implemented by the application and tested.
- [ ] `HEDRON_SESSION_SECRET` is set to a generated secret outside development.
- [ ] CSRF behavior is tested for every state-changing browser route.
- [ ] A shared job backend is configured before running multiple workers.
- [ ] Reverse-proxy path prefixes, cookies, headers, and TLS termination are tested.
- [ ] Production assets/manifests are built before starting the production server.
- [ ] Error handling, audit logging, observability, and rollback procedures exist.
- [ ] Experimental features have an approved fallback or are excluded.
- [ ] The team has verified the upgrade path using the [upgrade guide](upgrade.md).

## Stop and reassess when

- the deployment depends on undocumented proxy behavior;
- the application requires Plotly/Altair browser runtimes as a critical path;
- the application requires SSE/WebSockets without load and failure testing;
- the team needs vendor SLA, hosted operations, or managed identity;
- the required surface is only listed as Deferred or Experimental.

The [enterprise diligence guide](enterprise-diligence.md) contains the evidence questions
to take into a formal review.
