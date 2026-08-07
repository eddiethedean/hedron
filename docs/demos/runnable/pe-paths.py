import os

from fastapi import Request
from fastapi.responses import RedirectResponse

from hedron import Form, Hedron, InteractionResult, Page, Stack, SubmitButton, Text, html
from hedron.security import csrf_token_for_request

app = Hedron(
    title="PE paths",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

result = app.region("pe-result", description="HTMX result")


def _csrf(request: Request) -> str:
    return csrf_token_for_request(request, request.app.state.hedron_security)


@app.page("/")
def home(request: Request) -> Page:
    token = _csrf(request)
    return Page(
        Stack(
            Text("Invite note"),
            html.div(id=result.id),
            Form(
                html.input(type="hidden", name="csrf_token", value=token),
                html.label("Note", html.input(name="note", value="Ship PE-019")),
                SubmitButton("Submit with HTMX"),
                **{
                    "hx-post": "/save",
                    "hx-target": result.selector,
                    "hx-swap": "outerHTML",
                },
            ),
            Form(
                html.input(type="hidden", name="csrf_token", value=token),
                html.label("Note", html.input(name="note", value="Ship PE-019")),
                SubmitButton("Submit full page"),
                action="/save",
                method="post",
            ),
        ),
        title="PE",
    )


@app.action("/save", method="POST")
async def save(request: Request):
    form = await request.form()
    note = str(form.get("note") or "")
    if request.headers.get("HX-Request"):
        return InteractionResult(
            content=html.div(
                html.strong("Fragment path"),
                html.span(note),
                id=result.id,
            ),
            region_id=result.id,
        )
    return RedirectResponse(f"/done?note={note}", status_code=303)


@app.page("/done")
def done(request: Request) -> Page:
    return Page(Text(f"Full-page confirmation: {request.query_params.get('note', '')}"), title="Done")
