"""Component-page demos authored with Hedron components + hedron-sim."""

from __future__ import annotations

from collections.abc import Callable

from hedron import (
    AppShell,
    AttrHost,
    ComponentRef,
    ErrorState,
    Form,
    FormErrors,
    Fragment,
    HtmxLink,
    InfiniteScroll,
    InteractionResult,
    Lazy,
    Loading,
    MainPanel,
    Nav,
    NavLink,
    OobHost,
    OobUpdate,
    Page,
    Pagination,
    Poll,
    RefreshButton,
    Skeleton,
    Stack,
    SubmitButton,
    Toast,
    html,
    swap,
)
from hedron_core.interaction import InteractionPolicy
from hedron_sim import SimApp, embed_demo, sim_form, sim_local_time

__all__ = [
    "COMPONENT_DEMO_BUILDERS",
    "build_component_demo",
]


def _hx(**attrs: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in attrs.items():
        if key.startswith("hx_"):
            out["hx-" + key[3:].replace("_", "-")] = value
        else:
            out[key.replace("_", "-")] = value
    return out


def _ref(path: str, *, target: str, swap: str = "innerHTML", method: str = "GET") -> ComponentRef:
    return ComponentRef(
        logical_id=path.strip("/").replace("/", "-") or "root",
        path=path,
        method=method,
        target=target,
        swap=swap,
    )


def build_refresh_button() -> str:
    app = SimApp(demo_id="component-refresh")
    status = app.region("status-card")

    def panel():
        return html.div(
            html.strong("Service healthy"),
            html.span(f"Checked at {sim_local_time()}"),
            id=status.id,
            class_="hedron-sim-card",
            role="status",
            aria={"live": "polite"},
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                panel(),
                RefreshButton.for_region(status, href="/status", label="Refresh status"),
            ),
            title="RefreshButton",
        )

    @app.fragment("/status", region=status)
    def refresh():
        return swap(panel())

    return embed_demo(app)


def build_lazy() -> str:
    app = SimApp(demo_id="component-lazy")
    box = app.region("lazy-box")
    ref = _ref("/activity-feed", target=box.selector, swap="innerHTML")

    @app.page("/")
    def home() -> Page:
        return Page(
            Lazy(
                ref=ref,
                placeholder=Loading("Loading account activity…"),
                target_id=box.id,
            ),
            title="Lazy",
        )

    @app.fragment("/activity-feed", region=box)
    def feed():
        return swap(
            html.div(
                html.strong("3 recent events"),
                html.span("Deployment, approval, and release notes loaded."),
                class_="hedron-sim-card",
            )
        )

    return embed_demo(app)


def build_poll() -> str:
    app = SimApp(demo_id="component-poll")
    box = app.region("poll-box")
    ref = _ref("/jobs/42", target=box.selector, swap="innerHTML")

    def panel(state: str, detail: str):
        return html.div(
            html.strong(state),
            html.span(detail),
            class_="hedron-sim-card",
            role="status",
        )

    steps = (
        lambda: swap(panel("Queued", "Waiting for a worker")),
        lambda: swap(panel("Running", "Step 1 of 2")),
        lambda: swap(panel("Running", "Step 2 of 2")),
        lambda: swap(panel("Complete", "84 records imported; polling stopped")),
    )

    @app.page("/")
    def home() -> Page:
        return Page(
            Poll(
                ref=ref,
                interval_ms=700,
                target_id=box.id,
                content=panel("Queued", "Waiting for a worker"),
            ),
            title="Poll",
        )

    @app.fragment("/jobs/42", region=box, sequence=steps)
    def tick():
        return steps[0]()

    return embed_demo(app)


def build_infinite() -> str:
    app = SimApp(demo_id="component-infinite")
    feed = app.region("event-feed")
    ref = _ref("/events", target=feed.selector, swap="beforeend")

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                html.ol(
                    html.li("Deployment completed"),
                    html.li("Review approved"),
                    id=feed.id,
                    class_="hedron-sim-list",
                ),
                InfiniteScroll(ref=ref, target=feed.selector, swap="beforeend"),
            ),
            title="InfiniteScroll",
        )

    @app.fragment("/events", region=feed)
    def more():
        return swap(
            Fragment(
                html.li("Tests passed"),
                html.li("Release published"),
            )
        )

    return embed_demo(app)


