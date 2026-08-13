"""Visual theme gallery for Hedron's built-in interfaces.

Run with::

    uv run uvicorn --app-dir examples/theme-gallery app:app --reload
"""

from __future__ import annotations

from typing import Literal

from hedron import (
    Alert,
    AppShell,
    Badge,
    Button,
    Card,
    ChatInput,
    ChatMessage,
    ChipInput,
    CodeViewer,
    ColorInput,
    ConfirmButton,
    Expander,
    Footer,
    Form,
    FormErrors,
    FormField,
    Grid,
    Header,
    Heading,
    Hedron,
    Inline,
    Link,
    LinkButton,
    Metric,
    NumberInput,
    Page,
    Pagination,
    Pills,
    Popover,
    Progress,
    RadioGroup,
    RangeInput,
    RatingInput,
    SegmentedControl,
    Select,
    Skeleton,
    Stack,
    Status,
    SubmitButton,
    Table,
    Tabs,
    Text,
    TextArea,
    TextInput,
    Timeline,
    ToggleSwitch,
)

Mode = Literal["light", "dark"]
ThemeName = Literal["default", "aurora"]

app = Hedron(
    title="Hedron theme gallery",
    security="standard",
    explorer="off",
    session_secret="local-theme-gallery-only",
)


def _href(path: str, mode: Mode, theme: ThemeName) -> str:
    return f"{path}?mode={mode}&theme={theme}"


def _nav_link(label: str, path: str, current: str, mode: Mode, theme: ThemeName) -> Link:
    active = path == current
    return Link(
        label,
        _href(path, mode, theme),
        class_="hedron-nav-link active" if active else "hedron-nav-link",
    )


def _chrome(
    title: str,
    current: str,
    mode: Mode,
    theme: ThemeName,
    *content: object,
) -> Page:
    navigation = (
        _nav_link("Dashboard", "/", current, mode, theme),
        _nav_link("Settings", "/settings", current, mode, theme),
        _nav_link("Orders", "/orders", current, mode, theme),
        _nav_link("Support", "/support", current, mode, theme),
        _nav_link("Components", "/components", current, mode, theme),
    )
    mode_controls = Inline(
        Badge(f"{theme.title()} · {mode}", tone="info"),
        LinkButton("Default", _href(current, mode, "default")),
        LinkButton("Aurora", _href(current, mode, "aurora")),
        LinkButton("Light", _href(current, "light", theme)),
        LinkButton("Dark", _href(current, "dark", theme)),
        gap="0.45rem",
    )
    return Page(
        Header(
            Stack(
                Text("HEDRON / UI LAB", as_="small"),
                Heading("Theme gallery", level=2),
                gap="0.15rem",
            ),
            mode_controls,
        ),
        AppShell(
            nav=navigation,
            body=Stack(
                Heading(title, level=1),
                Text(
                    "A real-world composition of Hedron built-ins, rendered against the "
                    f"{theme} theme's {mode} palette."
                ),
                *content,
                gap="1.5rem",
            ),
        ),
        Footer(Text("Hedron theme gallery · local visual QA fixture", as_="small")),
        title=f"{title} · Hedron theme gallery",
        data_theme=mode,
        data_hedron_theme=theme,
    )


@app.page("/")
def dashboard(mode: Mode = "light", theme: ThemeName = "default") -> Page:
    return _chrome(
        "Operations dashboard",
        "/",
        mode,
        theme,
        Alert(
            "All systems are healthy. Data refreshed less than a minute ago.",
            title="Live workspace",
            tone="success",
        ),
        Grid(
            Metric("Monthly revenue", "$128,430", delta="+12.4%", delta_tone="up"),
            Metric("Active accounts", "8,942", delta="+418", delta_tone="up"),
            Metric("Open tickets", "37", delta="-8", delta_tone="up"),
            Metric("Churn risk", "2.8%", delta="+0.3%", delta_tone="down"),
            columns=4,
        ),
        Grid(
            Card(
                Table(
                    ["Account", "Plan", "Health", "Value"],
                    [
                        ["Northstar Labs", "Scale", Badge("Healthy", tone="success"), "$18,400"],
                        ["Acme Systems", "Pro", Badge("Watch", tone="warning"), "$12,800"],
                        ["Vertex Group", "Scale", Badge("Healthy", tone="success"), "$9,620"],
                        ["Fable Studio", "Starter", Badge("At risk", tone="danger"), "$2,140"],
                    ],
                    caption="Priority accounts",
                ),
                footer=Inline(
                    LinkButton("View accounts", _href("/orders", mode, theme)),
                    Button("Export report", variant="secondary"),
                ),
            ),
            Stack(
                Card(
                    Heading("Quarterly target", level=3),
                    Text("$385k of $500k booked"),
                    Progress(77, label="77 percent of quarterly revenue target"),
                    title="Revenue progress",
                ),
                Card(
                    Timeline(
                        [
                            ("09:42", "Payment received", Text("Northstar Labs · $18,400")),
                            ("09:18", "Workspace upgraded", Text("Vertex Group moved to Scale")),
                            ("08:55", "Risk detected", Text("Fable Studio engagement fell 18%")),
                        ],
                        label="Recent activity",
                    ),
                    title="Recent activity",
                ),
                gap="1rem",
            ),
            columns=2,
        ),
    )


