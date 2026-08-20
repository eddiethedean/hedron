"""Data Mover-class front end built with Python and zero application CSS (#528).

Every visual decision in this fixture comes from a ``Theme`` plus Hedron's
built-in chrome components. There is no application stylesheet, no ``<style>``
block, and no ``style=`` attribute; ``hedron style check --zero-app-css`` guards
that claim.

Run with::

    uv run uvicorn --app-dir examples/chrome-zero-css app:app --reload
"""

from __future__ import annotations

from hedron import (
    ActionGroup,
    AppShell,
    Badge,
    Button,
    Card,
    CsrfField,
    DescriptionList,
    FlowStep,
    Form,
    FormField,
    FormGrid,
    Hedron,
    Icon,
    Link,
    Page,
    PageHeader,
    ProcessFlow,
    RequestIndicator,
    SkipLink,
    SplitView,
    Stack,
    StateView,
    SubmitButton,
    Table,
    TableColumn,
    Text,
    TextInput,
    Theme,
    Typography,
    compile_palette,
    register_icon,
)
from hedron_core.theme import default_theme, register_theme_instance

PANEL_ID = "main-panel"
ENVIRONMENT = "staging"

# --- Design system: one seed color, compiled to an accessible token set. -------

BRAND = compile_palette("#2f6fed")

THEME: Theme = default_theme().extend(
    "datamover",
    tokens=BRAND,
    palette={"brand.seed": "#2f6fed", "brand.soft": BRAND["color.accent-soft"]},
    density="comfortable",
    shape={"radius": "0.65rem", "radius-lg": "1rem"},
    nav_width="16rem",
    elevation={"raised": "0 1px 2px rgb(15 23 42 / 8%)"},
)
register_theme_instance(THEME)

# --- Iconography: trusted SVGs registered once, referenced by logical name. ----

_ICONS: dict[str, tuple[str, str]] = {
    "pipeline": (
        "Pipeline",
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round"><path d="M4 7h6a4 4 0 0 1 4 4v6h6"/><circle cx="4" cy="7" r="1.6"/>'
        '<circle cx="20" cy="17" r="1.6"/></svg>',
    ),
    "team": (
        "Team",
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round"><circle cx="9" cy="8" r="3.2"/>'
        '<path d="M3 20a6 6 0 0 1 12 0"/><path d="M16 6.5a3 3 0 0 1 0 6"/></svg>',
    ),
    "settings": (
        "Settings",
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round"><circle cx="12" cy="12" r="3.2"/>'
        '<path d="M12 3v2.4M12 18.6V21M3 12h2.4M18.6 12H21"/></svg>',
    ),
    "audit": (
        "Audit log",
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round"><path d="M6 3h9l4 4v14H6z"/><path d="M9 12h7M9 16h5"/></svg>',
    ),
}

for _name, (_title, _svg) in _ICONS.items():
    register_icon(_name, _svg, title=_title, source="examples/chrome-zero-css")

app = Hedron(
    title="Hedron chrome, zero application CSS",
    security="standard",
    explorer="off",
    session_secret="local-chrome-zero-css-only",
    theme=THEME.name,
    default_styles=True,
)

NAV_GROUPS: dict[str, tuple[tuple[str, str, str], ...]] = {
    "Operate": (
        ("Pipelines", "/", "pipeline"),
        ("Audit log", "/audit", "audit"),
    ),
    "Administer": (
        ("Team", "/team", "team"),
        ("Settings", "/settings", "settings"),
    ),
}


def _nav_groups(current: str) -> dict[str, list[Link]]:
    groups: dict[str, list[Link]] = {}
    for label, entries in NAV_GROUPS.items():
        groups[label] = [
            Link(
                title,
                path,
                class_="hedron-nav-link active" if path == current else "hedron-nav-link",
            )
            for title, path, _icon in entries
        ]
    return groups


def _chrome(title: str, current: str, *content: object) -> Page:
    return Page(
        SkipLink(f"#{PANEL_ID}"),
        AppShell(
            banner=Text(
                "Synthetic fixture: no data leaves this process.",
                role="caption",
            ),
            brand=Stack(
                Typography("HEDRON", role="eyebrow"),
                Typography("Data Mover", role="title"),
                gap="0.1rem",
            ),
            env_badge=Text(ENVIRONMENT, role="label"),
            account=ActionGroup(
                RequestIndicator("Working…", id="global-indicator"),
                Text("ops@example.test", role="caption"),
                label="Account",
                align="end",
            ),
            nav_groups=_nav_groups(current),
            nav_footer=Text("v0.54 preview", role="caption"),
            app_footer=Text(
                "Hedron owns every stylesheet on this path.",
                role="caption",
            ),
            content_width="wide",
            panel_id=PANEL_ID,
            body=Stack(*content, gap="1.5rem"),
        ),
        title=f"{title} · Data Mover",
        data_hedron_theme=THEME.name,
    )