def build_pagination() -> str:
    app = SimApp(demo_id="component-pagination")
    results = app.region("page-results")

    pages = {
        1: ("Results 1–3", "Alpha · Bravo · Charlie"),
        2: ("Results 4–6", "Delta · Echo · Foxtrot"),
        3: ("Results 7–9", "Golf · Hotel · India"),
    }

    def panel(page: int, *, with_id: bool = False):
        title, detail = pages[page]
        attrs: dict[str, str] = {"class_": "hedron-sim-card"}
        if with_id:
            attrs["id"] = results.id
        return html.div(html.strong(title), html.span(detail), **attrs)

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                panel(1, with_id=True),
                Pagination(
                    page=1,
                    page_size=3,
                    total=9,
                    base_path="/results",
                    target=results.selector,
                ),
            ),
            title="Pagination",
        )

    for number in (1, 2, 3):
        path = f"/results?page={number}"

        def make(n: int = number, route_path: str = path) -> None:
            @app.fragment(route_path, region=results)
            def page_frag():
                return swap(panel(n))

        make()

    return embed_demo(app)


def build_error() -> str:
    app = SimApp(demo_id="component-error")
    box = app.region("error-box")

    @app.page("/")
    def home() -> Page:
        return Page(
            html.div(
                ErrorState(
                    "Activity could not be loaded.",
                    retry_href="/activity",
                    retry_label="Retry",
                    target=box.selector,
                ),
                id=box.id,
            ),
            title="ErrorState",
        )

    @app.fragment("/activity", region=box)
    def retry():
        return swap(
            html.div(
                html.strong("Activity restored"),
                html.span("The retry returned a successful fragment."),
                id=box.id,
                class_="hedron-sim-card",
                role="status",
            )
        )

    return embed_demo(app)


def build_form() -> str:
    app = SimApp(demo_id="component-form")
    region = app.region("demo-form")

    def form_body(*, errors: tuple[str, ...] = ()):
        kids: list[object] = []
        if errors:
            kids.append(FormErrors(errors))
        kids.extend(
            [
                html.label(
                    "Email address",
                    html.input(
                        name="email",
                        type="email",
                        placeholder="ada@example.com",
                        required="required",
                    ),
                ),
                SubmitButton("Submit"),
            ]
        )
        hx = _hx(hx_post="/demo", hx_target=region.selector, hx_swap="outerHTML")
        return html.div(
            Form(*kids, novalidate="novalidate", **hx),  # type: ignore[arg-type]
            id=region.id,
        )

    @app.page("/")
    def home() -> Page:
        return Page(form_body(), title="Form")

    def invalid():
        return InteractionResult(
            content=form_body(errors=("Enter a valid work email.",)),
            status_code=422,
        )

    def valid():
        return InteractionResult(
            content=html.div(
                html.strong("Submitted"),
                html.span(f"Queued for {sim_form('email')}."),
                id=region.id,
                class_="hedron-sim-card",
                role="status",
            ),
            status_code=200,
        )

    @app.action(
        "/demo",
        region=region,
        validate="email",
        variants={"invalid": invalid, "valid": valid},
    )
    def submit():
        return invalid()

    return embed_demo(app)


def build_shell_family(*, demo_id: str, title: str) -> str:
    app = SimApp(demo_id=demo_id)
    panel = app.region("comp-main-panel")

    def panel_body(name: str, detail: str):
        return html.div(
            html.strong(name),
            html.span(detail),
            class_="hedron-sim-card",
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            AppShell(
                nav=Nav(
                    NavLink(
                        "Home",
                        "/home",
                        target=panel.selector,
                        swap="innerHTML",
                        active=True,
                    ),
                    NavLink(
                        "Reports",
                        "/reports",
                        target=panel.selector,
                        swap="innerHTML",
                    ),
                    NavLink(
                        "Settings",
                        "/settings",
                        target=panel.selector,
                        swap="innerHTML",
                    ),
                ),
                body=panel_body("Home", "Overview metrics stay in MainPanel."),
                panel_id=panel.id,
            ),
            title=title,
        )

    @app.fragment("/home", region=panel)
    def home_frag():
        return swap(panel_body("Home", "Overview metrics stay in MainPanel."))

    @app.fragment("/reports", region=panel)
    def reports_frag():
        return swap(panel_body("Reports", "Reports fragment swapped into #comp-main-panel."))

    @app.fragment("/settings", region=panel)
    def settings_frag():
        return swap(panel_body("Settings", "Settings fragment; side nav stays put."))

    return embed_demo(app)


