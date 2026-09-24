---
description: Follow a Hedron application from a Posit Workbench development session to Posit Connect.
search:
  boost: 1.5
---

# Workbench and Connect

Use Posit Workbench as the development session and Posit Connect as the
publishing target. The optional `HedronPosit` facade can run the same application
locally, behind Workbench's session proxy, and as Connect FastAPI content.

The path starts with one Python project: develop and preview it in a Workbench
session, publish its application object as FastAPI content on Connect, then
give authorized users the Connect URL.

Start with the [Workbench first-app walkthrough](../first-app-posit-workbench.md)
for environment setup and a complete example. The [Posit deployment guide](../../guides/posit.md)
owns the detailed adapter contract and the [compatibility matrix](../../COMPATIBILITY.md)
owns supported product versions. `hedron-posit` is a Beta package, so check both
before a pilot.

## Develop behind Workbench's proxy

In an approved project environment with `hedron-posit` installed, construct the
application with `HedronPosit` and supply `HEDRON_SESSION_SECRET` through your
organization's secret mechanism. Then run:

```bash
hedron-posit check
hedron-posit run app:app
```

The launcher binds a local listener, resolves and validates Workbench's session
mount, and passes it to the application before import. Workbench's proxied
servers view opens the running app. Hedron scopes its URLs, assets, redirects,
and owned cookies to that mount. Do not hard-code a `/s/.../p/...` path or use a
Workbench session link as a durable URL: sessions can end or move. See Posit's
[proxied web server guide](https://docs.posit.co/ide/server-pro/user/vs-code/guide/proxying-web-servers.html)
for the Workbench side.

If Workbench does not provide `RS_SERVER_URL`, use the documented `--discover`
launcher path. [Posit Workbench](../../guides/posit-workbench.md) explains the
handoff, diagnostics, and mount errors.

## Publish as FastAPI content on Connect

Prepare a deployable project with its Python dependencies recorded in a
reviewed requirements or lock file. Install `hedron-posit` into the Connect
content environment; copying only its source tree is insufficient for the
documented Connect compatibility path. With an approved `rsconnect-python`
server configuration, publish the application object:

```bash
rsconnect deploy fastapi \
  -n <saved-server-name> \
  --entrypoint app:app \
  ./
```

Posit's [FastAPI publishing guide](https://docs.posit.co/connect/user/fastapi/)
documents the command and entrypoint. Connect gives the published content a
durable URL. Configure its access settings and application secrets through
your organization's platform process. The Hedron application must still
authorize its own protected routes, actions, and data. Connect credentials or
session headers are not automatic Hedron authorization.

If the application works locally but paths or cookies fail after publishing,
check the [Posit deployment guide](../../guides/posit.md) and run its redacted
diagnostics. A local `uvicorn` run on the Connect host does not reproduce a
Connect deployment's content path and cookie behavior.

Next: [Choose a migration pilot](migration-pilot.md).