@app.page("/settings")
def settings(mode: Mode = "light", theme: ThemeName = "default") -> Page:
    profile_form = Form(
        FormErrors(["The reply-to address needs verification."]),
        Grid(
            FormField(
                name="workspace",
                label="Workspace name",
                control=TextInput("workspace", value="Northstar Studio"),
                help="Shown to everyone in your organization.",
                required=True,
            ),
            FormField(
                name="reply_to",
                label="Reply-to email",
                control=TextInput(
                    "reply_to",
                    value="hello@example.test",
                    type="email",
                ),
                error="Verify this address before sending campaigns.",
            ),
            columns=2,
        ),
        FormField(
            name="summary",
            label="Workspace summary",
            control=TextArea(
                "summary",
                value="Product, growth, and customer operations in one place.",
            ),
            help="Keep it short and specific.",
        ),
        Grid(
            FormField(
                name="region",
                label="Data region",
                control=Select(
                    "region",
                    [("us-east", "US East"), ("eu-west", "EU West"), ("ap-south", "AP South")],
                    value="us-east",
                ),
            ),
            FormField(
                name="seats",
                label="Seat limit",
                control=NumberInput("seats", value=24, min=1, max=500),
            ),
            columns=2,
        ),
        FormField(
            name="retention",
            label="Retention window",
            control=RangeInput(
                "retention",
                value=60,
                min=30,
                max=90,
                markers=(30, 60, 90),
            ),
            help="60 days",
        ),
        ChipInput("domains", values=("example.com", "northstar.test"), placeholder="Add domain"),
        ToggleSwitch("weekly_digest", "Send a weekly performance digest", checked=True),
        ToggleSwitch("product_updates", "Email me about product updates"),
        Inline(SubmitButton("Save changes"), Button("Cancel", variant="secondary")),
        action="/settings",
        method="post",
    )
    return _chrome(
        "Workspace settings",
        "/settings",
        mode,
        theme,
        Grid(
            Card(profile_form, title="Profile and preferences"),
            Stack(
                Card(
                    SegmentedControl(
                        "density",
                        "Interface density",
                        (("comfortable", "Comfortable"), ("compact", "Compact")),
                        value="comfortable",
                    ),
                    Pills(
                        "week_start",
                        "Week starts on",
                        (("sun", "Sunday"), ("mon", "Monday")),
                        value="mon",
                    ),
                    FormField(
                        name="accent",
                        label="Accent color",
                        control=ColorInput(
                            "accent",
                            value="#6d3ce7" if theme == "aurora" else "#2563eb",
                        ),
                    ),
                    title="Appearance",
                ),
                Card(
                    RatingInput("experience", "Setup experience", value=4),
                    Text("Your response helps us improve onboarding.", as_="small"),
                    title="Feedback",
                ),
                Card(
                    Text("This permanently removes the workspace and all associated data."),
                    ConfirmButton("Delete workspace", confirm="Delete this workspace?"),
                    title="Danger zone",
                ),
            ),
            columns=2,
        ),
    )


@app.page("/orders")
def orders(mode: Mode = "light", theme: ThemeName = "default") -> Page:
    return _chrome(
        "Orders and fulfillment",
        "/orders",
        mode,
        theme,
        Inline(
            SegmentedControl(
                "status",
                "Order status",
                (("all", "All"), ("open", "Open"), ("fulfilled", "Fulfilled")),
                value="all",
            ),
            Popover(
                Text("CSV exports include the current filters and visible columns."),
                label="Export options",
                mode="details",
            ),
            gap="1rem",
        ),
        Grid(
            Card(
                Heading("#HD-1048", level=3),
                Inline(Badge("Paid", tone="success"), Badge("Priority", tone="info")),
                Text("Maya Chen · 3 items"),
                Text("Ships to Brooklyn, NY", as_="small"),
                footer=Inline(Button("Fulfill"), Button("Details", variant="secondary")),
            ),
            Card(
                Heading("#HD-1047", level=3),
                Inline(Badge("Pending", tone="warning"), Badge("Standard")),
                Text("Jon Bell · 1 item"),
                Text("Ships to Austin, TX", as_="small"),
                footer=Inline(Button("Review"), Button("Details", variant="secondary")),
            ),
            Card(
                Heading("#HD-1046", level=3),
                Inline(Badge("Refunded", tone="danger"), Badge("Archived")),
                Text("Ari Gomez · 2 items"),
                Text("Returned on August 12", as_="small"),
                footer=Inline(Button("Details", variant="secondary")),
            ),
            columns=3,
        ),
        Card(
            Table(
                ["Order", "Customer", "Date", "Status", "Total"],
                [
                    ["#HD-1048", "Maya Chen", "Aug 13", Badge("Paid", tone="success"), "$248.00"],
                    ["#HD-1047", "Jon Bell", "Aug 13", Badge("Pending", tone="warning"), "$84.00"],
                    [
                        "#HD-1046",
                        "Ari Gomez",
                        "Aug 12",
                        Badge("Refunded", tone="danger"),
                        "$162.00",
                    ],
                    ["#HD-1045", "Noah Reed", "Aug 12", Badge("Fulfilled", tone="info"), "$416.00"],
                ],
                caption="Recent orders",
            ),
            footer=Pagination(page=2, page_size=4, total=32, base_path="/orders"),
        ),
    )


