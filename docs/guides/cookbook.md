# Cookbook

Short recipes for common Hedron patterns. Prefer the linked guides when you need
full context.

## CSRF-safe POST fragment

See [Forms and actions](forms-and-actions.md). Seed the cookie with a GET, embed
`csrf_token` / `X-CSRF-Token`, return `InteractionResult` into a declared
`FragmentRegion`.

## Refresh a region (GET)

See [HTMX interactions](htmx-interactions.md): `RefreshButton` +
`@app.component` + `FragmentRegion`.

## Out-of-band swap

Return `InteractionResult` with `oob=(OobUpdate(...), ...)` for secondary regions.
Keep every OOB selector inside the route’s `fragment_regions` allowlist.

## Polling

Use `Poll` / `Lazy` with a fragment endpoint. Prefer polling on Flask/Django when
SSE is not Supported on that host ([live interaction](live-interaction.md)).

## File upload / download

`FileUpload` + action route for ingest; `DownloadButton` / `safe_download_response`
for downloads. Validate size/type in application code.

## Charts as fragments

Install `hedron[charts]` (+ backend extra). Follow [Charts and HTMX](charts-and-htmx.md).

## Turn Explorer off in production

`Hedron(explorer="off", production=True)` or `HEDRON_ENV=production`. Never ship
`explorer="development"`.

## Multi-worker sessions

Sticky sessions or an external session store; do not assume in-memory session
affinity. Job backends that need Redis set `HEDRON_REDIS_URL` explicitly.

## Production start failure `HED-BUILD-0003`

Run `hedron build` and deploy the manifest before `HEDRON_ENV=production`. See
[Deployment](deployment.md).

## Protect a route prefix

```python
users = HedronRouter(prefix="/users", dependencies=[Depends(require_user)])
```

See [Authentication](authentication.md).
