"""Guide-page demos authored with Hedron components + hedron-sim."""

from __future__ import annotations

from hedron import (
    Form,
    FormErrors,
    InteractionResult,
    OobHost,
    OobUpdate,
    Page,
    RefreshButton,
    Stack,
    SubmitButton,
    html,
    swap,
)
from hedron_core.interaction import InteractionPolicy
from hedron_sim import SimApp, embed_demo, sim_form, sim_local_time

__all__ = [
    "build_allowlist_403_demo",
    "build_charts_htmx_demo",
    "build_cookbook_oob_demo",
    "build_crud_demo",
    "build_forms_invite_demo",
    "build_htmx_interactions_demo",
    "build_live_poll_demo",
    "build_mutations_htmx_demo",
]


def _hx(**attrs: str) -> dict[str, str]:
    """Map ``hx_get=...`` kwargs to allowlisted ``hx-get`` HTML attributes."""
    out: dict[str, str] = {}
    for key, value in attrs.items():
        if key.startswith("hx_"):
            out["hx-" + key[3:].replace("_", "-")] = value
        else:
            out[key.replace("_", "-")] = value
    return out


def build_htmx_interactions_demo() -> str:
    app = SimApp(title="HTMX interactions", demo_id="htmx-interactions")
    status = app.region("hx-guide-status", description="Status panel")
    notes = app.region("hx-guide-notes", description="Notes counter")
    probe = app.region("hx-guide-probe", description="Allowlist probe")

    def status_panel():
        return html.div(
            html.strong("Service healthy"),
            html.span(f"Checked at {sim_local_time()}"),
            id=status.id,
            class_="hedron-sim-card",
            role="status",
            aria={"live": "polite"},
        )

    def notes_panel():
        return html.div(
            html.strong("Sample notes region"),
            html.span("Allowlisted #hx-guide-notes — count stays 0 in this sim"),
            id=notes.id,
            class_="hedron-sim-card",
            role="status",
            aria={"live": "polite"},
        )

    def probe_panel():
        return html.div(
            html.strong("Allowlisted swap"),
            html.span("HX-Target matched the declared probe region"),
            id=probe.id,
            class_="hedron-sim-card",
            role="status",
            aria={"live": "polite"},
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                status_panel(),
                RefreshButton.for_region(status, href="/status", label="Refresh status"),
                notes_panel(),
                RefreshButton.for_region(notes, href="/notes-count", label="Refresh sample region"),
                html.div(
                    html.button(
                        "Correct target → 200",
                        type="button",
                        class_="hedron-sim-btn hedron-sim-btn--primary",
                        **_hx(hx_get="/probe", hx_target=probe.selector, hx_swap="outerHTML"),
                    ),
                    html.button(
                        "Wrong #panel → 403",
                        type="button",
                        class_="hedron-sim-btn",
                        **_hx(hx_get="/probe", hx_target="#panel", hx_swap="outerHTML"),
                    ),
                    class_="hedron-sim-row",
                    role="group",
                    aria={"label": "Allowlist demo"},
                ),
                html.div(
                    html.strong("Allowlist probe"),
                    html.span("Try the correct vs wrong target buttons."),
                    id=probe.id,
                    class_="hedron-sim-card",
                    role="status",
                ),
                html.p(
                    "Click a control to simulate an HTMX fragment request.",
                    class_="hedron-sim-muted",
                ),
            ),
            title="HTMX",
        )

    @app.fragment("/status", region=status)
    def refresh_status():
        return swap(status_panel())

    @app.fragment("/notes-count", region=notes)
    def refresh_notes():
        return swap(notes_panel())

    @app.fragment("/probe", region=probe)
    def refresh_probe():
        return swap(probe_panel())

    return embed_demo(app)


def build_forms_invite_demo() -> str:
    app = SimApp(title="Invite form", demo_id="forms-invite")
    form_region = app.region("invite-form", description="Invite form")

    def invite_form(*, errors: tuple[str, ...] = ()):
        children: list = []
        if errors:
            children.append(FormErrors(errors))
        children.extend(
            [
                html.label(
                    "Work email",
                    html.input(
                        id="invite-email",
                        name="email",
                        type="email",
                        placeholder="ada@example.com",
                        autocomplete="email",
                    ),
                ),
                SubmitButton("Send invite"),
            ]
        )
        return html.div(
            Form(
                *children,
                novalidate="novalidate",
                **_hx(
                    hx_post="/invite",
                    hx_target=form_region.selector,
                    hx_swap="outerHTML",
                ),
            ),
            id=form_region.id,
        )

    def success_panel():
        return html.div(
            html.strong("Invite sent"),
            html.span(f"Queued for {sim_form('email')}."),
            id=form_region.id,
            class_="hedron-sim-card",
            role="status",
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                invite_form(),
                html.p(
                    "Try an empty or short value, then a real-looking email.",
                    class_="hedron-sim-muted",
                ),
            ),
            title="Invite",
        )

    def invalid():
        return InteractionResult(
            content=invite_form(errors=("Enter a valid work email.",)),
            status_code=422,
            region_id=form_region.id,
        )

    def valid():
        return InteractionResult(
            content=success_panel(),
            status_code=200,
            region_id=form_region.id,
        )

    @app.action(
        "/invite",
        region=form_region,
        validate="email",
        variants={"invalid": invalid, "valid": valid},
    )
    def invite_default():
        return invalid()

    return embed_demo(app)


