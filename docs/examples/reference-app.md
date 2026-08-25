# Reference app walkthrough

Annotated tour of
[`examples/reference-app`](https://github.com/eddiethedean/hedron/tree/main/examples/reference-app)—
the FastAPI flagship CRUD sample and multi-worker production kitchen sink on the living
**0.64.x** train. Prefer [session auth](session-auth.md) and
[notes + SQLAlchemy](notes-sqlalchemy.md) for a shorter second-hour path; use this app
when you want the full archetype in one tree.

Contract: [PRODUCTION_ARCHETYPE](../api/PRODUCTION_ARCHETYPE.md). Example README:
[`examples/reference-app/README.md`](https://github.com/eddiethedean/hedron/blob/main/examples/reference-app/README.md).

Click through the pattern demos below (docs simulations for CSRF, fragments, and chart
**panel** refresh — not a live login), then run the full app locally or via production
compose. Outside the workspace, install `hedron[charts]>=0.63.0,<0.64` from PyPI
(the repository tip is `0.64.0`, while the public PyPI release remains `0.63.0`; see
[Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor)).

!!! warning "Credentials for this app"

    The runnable reference app uses **HTTP Basic** `admin` / `secret`.
    Session-form demos with `ada` / `correct-horse` live only on
    [session auth](session-auth.md) — they will not work against this app.

## Ingredient checklist (production archetype)

| Ingredient | How this app covers it |
|---|---|
| reverse-proxy subpath | Caddy `handle_path /hedron/*` + `HEDRON_ROOT_PATH=/hedron` |
| Redis job/cache | `HEDRON_REDIS_URL` wires `RedisJobBackend` (`h1:job:`) + `RedisCacheBackend` (`h1:c:`) on one client (requires the `redis` package — see `requirements-prod.txt`) |
| sticky sessions or external session store | Signed cookie sessions/CSRF (default external path); optional Caddy sticky noted in `Caddyfile` |
| `HEDRON_ENV=production` | Set in compose + Dockerfile; refuses placeholder / `change-me` secrets |
| CSP | `security="strict"` + `[tool.hedron.asset_policy] strict_csp = true` |
| Explorer off | `explorer="off"` when `HEDRON_ENV=production` |
| multi-worker | uvicorn `--workers 2` + Redis-backed job/cache |

## Auth gate

The runnable reference app uses **HTTP Basic** (`admin` / `secret`) — not a session
login form. For a CSRF-safe session sign-in recipe (demo credentials `ada` /
`correct-horse`), use [session auth](session-auth.md) instead; do not try those
credentials against `examples/reference-app`.

## CSRF on forms (simulated)

Unsafe POSTs require a CSRF token. Missing token → 403:

=== "Demo"

    POST with CSRF succeeds; missing token → 403. Docs simulation.

    <!-- hedron-sim:csrf-guard -->

=== "Code"

    Focused runnable listing for this pattern—not the full reference app. Use the run instructions below for the production archetype:

    ```python title="app.py"
    import os

    from fastapi import Request

    from hedron import (
        CsrfField,
        Form,
        Hedron,
        Hx,
        Page,
        Stack,
        SubmitButton,
        Text,
        csrf_token_for_request,
    )

    app = Hedron(
        title="CSRF demo",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )


    def _csrf(request: Request) -> str:
        return csrf_token_for_request(request, request.app.state.hedron_security)


    @app.page("/")
    def home(request: Request) -> Page:
        token = _csrf(request)
        return Page(
            Stack(
                Text("GET seeds hedron_csrf"),
                Form(
                    CsrfField(token=token),
                    SubmitButton("POST with CSRF"),
                    action="/do",
                    method="post",
                    hx=Hx(target="body", swap="outerHTML"),
                ),
                Form(
                    SubmitButton("POST without CSRF"),
                    action="/do",
                    method="post",
                ),
            ),
            title="CSRF",
        )


    @app.action("/do", method="POST")
    def do_action() -> Page:
        return Page(Text("POST ok"), title="Done")
    ```

## Fragment list refresh (simulated)

Create/delete rows with HTMX swaps into a declared region — the same idea as the
user table on the dashboard:

=== "Demo"

    Fragment list refresh pattern used throughout the reference app. Docs simulation.

    <!-- hedron-sim:crud-notes -->

=== "Code"

    Focused runnable listing for this pattern—not the full reference app. Use the run instructions below for the production archetype:

    ```python title="app.py"
    from __future__ import annotations

    import os
    from typing import Annotated
    from uuid import uuid4

    from fastapi import Form, Request

    from hedron import CsrfField, Hedron, Page, Stack, SubmitButton, Text, TextInput, html

    app = Hedron(
        title="CRUD notes",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
    )

    NOTES: dict[str, str] = {}
    listing = app.region("notes-list", description="Notes list")


    def render_list(request: Request):
        del request  # request kept for signature parity with fragment handlers
        if not NOTES:
            return html.div(Text("No notes yet."), id=listing.id)
        items = []
        for note_id, body in NOTES.items():
            items.append(
                html.li(
                    Text(body),
                    " ",
                    html.form(
                        CsrfField(),
                        html.input(type="hidden", name="note_id", value=note_id),
                        SubmitButton("Delete"),
                        method="post",
                        **{
                            "hx-post": "/notes/delete",
                            "hx-target": listing.selector,
                            "hx-swap": "outerHTML",
                        },
                    ),
                )
            )
        return html.div(html.ul(*items), id=listing.id)


    @app.page("/")
    def home(request: Request) -> Page:
        return Page(
            Stack(
                render_list(request),
                html.form(
                    CsrfField(),
                    TextInput(name="note", placeholder="New note"),
                    SubmitButton("Add note"),
                    method="post",
                    **{
                        "hx-post": "/notes",
                        "hx-target": listing.selector,
                        "hx-swap": "outerHTML",
                    },
                ),
            ),
            title="CRUD",
        )


    @app.component("/notes", methods=["POST"], fragment_regions=(listing,))
    def add_note(request: Request, note: Annotated[str, Form()] = "") -> object:
        text = note.strip()
        if text:
            NOTES[str(uuid4())] = text
        return render_list(request)


    @app.component("/notes/delete", methods=["POST"], fragment_regions=(listing,))
    def delete_note(request: Request, note_id: Annotated[str, Form()] = "") -> object:
        NOTES.pop(note_id, None)
        return render_list(request)
    ```

## Chart panel refresh (simulated)

Dashboard chart routes return `InteractionResult` fragments:

=== "Demo"

    Refresh advances a short chart sequence (then wraps). Docs simulation.

    <!-- hedron-sim:charts-htmx -->

=== "Code"

    Focused runnable listing for this pattern—not the full reference app. Use the run instructions below for the production archetype:

    ```python title="app.py"
    import os

    from hedron import Hedron, InteractionResult, Page, Stack, html
    from hedron_charts import LineChart

    app = Hedron(
        title="Charts HTMX",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    panel = app.region("chart-panel", description="Chart panel")


    INITIAL_ROWS = [
        {"month": "Jan", "revenue": 10},
        {"month": "Feb", "revenue": 14},
        {"month": "Mar", "revenue": 18},
    ]
    UPDATED_ROWS = [
        {"month": "Jan", "revenue": 10},
        {"month": "Feb", "revenue": 14},
        {"month": "Mar", "revenue": 21},
    ]


    def chart_panel(rows, *, description: str):
        return html.section(
            LineChart(
                rows,
                x="month",
                y="revenue",
                title="Monthly revenue",
                description=description,
            ),
            id=panel.id,
            aria={"label": "Revenue chart panel"},
        )


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                chart_panel(
                    INITIAL_ROWS,
                    description="Revenue increased throughout the quarter.",
                ),
                html.button(
                    "Refresh chart panel",
                    type="button",
                    **{
                        "hx-get": "/charts/refresh",
                        "hx-target": panel.selector,
                        "hx-swap": "outerHTML",
                    },
                ),
            ),
            title="Charts",
        )


    @app.component("/charts/refresh", fragment_regions=(panel,))
    def refresh() -> InteractionResult:
        return InteractionResult(
            content=chart_panel(
                UPDATED_ROWS,
                description="March revenue increased to 21 after the refresh.",
            ),
            region_id=panel.id,
            trigger="chartRefreshed",
            cache="vary-htmx",
            explanation="Primary fragment refresh for chart panel",
        )
    ```

## Run (local demo)

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
uv run uvicorn app:app --app-dir examples/reference-app --reload
```

Sign in with HTTP Basic: **`admin` / `secret`**. Local/demo mode keeps Explorer in
`development` and uses an in-memory demo secret — replace before any shared deploy.

## Production compose (canonical archetype)

```bash
export HEDRON_SESSION_SECRET="$(openssl rand -hex 32)"   # required — no weak default
export HEDRON_ALLOW_DEMO_AUTH=1                          # sample Basic auth only
docker compose --profile full up --build
# App via proxy: http://localhost:8080/hedron/
```

Compose requires `HEDRON_SESSION_SECRET` (production gate refuses secrets containing
`change-me`). Demo HTTP Basic is gated behind `HEDRON_ALLOW_DEMO_AUTH=1`. Redis client +
uvicorn are installed in the image; for non-Docker prod installs use
[`requirements-prod.txt`](https://github.com/eddiethedean/hedron/blob/main/examples/reference-app/requirements-prod.txt).
Prefer this path when validating production posture —
[Ship a Hedron app](../guides/ship.md) ·
[Deployment](../guides/deployment.md).

## What the app demonstrates

| Concern | Where to look (`examples/reference-app/`) | Simulated above |
|---|---|---|
| `Hedron()` app + security profile | `app.py` → `build_hedron_app()` | — |
| Session/user gate | `require_user` + router `dependencies=[Depends(require_user)]` | Auth gate |
| CSRF on forms | `csrf_token_for_request` + hidden field / `hx-headers` in `_create_form` | CSRF on forms |
| Create user POST | `@users.action("", method="POST")` | Fragment list refresh |
| Fragment table refresh | `@users.component("/table")`, addressable `user_table` | Fragment list refresh |
| DataEditor / Auto / charts | dashboard + `/charts/*` (`hedron[charts]>=0.64.0,<0.65` or the monorepo source) | Chart panel refresh (sim) |
| Color mode | `ColorModeToggle` + preference cookie helpers | — |
| Production archetype | compose + `requirements-prod.txt` + README ingredient table | — |

## Suggested reading order in the code

1. `build_hedron_app()` — how the app is constructed and the build dir is prepared
2. `home` page handler — CSRF token issuance for the dashboard
3. `_create_form` — progressive form with HTMX target on `#user-table`
4. User create/update/delete actions — validation, store mutation, fragment returns
5. Chart routes — `InteractionResult` + declared fragment regions

## Related guides

- [Forms and actions](../guides/forms-and-actions.md)
- [Authentication](../guides/authentication.md)
- [HTMX interactions](../guides/htmx-interactions.md)
- [Charts and HTMX](../guides/charts-and-htmx.md)
- [Plain FastAPI + HedronRouter](../guides/plain-fastapi.md)
- [PRODUCTION_ARCHETYPE](../api/PRODUCTION_ARCHETYPE.md)
