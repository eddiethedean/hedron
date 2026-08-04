# Best practices

Practical defaults for production Hedron apps from the 0.8 compatibility baseline onward.

## Pages vs fragments

- Use `@app.page` (or full `Page`) for document shells and first paint.
- Use `@app.component` / fragment routes for HTMX swaps into declared regions.
- Declare `FragmentRegion` allowlists when OOB or retarget is in play—do not authorize one
  `#id` and emit `hx-swap-oob` for another.

## CSRF and secrets

- Issue CSRF on safe GETs; send `X-CSRF-Token` (or form field) on unsafe methods.
- Flask: enforced on `hedron_route` / `HedronFlask.respond`.
- Django: use middleware; align `CSRF_HEADER_NAME` for portable headers.
- Never commit real `session_secret` / `SECRET_KEY` values; rotate per environment.

## URLs and redirects

- Pass navigation/asset URLs through `SafeUrl.parse(..., purpose=...)`.
- Prefer `redirect_local` / typed interaction redirects; avoid open redirects via raw headers.
- Adapter `extra_headers` cannot overwrite validated `HX-*` URL/selector fields or weaken
  `Cache-Control` to `public`.

## Caching

- Prefer `cache="private"` or `no-store` for authenticated fragments.
- Use `vary-htmx` when responses differ by `HX-Request` / target.

## Templates

- Prefer typed Python components for reusable behavior and authorization. Install `hedron-jinja`
  when trusted authors need standards-first control over HTML, CSS, JavaScript, Jinja, and HTMX;
  bind every callable component alias explicitly and keep dynamic trust crossings visible. HDN is
  not available on the 0.9+ train.
- Do not put secrets or untrusted HTML in templates—use `TrustedHtml` at trust boundaries.

## Adapters

- Install `hedron-flask` / `hedron-django` separately; they never pull FastAPI.
- Treat Deferred rows (QuerySet DataSource, Hedron Django forms, capture UI) as app-owned
  workarounds until their destination phase.

## Testing

- Unit-render with `render(...)` for components.
- Use TestClient / Flask/Django clients for CSRF and fragment headers.
- Opt into browser suite (`HEDRON_BROWSER=1`) for critical HTMX flows.

See also [Security](security.md), [HTMX interactions](htmx-interactions.md),
[Deployment](deployment.md).