def build_live_poll_demo() -> str:
    app = SimApp(title="Job poll", demo_id="live-poll")
    job = app.region("job-panel", description="Job status")

    def panel(state: str, detail: str):
        return html.div(
            html.strong(state),
            html.span(detail),
            id=job.id,
            class_="hedron-sim-card",
            role="status",
            aria={"live": "polite"},
        )

    steps = (
        lambda: swap(panel("Queued", "Waiting for worker")),
        lambda: swap(panel("Running", "Step 1 of 2")),
        lambda: swap(panel("Running", "Step 2 of 2")),
        lambda: swap(panel("Complete", "84 records imported; polling stopped")),
    )

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                panel("Idle", "Click to start a bounded poll cycle."),
                html.button(
                    "Start job poll",
                    type="button",
                    class_="hedron-sim-btn hedron-sim-btn--primary",
                    **_hx(hx_get="/jobs/42", hx_target=job.selector, hx_swap="outerHTML"),
                ),
                html.p(
                    "Each click advances one poll step (four steps, then wraps).",
                    class_="hedron-sim-muted",
                ),
            ),
            title="Poll",
        )

    @app.fragment("/jobs/42", region=job, sequence=steps)
    def job_tick():
        return steps[0]()

    return embed_demo(app)


def build_cookbook_oob_demo() -> str:
    app = SimApp(title="OOB swap", demo_id="cookbook-oob")
    main = app.region("settings-main", description="Primary settings")
    host = app.region("toast-host", description="OOB toast host")

    def primary(draft: bool = True):
        title = "Draft settings" if draft else "Settings saved"
        detail = "Primary region — not saved yet." if draft else "Primary region updated."
        return html.div(
            html.strong(title),
            html.span(detail),
            id=main.id,
            class_="hedron-sim-card",
            role="status",
        )

    def oob_idle():
        return OobHost(
            html.span("Idle", class_="hedron-sim-badge"),
            html.span(html.strong("#toast-host"), html.small("Stable OOB swap root")),
            id=host.id,
        )

    def oob_saved():
        return OobHost(
            html.span("Saved", class_="hedron-sim-badge hedron-sim-badge--ok"),
            html.span(html.strong("#toast-host"), html.small("Out-of-band update")),
            id=host.id,
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                primary(True),
                oob_idle(),
                html.button(
                    "Save settings",
                    type="button",
                    class_="hedron-sim-btn hedron-sim-btn--primary",
                    **_hx(hx_post="/settings", hx_target=main.selector, hx_swap="outerHTML"),
                ),
                html.p(
                    "Primary swap + out-of-band host update in one response.",
                    class_="hedron-sim-muted",
                ),
            ),
            title="OOB",
        )

    @app.action("/settings", regions=(main, host))
    def save():
        return InteractionResult(
            content=primary(False),
            region_id=main.id,
            oob=(OobUpdate(content=oob_saved(), element_id=host.id),),
            policy=InteractionPolicy(declared_regions=(main, host)),
            explanation="Update main and OOB host",
        )

    return embed_demo(app)


