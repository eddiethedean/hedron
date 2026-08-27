"""Hedron 0.15 data-app surface demo (ergonomics, controls, map, media, marks).

Run from the monorepo root:

    uv run uvicorn app:app --app-dir examples/data-app-0.15 --reload

Explorer is off; session_secret is set for local use only.
"""

from __future__ import annotations

from hedron import (
    Audio,
    DateInput,
    Gallery,
    Heading,
    Hedron,
    Map,
    MarkerSpec,
    Page,
    Stack,
    Text,
    html,
)

app = Hedron(
    title="Hedron 0.15 data-app demo",
    security="standard",
    session_secret="data-app-0.15-dev-only",
    explorer="off",
)

# Optional identity / connections (stubs — wire in real apps):
# from hedron.oidc import ...  # OIDC login/logout helpers; host session remains authoritative
# from hedron.connections import ...  # named registry + providers; prefer host DI/lifespan


@app.view("/panel")
def panel():
    return html.div(Text("Panel refreshed"))


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Heading("0.15 data-app surface", level=1),
            Text("refreshable view, typed controls, Map, Gallery/Audio, mark="),
            panel(),
            panel.refresh_button("Refresh panel"),
            DateInput("visit_date", value="2026-08-05", mark="visit-date"),
            Map(
                center=(37.77, -122.42),
                zoom=11,
                markers=[
                    MarkerSpec(
                        id="ferry",
                        lat=37.7955,
                        lon=-122.3937,
                        label="Ferry Building",
                    ),
                ],
                mark="city-map",
            ),
            Gallery(
                [
                    {
                        "src": "/hedron-static/favicon.svg",
                        "alt": "Hedron mark",
                        "caption": "Gallery stub",
                    }
                ],
                mark="demo-gallery",
            ),
            # Audio stub — replace src with a real audio asset in production apps.
            Audio("/media/demo.mp3", mark="demo-audio"),
        ),
        title="0.15 data-app demo",
    )
