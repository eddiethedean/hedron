import os

from hedron import ComponentRef, Hedron, Page, Poll, html, swap

app = Hedron(
    title="Poll demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

box = app.region("poll-box")
ref = ComponentRef(
    logical_id="job-42",
    path="/jobs/42",
    target=box.selector,
    swap="innerHTML",
)

_STEPS = [
    ("Queued", "Waiting for a worker"),
    ("Running", "Step 1 of 2"),
    ("Running", "Step 2 of 2"),
    ("Complete", "84 records imported; polling stopped"),
]
_tick = 0


def panel(state: str, detail: str):
    return html.div(
        html.strong(state),
        html.span(detail),
        id=box.id,
        role="status",
    )


@app.page("/")
def home() -> Page:
    return Page(
        Poll(
            ref=ref,
            interval_ms=700,
            target_id=box.id,
            content=panel(*_STEPS[0]),
        ),
        title="Poll",
    )


@app.view("/jobs/42", fragment_regions=(box,))
def tick():
    global _tick
    state, detail = _STEPS[min(_tick, len(_STEPS) - 1)]
    _tick = min(_tick + 1, len(_STEPS) - 1)
    return swap(panel(state, detail))