def build_htmx_link() -> str:
    app = SimApp(demo_id="component-htmx-link")
    panel = app.region("htmx-link-panel")

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                html.div(
                    HtmxLink(
                        "Reports",
                        "/reports",
                        target=panel.selector,
                        swap="innerHTML",
                        class_="hedron-sim-btn",
                    ),
                    HtmxLink(
                        "Team",
                        "/team",
                        target=panel.selector,
                        swap="innerHTML",
                        class_="hedron-sim-btn",
                    ),
                    class_="hedron-sim-row",
                ),
                MainPanel(
                    html.strong("Choose a link"),
                    html.span("HtmxLink keeps href as the progressive-enhancement path."),
                    id=panel.id,
                ),
            ),
            title="HtmxLink",
        )

    @app.fragment("/reports", region=panel)
    def reports():
        return swap(
            Fragment(
                html.strong("Reports"),
                html.span("In-shell navigation with SafeUrl href fallback."),
            )
        )

    @app.fragment("/team", region=panel)
    def team():
        return swap(
            Fragment(
                html.strong("Team"),
                html.span("Ordinary href still works without JavaScript."),
            )
        )

    return embed_demo(app)


def build_oob_host() -> str:
    app = SimApp(demo_id="component-oob-host")
    main = app.region("oob-primary")
    host = app.region("demo-oob-host")

    def primary(*, draft: bool = True):
        return html.div(
            html.strong("Draft profile" if draft else "Profile saved"),
            html.span("Primary region waiting for save." if draft else "Primary region updated."),
            id=main.id,
            class_="hedron-sim-card",
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                primary(draft=True),
                OobHost(
                    html.span("OOB host", class_="hedron-sim-badge"),
                    html.span(html.strong("#status"), html.small("Stable swap root")),
                    id=host.id,
                ),
                html.button(
                    "Save",
                    type="button",
                    class_="hedron-sim-btn hedron-sim-btn--primary",
                    **_hx(hx_post="/profile", hx_target=main.selector, hx_swap="outerHTML"),
                ),
            ),
            title="OobHost",
        )

    @app.action("/profile", regions=(main, host))
    def save():
        return InteractionResult(
            content=primary(draft=False),
            oob=(
                OobUpdate(
                    content=OobHost(
                        html.span("Saved", class_="hedron-sim-badge hedron-sim-badge--ok"),
                        html.span(html.strong("#status"), html.small("Out-of-band update")),
                        id=host.id,
                    ),
                    element_id=host.id,
                ),
            ),
            policy=InteractionPolicy(declared_regions=(main, host)),
        )

    return embed_demo(app)


def build_attr_host() -> str:
    app = SimApp(demo_id="component-attr-host")
    host = app.region("demo-attr-host")

    def host_node(state: str):
        return AttrHost(
            html.strong("Attr host"),
            html.small(f"data-state={state}"),
            id=host.id,
            attrs={"data-state": state},
            class_="hedron-sim-card",
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                host_node("idle"),
                html.button(
                    "Run attribute OOB",
                    type="button",
                    class_="hedron-sim-btn hedron-sim-btn--primary",
                    **_hx(
                        hx_get="/status-attrs",
                        hx_target=host.selector,
                        hx_swap="outerHTML",
                    ),
                ),
            ),
            title="AttrHost",
        )

    @app.fragment(
        "/status-attrs",
        region=host,
        sequence=(
            lambda: swap(host_node("busy")),
            lambda: swap(host_node("ready")),
            lambda: swap(host_node("idle")),
        ),
    )
    def attrs():
        return swap(host_node("busy"))

    return embed_demo(app)


def build_loading() -> str:
    app = SimApp(demo_id="component-loading")
    box = app.region("loading-target")

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                html.div(Loading("Loading account activity…"), id=box.id),
                html.button(
                    "Load activity",
                    type="button",
                    class_="hedron-sim-btn hedron-sim-btn--primary",
                    **_hx(hx_get="/activity", hx_target=box.selector, hx_swap="innerHTML"),
                ),
            ),
            title="Loading",
        )

    @app.fragment("/activity", region=box)
    def load():
        return swap(
            html.div(
                html.strong("3 events"),
                html.span("Deployment, approval, and release notes."),
                class_="hedron-sim-card",
                role="status",
            )
        )

    return embed_demo(app)


def build_form_errors() -> str:
    app = SimApp(demo_id="component-form-errors")
    region = app.region("errors-demo")
    slot = app.region("errors-slot")

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                html.div(
                    html.p("Submit with missing fields to redisplay FormErrors in the region."),
                    html.div(id=slot.id),
                    html.button(
                        "Submit empty form",
                        type="button",
                        class_="hedron-sim-btn hedron-sim-btn--primary",
                        **_hx(
                            hx_post="/invite",
                            hx_target=slot.selector,
                            hx_swap="innerHTML",
                        ),
                    ),
                    id=region.id,
                    class_="hedron-sim-card",
                ),
            ),
            title="FormErrors",
        )

    @app.action("/invite", regions=(region, slot))
    def fail():
        return InteractionResult(
            content=FormErrors(["Email is required.", "Choose a billing plan."]),
            status_code=422,
        )

    return embed_demo(app)


