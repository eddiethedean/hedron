import os

from hedron import Hedron, Page, Stack, html, swap

app = Hedron(
    title="Job poll",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

job = app.region("job-panel", description="Job status")

_STEPS = [
    ("Queued", "Waiting for worker"),
    ("Running", "Step 1 of 2"),
    ("Running", "Step 2 of 2"),
    ("Complete", "84 records imported; polling stopped"),
]
_tick = 0


def panel(state: str, detail: str):
    return html.div(
        html.strong(state),
        html.span(detail),
        id=job.id,
        role="status",
        aria={"live": "polite"},
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            panel("Idle", "Click to start a bounded poll cycle."),
            html.button(
                "Start job poll",
                type="button",
                **{
                    "hx-get": "/jobs/42",
                    "hx-target": job.selector,
                    "hx-swap": "outerHTML",
                },
            ),
        ),
        title="Poll",
    )


@app.fragment("/jobs/42", region=job)
def job_tick():
    global _tick
    state, detail = _STEPS[min(_tick, len(_STEPS) - 1)]
    _tick = min(_tick + 1, len(_STEPS) - 1)
    return swap(panel(state, detail))
