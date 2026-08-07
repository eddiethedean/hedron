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
    "build_auth_login_demo",
    "build_charts_htmx_demo",
    "build_cookbook_oob_demo",
    "build_crud_demo",
    "build_csrf_guard_demo",
    "build_data_table_filter_demo",
    "build_forms_invite_demo",
    "build_htmx_interactions_demo",
    "build_jobs_poll_demo",
    "build_live_poll_demo",
    "build_minimal_form_demo",
    "build_mutations_htmx_demo",
    "build_pe_paths_demo",
    "build_tenant_deny_demo",
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


def build_live_poll_demo(*, demo_id: str = "live-poll") -> str:
    app = SimApp(title="Job poll", demo_id=demo_id)
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

    hint = (
        "Same bounded poll used on Live interaction — each click advances one step."
        if demo_id == "jobs-poll"
        else "Each click advances one poll step (four steps, then wraps)."
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
                html.p(hint, class_="hedron-sim-muted"),
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
            html.span(
                html.strong("#toast-host"),
                html.small("Stable OOB swap root"),
                class_="hedron-sim-oob-label",
            ),
            id=host.id,
        )

    def oob_saved():
        return OobHost(
            html.span("Saved", class_="hedron-sim-badge hedron-sim-badge--ok"),
            html.span(
                html.strong("#toast-host"),
                html.small("Out-of-band update"),
                class_="hedron-sim-oob-label",
            ),
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

    def list_row(text: str):
        return html.li(
            html.span(text),
            html.button(
                "Delete",
                type="button",
                class_="hedron-sim-btn",
                **{
                    "data-hedron-sim-list-index": "__HEDRON_SIM_LIST_INDEX__",
                    **_hx(
                        hx_delete="/notes/item",
                        hx_target=listing.selector,
                        hx_swap="outerHTML",
                    ),
                },
            ),
        )

    def empty_list():
        return html.div(html.p("No notes yet."), id=listing.id)

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                empty_list(),
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
                    "Add several notes, then delete any row — the list region swaps in place "
                    "(simulated HTMX; no CSRF in the docs demo).",
                    class_="hedron-sim-muted",
                ),
            ),
            title="CRUD",
        )

    @app.action(
        "/notes",
        region=listing,
        accumulate="note",
        empty=lambda: swap(empty_list()),
    )
    def add_note():
        return swap(list_row(sim_form("note")))

    @app.fragment("/notes/item", region=listing, method="DELETE", list_remove=True)
    def delete_note():
        return swap(empty_list())

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


def build_jobs_poll_demo() -> str:
    """Same poll sequence as live interaction, for the Celery/RQ jobs guide."""
    return build_live_poll_demo(demo_id="jobs-poll")


def build_minimal_form_demo() -> str:
    app = SimApp(title="Minimal form", demo_id="minimal-form")
    stage = app.region("notes-stage", description="Notes page")

    def notes_page():
        return html.div(
            Stack(
                html.strong("Leave a note"),
                Form(
                    html.input(type="hidden", name="csrf_token", value="sim-csrf"),
                    html.label(
                        "Note",
                        html.input(
                            id="minimal-note",
                            name="note",
                            type="text",
                            value="Ship the docs demo",
                            required="required",
                        ),
                    ),
                    SubmitButton("Save"),
                    **_hx(
                        hx_post="/save",
                        hx_target=stage.selector,
                        hx_swap="outerHTML",
                    ),
                ),
                html.p(
                    "Classic POST — confirmation replaces the page region (docs sim).",
                    class_="hedron-sim-muted",
                ),
            ),
            id=stage.id,
        )

    def saved_page():
        return html.div(
            Stack(
                html.strong("Saved"),
                html.span(sim_form("note")),
                html.button(
                    "Leave another note",
                    type="button",
                    class_="hedron-sim-btn",
                    **_hx(
                        hx_get="/notes",
                        hx_target=stage.selector,
                        hx_swap="outerHTML",
                    ),
                ),
            ),
            id=stage.id,
            class_="hedron-sim-card",
            role="status",
        )

    @app.page("/")
    def home() -> Page:
        return Page(notes_page(), title="Notes")

    @app.action("/save", region=stage)
    def save():
        return swap(saved_page())

    @app.fragment("/notes", region=stage)
    def notes():
        return swap(notes_page())

    return embed_demo(app)