def build_fragment() -> str:
    app = SimApp(demo_id="component-fragment")
    target = app.region("fragment-demo-target")

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                html.div(
                    html.span("Draft", class_="hedron-sim-badge"),
                    html.span(
                        html.strong("Profile"),
                        html.small("Click refresh to inject sibling nodes."),
                    ),
                    id=target.id,
                    class_="hedron-sim-card",
                ),
                RefreshButton.for_region(
                    target,
                    href="/profile-fragment",
                    label="Refresh fragment",
                    swap="innerHTML",
                ),
            ),
            title="Fragment",
        )

    @app.fragment("/profile-fragment", region=target)
    def refresh():
        return swap(
            Fragment(
                html.span("Saved", class_="hedron-sim-badge hedron-sim-badge--ok"),
                html.span(
                    html.strong("Profile updated"),
                    html.small("Two siblings; no Fragment wrapper."),
                ),
            )
        )

    return embed_demo(app)


def build_skeleton() -> str:
    app = SimApp(demo_id="component-skeleton")
    box = app.region("skeleton-target")

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                html.div(Skeleton(lines=3), id=box.id),
                html.button(
                    "Load profile",
                    type="button",
                    class_="hedron-sim-btn hedron-sim-btn--primary",
                    **_hx(hx_get="/profile", hx_target=box.selector, hx_swap="innerHTML"),
                ),
            ),
            title="Skeleton",
        )

    @app.fragment("/profile", region=box)
    def load():
        return swap(
            html.div(
                html.strong("Ada Lovelace"),
                html.span("Platform · Active"),
                class_="hedron-sim-card",
            )
        )

    return embed_demo(app)


def build_toast() -> str:
    app = SimApp(demo_id="component-toast")
    host = app.region("toast-host")

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                html.button(
                    "Copy API key",
                    type="button",
                    class_="hedron-sim-btn hedron-sim-btn--primary",
                    **_hx(hx_post="/copy-key", hx_target=host.selector, hx_swap="innerHTML"),
                ),
                OobHost(id=host.id),
            ),
            title="Toast",
        )

    @app.action("/copy-key", region=host)
    def copy():
        return swap(Toast("API key copied.", tone="success"))

    return embed_demo(app)


def build_confirm_button() -> str:
    app = SimApp(demo_id="component-confirm")
    row = app.region("confirm-row")

    @app.page("/")
    def home() -> Page:
        return Page(
            html.div(
                html.div(
                    html.strong("Draft report"),
                    html.span("Row present until you confirm delete."),
                    class_="hedron-sim-card",
                ),
                html.button(
                    "Delete item",
                    type="button",
                    class_="hedron-button hedron-button-danger hedron-confirm-button",
                    **_hx(
                        hx_confirm="Delete item?",
                        hx_delete="/items/1",
                        hx_target=row.selector,
                        hx_swap="innerHTML",
                    ),
                ),
                id=row.id,
            ),
            title="ConfirmButton",
        )

    @app.fragment("/items/1", region=row, method="DELETE")
    def delete():
        return swap(
            html.div(
                html.strong("Item deleted"),
                html.span("Row removed after confirm."),
                class_="hedron-sim-card",
                role="status",
            )
        )

    return embed_demo(app)


COMPONENT_DEMO_BUILDERS: dict[str, Callable[[], str]] = {
    "component-refresh": build_refresh_button,
    "component-lazy": build_lazy,
    "component-poll": build_poll,
    "component-infinite": build_infinite,
    "component-pagination": build_pagination,
    "component-error": build_error,
    "component-form": build_form,
    "component-auto-form": build_form,
    "component-app-shell": lambda: build_shell_family(
        demo_id="component-app-shell", title="AppShell"
    ),
    "component-main-panel": lambda: build_shell_family(
        demo_id="component-main-panel", title="MainPanel"
    ),
    "component-nav-link": lambda: build_shell_family(demo_id="component-nav-link", title="NavLink"),
    "component-htmx-link": build_htmx_link,
    "component-oob-host": build_oob_host,
    "component-attr-host": build_attr_host,
    "component-loading": build_loading,
    "component-form-errors": build_form_errors,
    "component-fragment": build_fragment,
    "component-skeleton": build_skeleton,
    "component-toast": build_toast,
    "component-confirm": build_confirm_button,
}


def build_component_demo(name: str) -> str:
    return COMPONENT_DEMO_BUILDERS[name]()