@app.page("/support")
def support(mode: Mode = "light", theme: ThemeName = "default") -> Page:
    return _chrome(
        "Customer support",
        "/support",
        mode,
        theme,
        Grid(
            Stack(
                Card(
                    Inline(Badge("Open", tone="success"), Text("Ticket #4821", as_="small")),
                    Heading("Webhook retries after timeout", level=3),
                    Text("Maya Chen · Northstar Labs"),
                    title="Current conversation",
                ),
                Status("Agent notes are only visible to your team.", tone="info"),
                ChatMessage(
                    "We see intermittent timeouts when our endpoint takes longer than five "
                    "seconds.",
                    role="user",
                    status="10:18",
                ),
                ChatMessage(
                    "I found the delivery attempts. Hedron retries with exponential backoff, so "
                    "the next event should arrive automatically.",
                    role="assistant",
                    status="10:20 · Delivered",
                ),
                ChatMessage(
                    "webhook.delivery.retried · attempt 3",
                    role="tool",
                    status="10:20",
                ),
                ChatInput(
                    action="/support",
                    placeholder="Reply to Maya…",
                    include_attachments=True,
                ),
                gap="0.8rem",
            ),
            Stack(
                Card(
                    Text("Northstar Labs", as_="strong"),
                    Text("Scale plan · Customer since 2024"),
                    Inline(Badge("Healthy", tone="success"), Badge("$18.4k ARR", tone="info")),
                    title="Customer",
                ),
                Card(
                    CodeViewer(
                        "{\n"
                        '  "event": "delivery.retried",\n'
                        '  "attempt": 3,\n'
                        '  "status": "queued"\n'
                        "}",
                        language="json",
                    ),
                    title="Latest event",
                ),
                Expander(
                    "Suggested response",
                    Text("Explain the retry window and link to delivery logs."),
                    open=True,
                ),
                gap="1rem",
            ),
            columns=2,
        ),
    )


@app.page("/components")
def components(mode: Mode = "light", theme: ThemeName = "default") -> Page:
    return _chrome(
        "Component states",
        "/components",
        mode,
        theme,
        Tabs(
            (
                "Actions",
                Stack(
                    Inline(
                        Button("Primary"),
                        Button("Secondary", variant="secondary"),
                        Button("Danger", variant="danger"),
                        Button("Disabled", disabled=True),
                    ),
                    Inline(
                        LinkButton("Link button", _href("/", mode, theme)),
                        ConfirmButton("Confirm action", confirm="Continue?"),
                    ),
                ),
            ),
            (
                "Feedback",
                Stack(
                    Alert("New information is available.", tone="info"),
                    Alert("Changes saved successfully.", tone="success"),
                    Alert("Review this setting before continuing.", tone="warning"),
                    Alert("The request could not be completed.", tone="danger"),
                ),
            ),
            (
                "Loading",
                Grid(
                    Card(Skeleton(lines=4), title="Loading card"),
                    Card(Progress(42, label="42 percent complete"), title="Upload progress"),
                    columns=2,
                ),
            ),
            active="Actions",
        ),
        Grid(
            Card(
                Inline(
                    Badge("Neutral"),
                    Badge("Info", tone="info"),
                    Badge("Success", tone="success"),
                    Badge("Warning", tone="warning"),
                    Badge("Danger", tone="danger"),
                ),
                title="Badges",
            ),
            Card(
                RadioGroup(
                    "notification",
                    "Notification level",
                    (("all", "All activity"), ("mentions", "Mentions only"), ("none", "None")),
                    value="mentions",
                ),
                title="Radio group",
            ),
            columns=2,
        ),
    )
