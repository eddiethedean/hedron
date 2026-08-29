"""Offline Edron Showcase simulation.

This is a documentation-only adapter. The runnable application is
``examples/edron-showcase/app.py`` and imports only ``edron``; this adapter
declares the same browser-visible contracts for static docs.
"""

from __future__ import annotations

from collections.abc import Iterable

from hedron import Page, SafeUrl, UrlPurpose, html, swap
from hedron_sim import SimApp, embed_demo, sim_local_time, wrap_browser_chrome

__all__ = ["build_edron_showcase_demo"]


def _hx(**attrs: str) -> dict[str, str]:
    return {
        ("hx-" + key[3:].replace("_", "-")) if key.startswith("hx_") else key: value
        for key, value in attrs.items()
    }


def _metric(label: str, value: str, delta: str):
    return html.dl(
        html.dt(label),
        html.dd(
            html.strong(value, data={"metric-value": "true"}),
            html.small(delta, class_="showcase-delta showcase-delta--up"),
        ),
        class_="hedron-metric showcase-metric",
    )


def _step(label: str, detail: str, state: str):
    return html.li(
        html.span(class_=f"showcase-step-dot showcase-step-dot--{state}", aria={"hidden": "true"}),
        html.div(html.strong(label), html.small(detail)),
        class_=f"showcase-step showcase-step--{state}",
    )


def _pipeline_card(region, *, refreshed: bool = False):
    return html.section(
        html.div(
            html.div(
                html.span("Workflow", class_="hedron-app-kicker"),
                html.h3("Data release pipeline"),
                html.p("Imperative page methods, lowered into a visible workflow."),
            ),
            html.span("Live" if refreshed else "Running", class_="hedron-status"),
            class_="showcase-card-heading",
        ),
        html.ol(
            _step("Compose", "Page output assembled", "complete"),
            _step("Validate", "Boundaries checked", "complete"),
            _step("Transform", "18 of 24 partitions applied", "current"),
            _step("Publish", "Awaiting owner approval", "pending"),
            class_="showcase-steps",
            aria={"label": "Data release pipeline"},
        ),
        html.div(
            html.span(
                "Updated just now · " + sim_local_time() if refreshed else "Transform in progress"
            ),
            html.button(
                "Refresh pipeline",
                type="button",
                class_="hedron-ui-button hedron-ui-button--primary",
                **_hx(
                    hx_post="/pipeline/refresh",
                    hx_target=region.selector,
                    hx_swap="outerHTML",
                ),
            ),
            class_="showcase-card-footer",
        ),
        id=region.id,
        class_="hedron-card hedron-app-panel showcase-card",
    )


def _approval_card(region, *, approved: bool = False):
    action = (
        html.div(
            html.span("The release candidate passed 42 automated checks."),
            html.button(
                "Approve release",
                type="button",
                class_="hedron-ui-button hedron-ui-button--primary",
                **_hx(
                    hx_post="/approve",
                    hx_target=region.selector,
                    hx_swap="outerHTML",
                ),
            ),
            class_="showcase-approval-action",
        )
        if not approved
        else html.div(
            html.span("Publish queued for the worker pool."),
            html.span("Approved", class_="hedron-status showcase-status-success"),
            class_="showcase-approval-action",
        )
    )
    return html.section(
        html.div(
            html.div(
                html.span("Action boundary", class_="hedron-app-kicker"),
                html.h3("v1.0.5-rc1"),
                html.p("An explicit Edron action owns the unsafe state transition."),
            ),
            html.span("Approved" if approved else "Needs review", class_="hedron-role"),
            class_="showcase-card-heading",
        ),
        html.div(
            html.div(
                html.strong("64%"),
                html.span("release checklist complete"),
                class_="showcase-progress-label",
            ),
            html.progress(value="64", max="100", aria={"label": "Release checklist progress"}),
            class_="showcase-progress",
        ),
        action,
        id=region.id,
        class_="hedron-card hedron-app-panel showcase-card",
    )


def _run_rows(filter_name: str) -> Iterable[object]:
    rows = (
        ("nightly-warehouse", "Running", "18m", "1,284,012", "info"),
        ("crm-backfill", "Succeeded", "42m", "96,410", "success"),
        ("events-replay", "Failed", "4m", "0", "danger"),
        ("lookup-refresh", "Queued", "—", "—", "neutral"),
    )
    for name, status, duration, count, tone in rows:
        if filter_name == "attention" and tone != "danger":
            continue
        yield html.tr(
            html.td(name),
            html.td(html.span(status, class_=f"hedron-role showcase-role--{tone}")),
            html.td(duration),
            html.td(count),
        )


