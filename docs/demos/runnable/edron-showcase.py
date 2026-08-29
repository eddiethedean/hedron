"""Minimal Edron-only source companion for the interactive showcase."""

import edron as ed

theme = ed.theme("edron-showcase", accent="#0d9488")
app = ed.App(
    title="Edron Showcase",
    security="standard",
    session_secret="replace-in-production",
    theme=theme,
)


@app.page("/", title="Edron Showcase")
class Showcase(ed.Page):
    @ed.fragment(path="/pipeline/refresh")
    def pipeline(self) -> None:
        with self.card(title="Pipeline") as card:
            card.info("Transform in progress")
            card.text("Compose → validate → transform → publish")

    @ed.action(path="/approve", fallback="/")
    def approve(self) -> ed.Outcome:
        return ed.success("Publish queued")

    def render(self) -> None:
        self.heading("Command center")
        self.caption("A complete workspace composed from Edron page methods.")
        self.metric("Successful runs", "98.7%", delta="+2.1%", delta_tone="up")
        self.pipeline()
        self.button("Refresh pipeline", action=self.pipeline)
        self.button("Approve release", action=self.approve)