def build_auth_login_demo() -> str:
    app = SimApp(title="Sign in", demo_id="auth-login")
    panel = app.region("auth-panel", description="Auth panel")

    def login_form(*, errors: tuple[str, ...] = ()):
        children: list = []
        if errors:
            children.append(FormErrors(errors))
        children.extend(
            [
                html.label(
                    "Username",
                    html.input(
                        id="auth-username",
                        name="username",
                        type="text",
                        value="ada",
                        autocomplete="username",
                    ),
                ),
                html.label(
                    "Password",
                    html.input(
                        id="auth-password",
                        name="password",
                        type="password",
                        value="",
                        autocomplete="current-password",
                    ),
                ),
                SubmitButton("Sign in"),
            ]
        )
        return html.div(
            Form(
                *children,
                novalidate="novalidate",
                **_hx(
                    hx_post="/login",
                    hx_target=panel.selector,
                    hx_swap="outerHTML",
                ),
            ),
            html.button(
                "Open /home anonymously",
                type="button",
                class_="hedron-sim-btn",
                **_hx(
                    hx_get="/home",
                    hx_target=panel.selector,
                    hx_swap="outerHTML",
                ),
            ),
            html.p(
                "Demo credentials: ada / correct-horse (local learning only).",
                class_="hedron-sim-muted",
            ),
            id=panel.id,
        )

    def signed_in():
        return html.div(
            html.strong("Signed in as ada"),
            html.span("Session gate passed — home content is visible."),
            html.button(
                "Sign out",
                type="button",
                class_="hedron-sim-btn",
                **_hx(
                    hx_get="/login-form",
                    hx_target=panel.selector,
                    hx_swap="outerHTML",
                ),
            ),
            id=panel.id,
            class_="hedron-sim-card",
            role="status",
        )

    def denied():
        return html.div(
            html.strong("401 Sign in required"),
            html.span("Gated /home refused the anonymous request."),
            html.button(
                "Back to login",
                type="button",
                class_="hedron-sim-btn",
                **_hx(
                    hx_get="/login-form",
                    hx_target=panel.selector,
                    hx_swap="outerHTML",
                ),
            ),
            id=panel.id,
            class_="hedron-sim-card",
            role="status",
        )

    @app.page("/")
    def home() -> Page:
        return Page(login_form(), title="Login")

    def invalid():
        return InteractionResult(
            content=login_form(errors=("Invalid username or password.",)),
            status_code=401,
            region_id=panel.id,
        )

    def valid():
        return InteractionResult(
            content=signed_in(),
            status_code=200,
            region_id=panel.id,
        )

    @app.action(
        "/login",
        region=panel,
        validate="credentials",
        variants={"invalid": invalid, "valid": valid},
    )
    def login_default():
        return invalid()

    @app.fragment("/home", region=panel)
    def gated_home():
        return InteractionResult(
            content=denied(),
            status_code=401,
            region_id=panel.id,
        )

    @app.fragment("/login-form", region=panel)
    def reset_login():
        return swap(login_form())

    return embed_demo(app)