def build_allowlist_403_demo() -> str:
    app = SimApp(title="Allowlist 403", demo_id="allowlist-403")
    status = app.region("service-status", description="Status")

    def panel(ok: bool = False):
        if ok:
            return html.div(
                html.strong("Allowlisted swap"),
                html.span("HX-Target matched #service-status"),
                id=status.id,
                class_="hedron-sim-card",
                role="status",
            )
        return html.div(
            html.strong("Allowlist probe"),
            html.span("Region #service-status is declared on the route."),
            id=status.id,
            class_="hedron-sim-card",
            role="status",
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                panel(False),
                html.div(
                    html.button(
                        "Correct #service-status → 200",
                        type="button",
                        class_="hedron-sim-btn hedron-sim-btn--primary",
                        **_hx(
                            hx_get="/status",
                            hx_target=status.selector,
                            hx_swap="outerHTML",
                        ),
                    ),
                    html.button(
                        "Wrong #panel → 403",
                        type="button",
                        class_="hedron-sim-btn",
                        **_hx(hx_get="/status", hx_target="#panel", hx_swap="outerHTML"),
                    ),
                    class_="hedron-sim-row",
                    role="group",
                    aria={"label": "Allowlist"},
                ),
                html.p(
                    "Fail-closed: undeclared HX-Target never swaps.",
                    class_="hedron-sim-muted",
                ),
            ),
            title="403",
        )

    @app.fragment("/status", region=status)
    def refresh():
        return swap(panel(True))

    return embed_demo(app)


def build_charts_htmx_demo() -> str:
    app = SimApp(title="Charts HTMX", demo_id="charts-htmx")
    panel = app.region("chart-panel", description="Chart panel")

    def chart(rev: int):
        return html.div(
            html.figure(
                html.figcaption(
                    html.strong("Monthly revenue"),
                    html.span(f"Fragment refresh #{rev}"),
                ),
                html.div(
                    class_="hdc-chart-art",
                    role="img",
                    aria={"label": "Sample chart"},
                ),
                class_="hdc-chart",
            ),
            id=panel.id,
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                chart(1),
                RefreshButton.for_region(
                    panel, href="/charts/refresh", label="Refresh chart panel"
                ),
                html.p(
                    "Each click advances a short chart sequence (then wraps).",
                    class_="hedron-sim-muted",
                ),
            ),
            title="Charts",
        )

    @app.fragment(
        "/charts/refresh",
        region=panel,
        sequence=(lambda: swap(chart(2)), lambda: swap(chart(3)), lambda: swap(chart(4))),
    )
    def refresh():
        return swap(chart(2))

    return embed_demo(app)


def build_crud_demo() -> str:
    app = SimApp(title="CRUD notes", demo_id="crud-notes")
    listing = app.region("notes-list", description="Notes list")

    def list_panel(*items: str):
        rows = [
            html.li(
                html.span(text),
                html.button(
                    "Delete",
                    type="button",
                    class_="hedron-sim-btn",
                    **_hx(
                        hx_delete="/notes/1",
                        hx_target=listing.selector,
                        hx_swap="outerHTML",
                    ),
                ),
            )
            for text in items
        ]
        return html.div(
            html.ul(*rows, class_="hedron-sim-list") if rows else html.p("No notes yet."),
            id=listing.id,
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                # Start empty so add → delete → add stays coherent (no resurrected seed note).
                list_panel(),
                Form(
                    html.label(
                        "Note",
                        html.input(
                            id="crud-note",
                            name="note",
                            type="text",
                            placeholder="New note",
                            required=True,
                        ),
                    ),
                    SubmitButton("Add note"),
                    **_hx(
                        hx_post="/notes",
                        hx_target=listing.selector,
                        hx_swap="outerHTML",
                    ),
                ),
                html.p(
                    "Add a note, then delete it — the list region swaps in place "
                    "(simulated HTMX; no CSRF in the docs demo).",
                    class_="hedron-sim-muted",
                ),
            ),
            title="CRUD",
        )

    @app.action("/notes", region=listing)
    def add_note():
        return swap(list_panel(sim_form("note")))

    @app.fragment("/notes/1", region=listing, method="DELETE")
    def delete_note():
        return swap(list_panel())

    return embed_demo(app)


def build_mutations_htmx_demo() -> str:
    """HTMX fragment POST path from the mutations guide (PE-on story)."""
    app = SimApp(title="Mutations HTMX", demo_id="mutations-htmx")
    result = app.region("save-result", description="Save result")

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                Form(
                    html.label(
                        "Note",
                        html.input(
                            id="pe-note",
                            name="note",
                            type="text",
                            value="Ship the docs demo",
                        ),
                    ),
                    SubmitButton("Save"),
                    **_hx(
                        hx_post="/save",
                        hx_target=result.selector,
                        hx_swap="innerHTML",
                    ),
                ),
                html.div(
                    id=result.id,
                    class_="hedron-sim-card",
                    role="status",
                    aria={"live": "polite"},
                ),
                html.p(
                    "HTMX on — submit swaps the declared result region.",
                    class_="hedron-sim-muted",
                ),
            ),
            title="Mutations",
        )

    @app.action("/save", region=result)
    def save():
        return swap(
            html.div(
                html.strong("Saved in region"),
                html.span(sim_form("note")),
            )
        )

    return embed_demo(app)