def _runs_card(region, filter_name: str = "all"):
    selected = "Needs attention" if filter_name == "attention" else "All runs"
    return html.section(
        html.div(
            html.div(
                html.span("Data methods", class_="hedron-app-kicker"),
                html.h3("Recent runs"),
                html.p(selected + " · bounded result set"),
            ),
            html.div(
                html.button(
                    "All",
                    type="button",
                    class_=(
                        "showcase-filter showcase-filter--active"
                        if filter_name == "all"
                        else "showcase-filter"
                    ),
                    **_hx(hx_get="/runs/all", hx_target=region.selector, hx_swap="outerHTML"),
                ),
                html.button(
                    "Needs attention",
                    type="button",
                    class_=(
                        "showcase-filter showcase-filter--active"
                        if filter_name == "attention"
                        else "showcase-filter"
                    ),
                    **_hx(
                        hx_get="/runs/attention",
                        hx_target=region.selector,
                        hx_swap="outerHTML",
                    ),
                ),
                class_="showcase-filters",
            ),
            class_="showcase-card-heading showcase-card-heading--stacked",
        ),
        html.div(
            html.table(
                html.thead(
                    html.tr(
                        html.th("Run"),
                        html.th("Status"),
                        html.th("Duration"),
                        html.th("Rows"),
                    )
                ),
                html.tbody(*_run_rows(filter_name)),
            ),
            class_="hedron-demo-table-wrap",
        ),
        id=region.id,
        class_="hedron-card hedron-app-panel showcase-card",
    )


def _activity_card():
    return html.section(
        html.div(
            html.span("Page lifecycle", class_="hedron-app-kicker"),
            html.h3("Recent activity"),
            html.p("Request-local output, visible by default."),
            class_="showcase-card-heading showcase-card-heading--single",
        ),
        html.ol(
            html.li(
                html.time("09:42"),
                html.div(
                    html.strong("Release candidate built"),
                    html.span("v1.0.4 · 42 checks passed"),
                ),
            ),
            html.li(
                html.time("09:18"),
                html.div(html.strong("Workspace upgraded"), html.span("Northstar moved to Scale")),
            ),
            html.li(
                html.time("08:55"),
                html.div(
                    html.strong("Risk signal resolved"),
                    html.span("Latency returned to baseline"),
                ),
            ),
            class_="showcase-activity",
        ),
        class_="hedron-card hedron-app-panel showcase-card",
    )


def _inventory(region):
    return html.section(
        html.div(
            html.div(
                html.span("Edron vocabulary", class_="hedron-app-kicker"),
                html.h3("What you just saw"),
                html.p("The product surface comes from Page methods and declared descriptors."),
            ),
            html.button(
                "Inspect surface map",
                type="button",
                class_="hedron-ui-button",
                **_hx(hx_get="/components/map", hx_target=region.selector, hx_swap="outerHTML"),
            ),
            class_="showcase-card-heading",
        ),
        html.div(
            html.span("App", class_="showcase-chip"),
            html.span("Page", class_="showcase-chip"),
            html.span("Columns", class_="showcase-chip"),
            html.span("Fragment", class_="showcase-chip"),
            html.span("Action", class_="showcase-chip showcase-chip--accent"),
            html.span("Outcome", class_="showcase-chip"),
            class_="showcase-chip-list",
        ),
        id=region.id,
        class_="hedron-card hedron-app-panel showcase-card",
    )