def build_csrf_guard_demo() -> str:
    app = SimApp(title="CSRF guard", demo_id="csrf-guard")
    result = app.region("csrf-result", description="CSRF result")

    def result_idle():
        return html.div(
            html.strong("Awaiting POST"),
            html.span("Unsafe methods need a matching csrf_token."),
            id=result.id,
            class_="hedron-sim-card",
            role="status",
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                result_idle(),
                html.div(
                    html.button(
                        "POST with CSRF",
                        type="button",
                        class_="hedron-sim-btn hedron-sim-btn--primary",
                        **_hx(
                            hx_post="/do",
                            hx_target=result.selector,
                            hx_swap="outerHTML",
                        ),
                    ),
                    html.button(
                        "POST without CSRF",
                        type="button",
                        class_="hedron-sim-btn",
                        **_hx(
                            hx_post="/do-missing",
                            hx_target=result.selector,
                            hx_swap="outerHTML",
                        ),
                    ),
                    class_="hedron-sim-row",
                    role="group",
                    aria={"label": "CSRF"},
                ),
                html.p(
                    "Simulated fail-closed CSRF — missing token → 403, no success copy.",
                    class_="hedron-sim-muted",
                ),
            ),
            title="CSRF",
        )

    @app.action("/do", region=result)
    def with_token():
        return swap(
            html.div(
                html.strong("POST ok"),
                html.span("csrf_token matched the cookie."),
                id=result.id,
                class_="hedron-sim-card",
                role="status",
            )
        )

    @app.action("/do-missing", region=result)
    def missing_token():
        return InteractionResult(
            content=html.div(
                html.strong("403 CSRF failed"),
                html.span("Missing or mismatched csrf_token — action rejected."),
                id=result.id,
                class_="hedron-sim-card",
                role="status",
            ),
            status_code=403,
            region_id=result.id,
        )

    return embed_demo(app)


def build_data_table_filter_demo() -> str:
    app = SimApp(title="Data table filter", demo_id="data-table-filter")
    table = app.region("people-table", description="People table")

    rows = (
        ("1", "Ada", "admin"),
        ("2", "Grace", "member"),
        ("3", "Katherine", "admin"),
        ("4", "Margaret", "member"),
    )

    def table_panel(filter_role: str | None = None):
        filtered = [r for r in rows if filter_role is None or r[2] == filter_role]
        label = "All people" if filter_role is None else f"Role: {filter_role}"
        body_rows = [
            html.tr(html.td(rid), html.td(name), html.td(role))
            for rid, name, role in filtered
        ]
        return html.div(
            html.strong(label),
            html.table(
                html.thead(html.tr(html.th("ID"), html.th("Name"), html.th("Role"))),
                html.tbody(*body_rows),
            ),
            id=table.id,
            class_="hedron-sim-card",
            role="region",
            aria={"live": "polite"},
        )

    def filter_btn(label: str, path: str, *, primary: bool = False):
        classes = "hedron-sim-btn hedron-sim-btn--primary" if primary else "hedron-sim-btn"
        return html.button(
            label,
            type="button",
            class_=classes,
            **_hx(hx_get=path, hx_target=table.selector, hx_swap="outerHTML"),
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                table_panel(),
                html.div(
                    filter_btn("All", "/rows", primary=True),
                    filter_btn("Admins", "/rows/admin"),
                    filter_btn("Members", "/rows/member"),
                    class_="hedron-sim-row",
                    role="group",
                    aria={"label": "Filter"},
                ),
                html.p(
                    "Filter swaps the declared table region — same pattern as DataTable HTMX.",
                    class_="hedron-sim-muted",
                ),
            ),
            title="People",
        )

    @app.fragment("/rows", region=table)
    def all_rows():
        return swap(table_panel())

    @app.fragment("/rows/admin", region=table)
    def admin_rows():
        return swap(table_panel("admin"))

    @app.fragment("/rows/member", region=table)
    def member_rows():
        return swap(table_panel("member"))

    return embed_demo(app)


