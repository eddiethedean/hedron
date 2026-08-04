# Migrate from plain FastAPI / Jinja + HTMX

Short path for teams that already ship FastAPI (or Jinja templates) with HTMX and want
typed Hedron components. For Streamlit, see [Migrate from Streamlit](streamlit-migration.md).

## What you keep

- FastAPI routing, dependency injection, middleware, OpenAPI, and async I/O
- Ordinary HTML/CSS and HTMX request/swap semantics
- Your auth, persistence, and deployment choices

## What Hedron adds

- Typed `Page` / component trees instead of ad-hoc template strings for UI structure
- Fragment vs page rendering from explicit HTMX headers
- CSRF profiles, SafeUrl / TrustedHtml boundaries, and validated `InteractionResult` headers
- Optional CLI (`check`, `routes`, `build`) and Explorer for inspectability

## Minimal mapping

| Plain FastAPI + Jinja/HTMX | Hedron |
|---|---|
| `FastAPI()` + Jinja `TemplateResponse` | `Hedron(...)` + `@app.page` returning `Page(...)` |
| Partial template for `HX-Request` | Same handler; Hedron selects fragment mode, or `@app.component` |
| Manual CSRF cookie/header wiring | Built-in profile (`security="standard"`) + `csrf_token_for_request` |
| Hand-rolled `HX-Trigger` / retarget | `InteractionResult` fields (validated) |
| `FastAPI` only (no facade) | `HedronRouter` on a plain `FastAPI` — [Plain FastAPI](plain-fastapi.md) |

## Suggested steps

1. Install `hedron` beside your existing app ([installation](../getting-started/installation.md)).
2. Convert one read-only page to `@app.page` + built-ins ([quickstart](../getting-started/quickstart.md)).
3. Move one HTMX refresh to `@app.component` + `FragmentRegion`
   ([HTMX interactions](htmx-interactions.md)).
4. Port one form POST with CSRF ([minimal form](minimal-form.md)).
5. Keep Jinja where you prefer templates via optional `hedron[jinja]`
   ([HDJ authoring](hdj-authoring.md)), or stay on Python components.

## Next

[Why Hedron](why-hedron.md) · [Evaluate Hedron](evaluate.md) ·
[Forms and actions](forms-and-actions.md) · [Deployment](deployment.md)
