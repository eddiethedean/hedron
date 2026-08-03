"""Static team-admin CRUD page proof for phase 0.1 (no HTTP)."""

from __future__ import annotations

from hedron_core import (
    Alert,
    Button,
    Card,
    Footer,
    Form,
    FormErrors,
    FormField,
    Header,
    Heading,
    Main,
    Nav,
    Page,
    RenderContext,
    RenderMode,
    RenderResult,
    SafeUrl,
    Section,
    Select,
    Stack,
    SubmitButton,
    Table,
    Text,
    TextInput,
    UrlPurpose,
    html,
    render,
)

USERS = (
    ("1", "Ada Lovelace", "ada@example.com", "admin"),
    ("2", "Grace Hopper", "grace@example.com", "member"),
    ("3", "Alan Turing", "alan@example.com", "member"),
)


def users_table() -> Table:
    return Table(
        headers=["ID", "Name", "Email", "Role"],
        rows=[list(row) for row in USERS],
        caption="Team members",
    )


def create_user_form(*, errors: tuple[str, ...] = ()) -> Card:
    return Card(
        Form(
            FormErrors(errors),
            FormField(
                name="name",
                label="Name",
                control=TextInput("name", required=True),
                required=True,
                help="Full name as shown to the team.",
            ),
            FormField(
                name="email",
                label="Email",
                control=TextInput("email", type="email", required=True),
                required=True,
            ),
            FormField(
                name="role",
                label="Role",
                control=Select(
                    "role",
                    options=[("member", "Member"), ("admin", "Admin")],
                    value="member",
                    required=True,
                ),
                required=True,
            ),
            SubmitButton("Create user"),
            action=SafeUrl.parse("/users", purpose=UrlPurpose.FORM_ACTION),
            method="post",
        ),
        title="Create user",
    )


def team_admin_page(*, form_errors: tuple[str, ...] = ()) -> Page:
    users_href = SafeUrl.parse("/users", purpose=UrlPurpose.NAVIGATION)
    return Page(
        Header(
            Heading("Hedron Team Admin", level=1),
            Nav(html.a("Users", href=users_href)),
        ),
        Main(
            Section(
                Stack(
                    Heading("Users", level=2),
                    users_table(),
                    create_user_form(errors=form_errors),
                    Alert(
                        "Static phase 0.1 proof — no HTTP server required.",
                        tone="info",
                        title="Offline render",
                    ),
                    Button("Refresh list"),
                )
            )
        ),
        Footer(Text("© Hedron reference application")),
        title="Team Admin",
        lang="en",
    )


def render_page() -> RenderResult:
    context = RenderContext.standalone(locale="en", theme="default")
    return render(team_admin_page(), context=context, mode=RenderMode.PAGE)


def render_users_fragment() -> RenderResult:
    context = RenderContext.standalone(locale="en")
    return render(users_table(), context=context, mode=RenderMode.FRAGMENT)


if __name__ == "__main__":
    print(render_page().html)
