# Migrate from plain FastAPI / Jinja + HTMX

Path for teams that already ship FastAPI (or Jinja templates) with HTMX and want reusable
Hedron components. For Streamlit, see [Migrate from Streamlit](streamlit-migration.md).

## What you keep

- FastAPI routing, dependency injection, middleware, OpenAPI, and async I/O
- Ordinary HTML/CSS and HTMX request/swap semantics
- Your auth, persistence, and deployment choices

## What Hedron adds

- `Page` / component trees instead of ad-hoc template strings for UI structure
- Fragment vs page rendering from explicit HTMX headers
- CSRF profiles, SafeUrl / TrustedHtml boundaries, and validated `InteractionResult` headers
- Optional CLI (`check`, `routes`, `build`) and Explorer for inspectability

## Mental model shift

| Concern | Plain FastAPI + Jinja | Hedron |
|---|---|---|
| UI structure | Template files + `context={...}` | Python components returning `Page` / fragments |
| Partial updates | Separate partial template or `if request.headers.get("HX-Request")` | Same handler; Hedron selects page vs fragment mode, or `@app.component` |
| CSRF | Manual cookie/header or Starlette SessionMiddleware DIY | Built-in profile (`security="standard"`) + `csrf_token_for_request` |
| HTMX response headers | Hand-set `HX-Trigger` / `HX-Retarget` | `InteractionResult` fields (validated) |
| Secrets in markup | Easy to leak via `{{ }}` | `Secret` / non-renderable types; escape by default |
| Staying on FastAPI only | Native | `HedronRouter` on a plain `FastAPI` — [Plain FastAPI](plain-fastapi.md) |

You do **not** have to rewrite the whole app. Migrate one route at a time and keep Jinja
for pages that are fine as templates (`hedron[jinja]` / HDJ) or leave them outside Hedron.

## Before / after: a page

**Before (Jinja TemplateResponse):**

```python
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "title": "Acme", "message": "Hello"},
    )
```

**After (Hedron page):**

```python
from hedron import Hedron, Heading, Page, Stack, Text

app = Hedron(title="Acme", security="standard", session_secret="replace-in-production")


@app.page("/")
def home() -> Page:
    return Page(
        Stack(Heading("Acme", level=1), Text("Hello")),
        title="Acme",
    )
```

## Before / after: an HTMX fragment

**Before:** a partial template returned when `HX-Request` is set, or a dedicated
`/partials/...` route.

**After:** declare a region and return `InteractionResult` from `@app.component` — see
[HTMX interactions](htmx-interactions.md). Direct navigation to the same URL can still
return a full `Page` when you keep a `@app.page` entry point.

## Before / after: a form POST

**Before:** Jinja form + manual CSRF token field + FastAPI `Form(...)` handler that
re-renders a template.

**After:** [Minimal form POST](minimal-form.md) with `csrf_token_for_request` (also
re-exported from `hedron`) and `@app.action`. For validation fragments, continue to
[Forms and actions](forms-and-actions.md).

## Suggested migration order

1. Install `hedron` beside your existing app ([installation](../getting-started/installation.md)).
2. Wrap or replace one read-only page with `@app.page` + built-ins
   ([quickstart](../getting-started/quickstart.md)).
3. Move one HTMX refresh to `@app.component` + `FragmentRegion`
   ([HTMX interactions](htmx-interactions.md)).
4. Port one form POST with CSRF ([minimal form](minimal-form.md)).
5. Wire persistence with FastAPI `Depends` as you already do; for grids see
   [Data applications](data-apps.md) (including SQLAlchemy).
6. Keep Jinja where you prefer templates via optional `hedron[jinja]`
   ([HDJ authoring](hdj-authoring.md)), or stay on Python components.
7. Turn on `hedron build` / production env when you deploy ([Deployment](deployment.md)).

## What not to rewrite first

- Auth and session stores — keep your existing FastAPI auth; see
  [Authentication](authentication.md) only when you want Hedron session helpers.
- Complex Jinja macros — leave them or migrate gradually to components.
- Client-side JS that is not HTMX — Hedron does not replace your existing scripts.

## Next

[Why Hedron](why-hedron.md) · [Evaluate Hedron](evaluate.md) ·
[Forms and actions](forms-and-actions.md) · [Data applications](data-apps.md) ·
[Deployment](deployment.md)