@app.page("/")
def pipelines() -> Page:
    flow = ProcessFlow(
        FlowStep("Discover", status="complete", description="1,284 objects catalogued"),
        FlowStep("Stage", status="complete", description="Landed in the staging bucket"),
        FlowStep("Transform", status="current", description="18 of 24 partitions applied"),
        FlowStep("Verify", status="pending", description="Row counts and checksums"),
        FlowStep("Publish", status="blocked", description="Waiting on approval from Dana"),
        label="Migration pipeline",
        direction="horizontal",
    )
    runs = Table(
        rows=[
            ["nightly-warehouse", Badge("Running", tone="info"), "18m", "1,284"],
            ["crm-backfill", Badge("Succeeded", tone="success"), "42m", "96,410"],
            ["events-replay", Badge("Failed", tone="danger"), "4m", "0"],
            ["lookup-refresh", Badge("Queued", tone="neutral"), "—", "—"],
        ],
        columns=[
            TableColumn(header="Run", size="wide"),
            TableColumn(header="Status"),
            TableColumn(header="Duration", align="end"),
            TableColumn(header="Rows", numeric=True),
        ],
        caption="Recent runs",
        density="compact",
        sticky_header=True,
        zebra=True,
    )
    return _chrome(
        "Pipelines",
        "/",
        PageHeader(
            "Pipelines",
            eyebrow="Operate",
            description="Move, verify, and publish datasets between environments.",
            actions=ActionGroup(
                Button("New pipeline", leading_icon="pipeline"),
                Button("Import", variant="secondary"),
                label="Pipeline actions",
                align="end",
            ),
        ),
        Card(flow, title="Migration pipeline"),
        SplitView(
            Card(runs, title="Runs"),
            Stack(
                StateView(
                    "Publish is waiting on approval",
                    kind="permission",
                    description="Dana must approve the production publish step.",
                    actions=Button("Request approval"),
                ),
                Card(
                    DescriptionList(
                        ("Source", Text("warehouse-prod")),
                        ("Target", Text("warehouse-staging")),
                        ("Owner", Text("ops@example.test")),
                        ("Window", Text("02:00–04:00 UTC")),
                        columns=2,
                        density="compact",
                    ),
                    title="Pipeline details",
                ),
                gap="1rem",
            ),
            ratio="2:1",
            collapse="lg",
        ),
    )


@app.page("/sign-in")
def sign_in() -> Page:
    return _chrome(
        "Sign in",
        "/sign-in",
        PageHeader(
            "Sign in",
            eyebrow="Data Mover",
            description="Synthetic credentials only; nothing is verified.",
        ),
        SplitView(
            Card(
                form_sign_in(),
                title="Workspace access",
            ),
            StateView(
                "Single sign-on is offline",
                kind="offline",
                description="The synthetic identity provider is not reachable.",
                detail="idp.connect: ECONNREFUSED",
            ),
            ratio="1:1",
            collapse="md",
        ),
    )


def form_sign_in(error: str | None = None) -> Form:
    fields = FormGrid(
        FormField(
            name="email",
            label="Work email",
            control=TextInput("email", type="email", required=True),
            required=True,
        ),
        FormField(
            name="password",
            label="Password",
            control=TextInput("password", type="password", required=True),
            error=error,
            required=True,
        ),
        columns={"base": 1, "md": 2},
    )
    return Form(
        fields,
        CsrfField(),
        ActionGroup(
            SubmitButton("Continue"),
            Button("Use a recovery code", variant="secondary"),
            label="Sign-in actions",
        ),
        action="/sign-in",
        method="post",
    )


@app.page("/sign-in", methods=("POST",))
def sign_in_submit() -> Page:
    return _chrome(
        "Sign in",
        "/sign-in",
        PageHeader("Sign in", eyebrow="Data Mover"),
        StateView(
            "Credentials are not checked in this fixture",
            kind="error",
            description="Use the navigation to explore the synthetic surfaces.",
        ),
    )


@app.page("/settings")
def settings() -> Page:
    return _chrome(
        "Settings",
        "/settings",
        PageHeader(
            "Settings",
            eyebrow="Administer",
            description="Presentation is configured in Python, not CSS.",
            actions=ActionGroup(Button("Save", leading_icon="settings"), align="end"),
        ),
        Card(
            DescriptionList(
                ("Theme", Text(THEME.name)),
                ("Inherits from", Text(THEME.parent or "—")),
                ("Density", Text(THEME.density or "—")),
                ("Nav width", Text(THEME.nav_width or "—")),
                ("Accent", Text(THEME.tokens["color.accent"])),
                ("Seed", Text(THEME.palette["brand.seed"])),
                columns=2,
            ),
            title="Design system",
        ),
        Card(
            FormGrid(
                FormField(
                    name="workspace",
                    label="Workspace",
                    control=TextInput("workspace", value="Northstar Data"),
                ),
                FormField(
                    name="region",
                    label="Region",
                    control=TextInput("region", value="us-east"),
                ),
                FormField(
                    name="retention",
                    label="Retention (days)",
                    control=TextInput("retention", value="90"),
                ),
                columns={"base": 1, "md": 2, "lg": 3},
            ),
            title="Workspace",
        ),
    )


@app.page("/team")
def team() -> Page:
    return _chrome(
        "Team",
        "/team",
        PageHeader("Team", eyebrow="Administer", description="Synthetic membership list."),
        Card(
            Table(
                ["Member", "Role", "Status"],
                [
                    ["Dana Ellis", "Approver", Badge("Active", tone="success")],
                    ["Rae Osei", "Operator", Badge("Active", tone="success")],
                    ["Sam Rivera", "Viewer", Badge("Invited", tone="warning")],
                ],
                caption="Workspace members",
                density="comfortable",
            ),
            footer=ActionGroup(Button("Invite", leading_icon="team"), align="end"),
        ),
    )


@app.page("/audit")
def audit() -> Page:
    return _chrome(
        "Audit log",
        "/audit",
        PageHeader("Audit log", eyebrow="Operate", description="Nothing recorded yet."),
        StateView(
            "No audit events",
            kind="empty",
            description="Events appear here after the first published run.",
            actions=Button("Run a pipeline", leading_icon="pipeline"),
        ),
        Card(
            Stack(
                Typography("Legend", role="label"),
                ActionGroup(
                    Icon("pipeline", title="Pipeline events"),
                    Icon("team", title="Membership events"),
                    Icon("settings", title="Configuration events"),
                    label="Event categories",
                ),
                gap="0.5rem",
            ),
            title="Event categories",
        ),
    )