def build_pe_paths_demo() -> str:
    app = SimApp(title="Progressive enhancement", demo_id="pe-paths")
    stage = app.region("pe-stage", description="PE stage")
    result = app.region("pe-result", description="HTMX result")

    def form_body():
        return Stack(
            html.strong("Invite note"),
            html.div(
                id=result.id,
                class_="hedron-sim-card",
                role="status",
                aria={"live": "polite"},
            ),
            Form(
                html.input(type="hidden", name="csrf_token", value="sim-csrf"),
                html.label(
                    "Note (HTMX path)",
                    html.input(
                        id="pe-note-htmx",
                        name="note",
                        type="text",
                        value="Ship PE-019",
                    ),
                ),
                SubmitButton("Submit with HTMX"),
                **_hx(
                    hx_post="/save-htmx",
                    hx_target=result.selector,
                    hx_swap="outerHTML",
                ),
            ),
            Form(
                html.input(type="hidden", name="csrf_token", value="sim-csrf"),
                html.label(
                    "Note (full-page path)",
                    html.input(
                        id="pe-note-page",
                        name="note",
                        type="text",
                        value="Ship PE-019",
                    ),
                ),
                SubmitButton("Submit full page (no HTMX path)"),
                **_hx(
                    hx_post="/save-page",
                    hx_target=stage.selector,
                    hx_swap="outerHTML",
                ),
            ),
            html.p(
                "HTMX path swaps #pe-result. Full-page path replaces the whole stage.",
                class_="hedron-sim-muted",
            ),
        )

    def stage_panel():
        return html.div(form_body(), id=stage.id)

    def page_confirmation():
        return html.div(
            Stack(
                html.strong("Full-page confirmation"),
                html.span(sim_form("note")),
                html.span("No HX-Request branch — Page / RedirectResponse path."),
                html.button(
                    "Start over",
                    type="button",
                    class_="hedron-sim-btn",
                    **_hx(
                        hx_get="/reset",
                        hx_target=stage.selector,
                        hx_swap="outerHTML",
                    ),
                ),
            ),
            id=stage.id,
            class_="hedron-sim-card",
            role="status",
        )

    @app.page("/")
    def home() -> Page:
        return Page(stage_panel(), title="PE")

    @app.action("/save-htmx", region=result)
    def save_htmx():
        return swap(
            html.div(
                html.strong("Fragment path"),
                html.span(sim_form("note")),
                id=result.id,
                class_="hedron-sim-card",
                role="status",
            )
        )

    @app.action("/save-page", region=stage)
    def save_page():
        return swap(page_confirmation())

    @app.fragment("/reset", region=stage)
    def reset():
        return swap(stage_panel())

    return embed_demo(app)


def build_tenant_deny_demo() -> str:
    app = SimApp(title="Tenant isolation", demo_id="tenant-deny")
    status = app.region("job-status", description="Job status")

    def idle():
        return html.div(
            html.strong("Job status"),
            html.span("Authorize before every poll — wrong tenant → not found."),
            id=status.id,
            class_="hedron-sim-card",
            role="status",
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                idle(),
                html.div(
                    html.button(
                        "Poll (same tenant)",
                        type="button",
                        class_="hedron-sim-btn hedron-sim-btn--primary",
                        **_hx(
                            hx_get="/jobs/42",
                            hx_target=status.selector,
                            hx_swap="outerHTML",
                        ),
                    ),
                    html.button(
                        "Poll (other tenant)",
                        type="button",
                        class_="hedron-sim-btn",
                        **_hx(
                            hx_get="/jobs/99",
                            hx_target=status.selector,
                            hx_swap="outerHTML",
                        ),
                    ),
                    class_="hedron-sim-row",
                    role="group",
                    aria={"label": "Tenant"},
                ),
                html.p(
                    "Cross-tenant job IDs must not leak status HTML.",
                    class_="hedron-sim-muted",
                ),
            ),
            title="Tenant",
        )

    @app.fragment("/jobs/42", region=status)
    def same_tenant():
        return swap(
            html.div(
                html.strong("Running"),
                html.span("tenant A · job 42 authorized"),
                id=status.id,
                class_="hedron-sim-card",
                role="status",
            )
        )

    @app.fragment("/jobs/99", region=status)
    def other_tenant():
        return InteractionResult(
            content=html.div(
                html.strong("404 Not found"),
                html.span("Job 99 is outside this tenant — refuse without leaking."),
                id=status.id,
                class_="hedron-sim-card",
                role="status",
            ),
            status_code=404,
            region_id=status.id,
        )

    return embed_demo(app)