def build_edron_showcase_demo() -> str:
    """Return the full-feature Edron Showcase as a no-server docs island."""
    app = SimApp(title="Edron Showcase", demo_id="edron-showcase-dashboard")
    pipeline = app.region("edron-showcase-pipeline", description="Pipeline status")
    approval = app.region("edron-showcase-approval", description="Release approval")
    runs = app.region("edron-showcase-runs", description="Recent runs")
    inventory = app.region("edron-showcase-inventory", description="Edron vocabulary")

    @app.page("/")
    def home() -> Page:
        return Page(
            html.div(
                html.aside(
                    html.div(
                        html.span("◇", aria={"hidden": "true"}),
                        html.strong("Edron"),
                        class_="showcase-brand",
                    ),
                    html.span("APP FACADE", class_="showcase-nav-label"),
                    html.nav(
                        html.a(
                            "Overview",
                            href=SafeUrl.parse(
                                "#edron-showcase-overview", purpose=UrlPurpose.NAVIGATION
                            ),
                            class_="showcase-nav-link showcase-nav-link--active",
                        ),
                        html.a(
                            "Deployments",
                            href=SafeUrl.parse(
                                "#edron-showcase-runs", purpose=UrlPurpose.NAVIGATION
                            ),
                            class_="showcase-nav-link",
                        ),
                        html.a(
                            "Components",
                            href=SafeUrl.parse(
                                "#edron-showcase-inventory", purpose=UrlPurpose.NAVIGATION
                            ),
                            class_="showcase-nav-link",
                        ),
                        aria={"label": "Showcase navigation"},
                    ),
                    html.div(
                        html.span("AL", class_="showcase-avatar"),
                        html.div(html.strong("Alex Lee"), html.small("Platform lead")),
                        class_="showcase-account",
                    ),
                    class_="hedron-app-nav showcase-nav",
                ),
                html.main(
                    html.header(
                        html.div(
                            html.span("EDRON / SHOWCASE", class_="hedron-app-kicker"),
                            html.h2("Command center"),
                            html.p(
                                "A batteries-included workspace composed from Edron page methods."
                            ),
                        ),
                        html.div(
                            html.span("● All systems operational", class_="showcase-health"),
                            html.button("Export report", type="button", class_="hedron-ui-button"),
                            class_="showcase-header-actions",
                        ),
                        class_="hedron-app-heading showcase-heading",
                    ),
                    html.div(
                        html.strong("Workspace health"),
                        html.span("Every surface is request-local, bounded, and server-rendered."),
                        class_="showcase-alert",
                        role="status",
                    ),
                    html.div(
                        _metric("Monthly volume", "1.28M", "+18.4%"),
                        _metric("Reusable pages", "12", "+4 this quarter"),
                        _metric("Stable APIs", "100%", "Edron 1.0"),
                        _metric("Time to deploy", "11m", "−24%"),
                        class_="hedron-app-metrics showcase-metrics",
                        aria={"label": "Workspace metrics"},
                    ),
                    html.div(
                        _pipeline_card(pipeline),
                        _approval_card(approval),
                        class_="showcase-two-column",
                    ),
                    html.div(
                        _runs_card(runs),
                        _activity_card(),
                        class_="showcase-two-column showcase-two-column--wide",
                    ),
                    _inventory(inventory),
                    id="edron-showcase-overview",
                    class_="hedron-app-main showcase-main",
                ),
                class_="hedron-demo hedron-app-shell showcase-shell edron-showcase-shell",
            ),
            title="Edron Showcase",
        )

    @app.fragment("/pipeline/refresh", region=pipeline, method="POST")
    def refresh_pipeline():
        return swap(_pipeline_card(pipeline, refreshed=True))

    @app.action("/approve", region=approval, method="POST")
    def approve_release():
        return swap(_approval_card(approval, approved=True))

    @app.fragment("/runs/all", region=runs)
    def all_runs():
        return swap(_runs_card(runs))

    @app.fragment("/runs/attention", region=runs)
    def attention_runs():
        return swap(_runs_card(runs, "attention"))

    @app.fragment("/components/map", region=inventory)
    def component_map():
        return swap(
            html.section(
                html.div(
                    html.div(
                        html.span("Surface map", class_="hedron-app-kicker"),
                        html.h3("The Edron boundary stays inspectable"),
                        html.p(
                            "Pages, fragments, actions, and outcomes remain ordinary Python "
                            "contracts."
                        ),
                    ),
                    html.span("6 surfaces", class_="hedron-status"),
                    class_="showcase-card-heading",
                ),
                html.div(
                    html.span("Page", class_="showcase-chip showcase-chip--accent"),
                    html.span("Fragment", class_="showcase-chip"),
                    html.span("Action", class_="showcase-chip"),
                    html.span("Outcome", class_="showcase-chip"),
                    html.span("Progressive fallback", class_="showcase-chip"),
                    class_="showcase-chip-list",
                ),
                id=inventory.id,
                class_="hedron-card hedron-app-panel showcase-card",
            )
        )

    island = embed_demo(app, class_="hedron-sim hedron-sim--browser", trace=True)
    return wrap_browser_chrome(
        island,
        url="127.0.0.1:8000",
        caption=(
            "Offline Edron Showcase — try Refresh pipeline, filter Recent runs, "
            "approve the release, "
            "and inspect the Edron surface map."
        ),
    )
