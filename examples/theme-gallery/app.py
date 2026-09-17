"""Visual theme gallery for Hedron's built-in interfaces.

Run with::

    uv run uvicorn --app-dir examples/theme-gallery app:app --reload
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi.responses import FileResponse

from hedron import (
    AccountSummary,
    ActionGroup,
    Alert,
    AppShell,
    Badge,
    Brand,
    Button,
    CameraCapture,
    Card,
    Carousel,
    ChatInput,
    ChatMessage,
    Checkbox,
    ChipInput,
    CircularProgress,
    ClipboardCopy,
    CodeViewer,
    ColorInput,
    ConfirmButton,
    ConnectorFlow,
    ConnectorNode,
    ConnectorTrack,
    DateInput,
    DateTimeInput,
    DescriptionList,
    Dialog,
    Dialogue,
    DirectoryUpload,
    Divider,
    EnvironmentBanner,
    Expander,
    FileUpload,
    FlowStep,
    Footer,
    Form,
    FormErrors,
    FormField,
    Gallery,
    GeolocationButton,
    Grid,
    Header,
    Heading,
    Hedron,
    HelpInspector,
    IconButton,
    Identity,
    Image,
    Inline,
    Link,
    LinkButton,
    List,
    Map,
    Math,
    Metric,
    MicrophoneCapture,
    MultiSelect,
    NavStatus,
    NumberInput,
    Page,
    Pagination,
    ParameterViewer,
    Pills,
    Popover,
    PredictionLabel,
    ProcessFlow,
    Progress,
    RadioGroup,
    RangeInput,
    RatingInput,
    ResourceList,
    ResourceRow,
    ScrollRegion,
    SegmentedControl,
    Select,
    SelectSlider,
    Skeleton,
    Stack,
    StateView,
    Status,
    SubmitButton,
    Surface,
    Table,
    Tabs,
    Text,
    TextArea,
    TextInput,
    TimeInput,
    Timeline,
    Toast,
    ToggleSwitch,
    Tooltip,
    Typography,
)
from hedron_charts import LineChart
from hedron_core.builtins.appearance import Appearance, Emphasis, Size
from hedron_core.component import NodeLike
from hedron_core.icons import register_first_party_icons

Mode = Literal["light", "dark"]
ThemeName = Literal["default", "aurora"]
APPEARANCES: tuple[Appearance, ...] = ("solid", "outline", "soft", "ghost", "plain", "raised")
EMPHASES: tuple[Emphasis, ...] = ("primary", "secondary", "danger", "neutral")

app = Hedron(
    title="Hedron theme gallery",
    security="standard",
    explorer="off",
    session_secret="local-theme-gallery-only",
)
register_first_party_icons()


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
    *content: NodeLike,
) -> Page:
    navigation = (
        _nav_link("Dashboard", "/", current, mode, theme),
        _nav_link("Settings", "/settings", current, mode, theme),
        _nav_link("Orders", "/orders", current, mode, theme),
        _nav_link("Support", "/support", current, mode, theme),
        _nav_link("Components", "/components", current, mode, theme),
        _nav_link("Forms", "/forms", current, mode, theme),
        _nav_link("Surfaces", "/surfaces", current, mode, theme),
        _nav_link("Content", "/content", current, mode, theme),
        _nav_link("Media", "/media", current, mode, theme),
    )
    mode_controls = Inline(
        Badge(f"{theme.title()} · {mode}", tone="info"),
        LinkButton("Default", _href(current, mode, "default")),
        LinkButton("Aurora", _href(current, mode, "aurora")),
        LinkButton("Light", _href(current, "light", theme)),
        LinkButton("Dark", _href(current, "dark", theme)),
        gap="sm",
    )
    return Page(
        Header(
            Stack(
                Text("HEDRON / UI LAB", as_="small"),
                Heading("Theme gallery", level=2),
                gap="xs",
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
        LineChart(
            [
                {"month": month, "revenue": revenue}
                for month, revenue in (
                    ("Apr", 82),
                    ("May", 96),
                    ("Jun", 104),
                    ("Jul", 110),
                    ("Aug", 114),
                    ("Sep", 128),
                )
            ],
            x="month",
            y="revenue",
            title="Revenue trend",
            description="Monthly revenue in thousands of dollars.",
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


@app.page("/forms")
def forms(mode: Mode = "light", theme: ThemeName = "default") -> Page:
    return _chrome(
        "Form controls",
        "/forms",
        mode,
        theme,
        Grid(
            Card(
                FormField(
                    name="search",
                    label="Search",
                    control=TextInput("search", placeholder="Search projects"),
                ),
                FormField(
                    name="password",
                    label="Password",
                    control=TextInput("password", type="password", value="sample-password"),
                ),
                FormField(
                    name="disabled",
                    label="Disabled",
                    control=TextInput(
                        "disabled", value="Managed by your organization", disabled=True
                    ),
                ),
                FormField(
                    name="invalid",
                    label="Invalid",
                    control=TextInput("invalid", value="Incomplete"),
                    error="Enter a complete value.",
                ),
                FormField(
                    name="notes", label="Notes", control=TextArea("notes", placeholder="Add a note")
                ),
                title="Text and validation",
            ),
            Card(
                FormField(name="date", label="Date", control=DateInput("date", value="2026-09-17")),
                FormField(name="time", label="Time", control=TimeInput("time", value="09:30")),
                FormField(
                    name="datetime",
                    label="Date and time",
                    control=DateTimeInput("datetime", value="2026-09-17T09:30"),
                ),
                FormField(
                    name="teams",
                    label="Teams",
                    control=MultiSelect(
                        "teams",
                        (
                            ("design", "Design"),
                            ("engineering", "Engineering"),
                            ("operations", "Operations"),
                        ),
                        values=("design", "engineering"),
                    ),
                ),
                FormField(
                    name="priority",
                    label="Priority",
                    control=SelectSlider("priority", ("Low", "Medium", "High"), value="Medium"),
                ),
                title="Native selections",
            ),
            Card(
                Checkbox("terms", "I agree to the workspace guidelines", checked=True),
                ToggleSwitch("enabled", "Enable notifications", checked=True),
                ToggleSwitch("locked", "Managed notification setting", checked=True, disabled=True),
                SegmentedControl(
                    "view", "View", (("list", "List"), ("board", "Board")), value="list"
                ),
                Pills(
                    "period",
                    "Reporting period",
                    (("week", "Week"), ("month", "Month")),
                    value="month",
                ),
                RatingInput("rating", "Quality rating", value=4),
                title="Choices",
            ),
            Card(
                FileUpload(label="Upload attachment", hint="Choose a document or image."),
                DirectoryUpload(label="Upload folder"),
                ChipInput("tags", values=("Design", "Reviewed"), placeholder="Add a tag"),
                FormField(
                    name="budget", label="Budget", control=NumberInput("budget", value=2500, min=0)
                ),
                FormField(
                    name="opacity",
                    label="Opacity",
                    control=RangeInput("opacity", value=70, min=0, max=100),
                ),
                title="Files and values",
            ),
            columns=2,
        ),
    )


@app.get("/gallery-art.svg")
def gallery_art() -> FileResponse:
    return FileResponse(Path(__file__).with_name("landscape.svg"), media_type="image/svg+xml")


@app.page("/media")
def media(mode: Mode = "light", theme: ThemeName = "default") -> Page:
    return _chrome(
        "Media and capture",
        "/media",
        mode,
        theme,
        Gallery(
            [
                {
                    "src": "/gallery-art.svg",
                    "alt": "Layered blue and violet hills",
                    "caption": "Workspace cover",
                },
                {
                    "src": "/gallery-art.svg",
                    "alt": "Layered blue and violet hills",
                    "caption": "Project cover",
                },
            ],
            lightbox=True,
        ),
        Grid(
            Card(Image("/gallery-art.svg", alt="Layered blue and violet hills"), title="Image"),
            Card(
                Carousel(
                    [
                        (
                            "Overview",
                            Stack(
                                Heading("A connected workspace", level=3),
                                Text("Shared foundations for every screen."),
                            ),
                        ),
                        (
                            "Details",
                            Stack(
                                Heading("Built for your team", level=3),
                                Text("Consistent controls and readable content."),
                            ),
                        ),
                    ],
                    label="Product tour",
                ),
                title="Carousel",
            ),
            Card(
                CameraCapture(),
                MicrophoneCapture(),
                GeolocationButton(),
                title="Native capture controls",
            ),
            Card(
                Map(
                    center=(40.71, -74.01),
                    zoom=10,
                    markers=[{"lat": 40.71, "lon": -74.01, "label": "New York workspace"}],
                ),
                title="Map fallback",
            ),
            columns=2,
        ),
    )


@app.page("/surfaces")
def surfaces(mode: Mode = "light", theme: ThemeName = "default") -> Page:
    return _chrome(
        "Surfaces and workflows",
        "/surfaces",
        mode,
        theme,
        Grid(
            *(
                Card(
                    Stack(
                        Heading(appearance.title(), level=3),
                        Text("Shared shape, spacing, and palette."),
                        Button("Action", appearance="outline"),
                    ),
                    appearance=appearance,
                )
                for appearance in APPEARANCES
            ),
            columns=3,
        ),
        Grid(
            Surface(Text("Default surface")),
            Surface(Text("Plain surface"), appearance="plain"),
            Surface(Text("Raised surface"), appearance="raised"),
            columns=3,
        ),
        Grid(
            Card(
                Text("The inset belongs to the body; the header and footer stay flush."),
                title="Compact card",
                padding="sm",
                footer=Button("Continue", size="sm"),
            ),
            Card(
                Text("A roomier body uses the same spacing scale."),
                title="Spacious card",
                padding="lg",
                footer=Button("Continue"),
            ),
            columns=2,
        ),
        ProcessFlow(
            FlowStep("Connect", status="complete", description="Source verified"),
            FlowStep("Import", status="current", description="Reading records"),
            FlowStep("Review", status="blocked", description="Approval required"),
            FlowStep("Publish", status="pending", description="Waiting for review"),
            label="Import workflow",
        ),
        ConnectorFlow(
            ConnectorNode(
                "Source workspace", detail="Customer records", runtime="Ready", state="succeeded"
            ),
            ConnectorTrack(
                Text("Syncing records", as_="small"), active=True, label="Active transfer"
            ),
            ConnectorNode(
                "Analytics warehouse",
                kind="target",
                detail="Reporting dataset",
                runtime="Running",
                state="running",
            ),
            appearance="soft",
            background="dots",
        ),
        Grid(
            StateView(
                "No projects yet",
                description="Create your first project to get started.",
                actions=Button("Create project"),
            ),
            StateView(
                "Preparing your workspace",
                kind="loading",
                description="This may take a moment.",
                children=Skeleton(lines=2),
            ),
            StateView("Changes saved", kind="success", description="Your workspace is up to date."),
            StateView(
                "Unable to connect",
                kind="error",
                description="Try again in a moment.",
                actions=Button("Retry", appearance="outline"),
            ),
            StateView(
                "Access required",
                kind="permission",
                description="Ask a workspace owner for access.",
            ),
            StateView(
                "You are offline",
                kind="offline",
                description="Your changes will sync when you reconnect.",
            ),
            columns=2,
        ),
    )


@app.page("/content")
def content(mode: Mode = "light", theme: ThemeName = "default") -> Page:
    return _chrome(
        "Identity and content",
        "/content",
        mode,
        theme,
        Grid(
            Card(
                Brand("Northstar", mark_text="N", subtitle="A connected workspace"),
                Identity("Maya Chen", detail="Workspace owner"),
                AccountSummary("Northstar Studio", detail="Scale plan", mark_text="NS"),
                EnvironmentBanner("Preview workspace", tone="warning"),
                NavStatus("All changes synced", tone="success"),
                title="Identity and chrome",
            ),
            Card(
                Typography("PRODUCT UPDATE", role="eyebrow"),
                Typography("Clear, considered interfaces", role="title"),
                Typography(
                    "Body copy, labels, and supporting text share one readable scale.", role="body"
                ),
                Typography("Supporting details stay legible in both palettes.", role="caption"),
                Divider(),
                DescriptionList(
                    ("Workspace", "Northstar Studio"),
                    ("Region", "US East"),
                    ("Plan", Badge("Scale", tone="info")),
                ),
                List("Readable typography", "Consistent surfaces", "Predictable controls"),
                Link("Read the documentation", _href("/", mode, theme)),
                title="Typography and lists",
            ),
            Card(
                ResourceList(
                    ResourceRow(
                        "Design system",
                        description="Shared components and foundations",
                        href=_href("/components", mode, theme),
                        meta=Badge("Updated", tone="success"),
                    ),
                    ResourceRow(
                        "Quarterly report",
                        description="Revenue and customer health",
                        actions=Button("Download", appearance="outline", size="sm"),
                    ),
                    label="Workspace resources",
                ),
                title="Resources",
            ),
            Card(
                ParameterViewer(
                    {"temperature": 0.7, "max_tokens": 2048, "model": "workspace-assistant"}
                ),
                PredictionLabel(
                    (
                        {"class_id": "Healthy", "score": 0.94, "calibrated": True},
                        {"class_id": "At risk", "score": 0.06},
                    )
                ),
                Math(r"P(A \\mid B) = \\frac{P(B \\mid A) P(A)}{P(B)}", display=True),
                title="Model inspection",
            ),
            Card(
                Dialogue(
                    (
                        {"speaker": "Maya", "text": "Can you summarize the workspace activity?"},
                        {
                            "speaker": "Assistant",
                            "text": "Revenue is up and all systems are healthy.",
                        },
                    )
                ),
                title="Transcript",
            ),
            Card(
                ScrollRegion(
                    CodeViewer("def workspace_health():\n    return 'healthy'", language="python"),
                    size="sm",
                    label="Source code",
                ),
                HelpInspector(
                    "How this works",
                    Text("Theme tokens carry the same palette through every built-in component."),
                    open=True,
                ),
                CircularProgress(72, label="Indexing progress"),
                title="Code and inspection",
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
                gap="md",
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
    sizes: tuple[Size, ...] = ("sm", "md", "lg")
    return _chrome(
        "Component states",
        "/components",
        mode,
        theme,
        Grid(
            *(
                Card(
                    *(
                        Inline(
                            Button(emphasis.title(), appearance=appearance, emphasis=emphasis),
                            Button(
                                "Disabled", appearance=appearance, emphasis=emphasis, disabled=True
                            ),
                        )
                        for emphasis in EMPHASES
                    ),
                    title=f"{appearance.title()} buttons",
                )
                for appearance in APPEARANCES
            ),
            columns=2,
        ),
        Card(
            ActionGroup(
                *(
                    Button(f"{size.upper()} action", size=size, leading_icon="check")
                    for size in sizes
                )
            ),
            ActionGroup(
                *(
                    IconButton(
                        f"{size.upper()} settings", icon="⚙", size=size, appearance="outline"
                    )
                    for size in sizes
                )
            ),
            Button("Full width action", width="full"),
            title="Sizes and icons",
        ),
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
        Grid(
            Card(
                *(
                    Alert(
                        "Changes to this workspace are visible to your team.",
                        title=tone.title(),
                        tone=tone,
                    )
                    for tone in ("info", "success", "warning", "danger")
                ),
                title="Feedback tones",
            ),
            Card(
                Toast("Report exported successfully.", tone="success", ttl_ms=None),
                Popover(
                    Text("A themed details disclosure."), label="Details popover", mode="details"
                ),
                Popover(Text("A themed native overlay."), label="Native popover"),
                Button(
                    "Review changes",
                    appearance="outline",
                    attrs={"data-hedron-dialog-open": "#gallery-dialog"},
                ),
                Tooltip("Copy the workspace ID", ClipboardCopy("workspace-northstar")),
                title="Overlays and helpers",
            ),
            columns=2,
        ),
        Dialog(
            "Review changes",
            Text("The dialog uses the same surface, type, and control palette."),
            id="gallery-dialog",
        ),
    )
