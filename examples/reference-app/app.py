"""Authenticated team-admin CRUD reference application (phase 0.3)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated, Any, Literal

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from hedron import (
    Alert,
    Card,
    ErrorState,
    Footer,
    FormErrors,
    FormField,
    Header,
    Heading,
    Hedron,
    HedronRouter,
    Lazy,
    Main,
    Nav,
    Page,
    RefreshButton,
    Section,
    Select,
    Stack,
    SubmitButton,
    Table,
    Text,
    TextInput,
    html,
)
from hedron.routing.reverse import ComponentRef
from hedron.security.csrf import generate_csrf_token
from hedron_core import Field, FormModel, addressable
from hedron_core.security import SafeUrl, UrlPurpose

Role = Literal["admin", "member"]


@dataclass
class User:
    id: str
    name: str
    email: str
    role: Role


@dataclass
class Store:
    users: dict[str, User] = field(
        default_factory=lambda: {
            "1": User("1", "Ada Lovelace", "ada@example.com", "admin"),
            "2": User("2", "Grace Hopper", "grace@example.com", "member"),
            "3": User("3", "Alan Turing", "alan@example.com", "member"),
        }
    )
    _next_id: int = 4

    def list_users(self) -> list[User]:
        return sorted(self.users.values(), key=lambda u: int(u.id))

    def create(self, name: str, email: str, role: Role) -> User:
        user = User(str(self._next_id), name, email, role)
        self._next_id += 1
        self.users[user.id] = user
        return user

    def update(self, user_id: str, name: str, email: str, role: Role) -> User:
        if user_id not in self.users:
            raise KeyError(user_id)
        user = User(user_id, name, email, role)
        self.users[user_id] = user
        return user

    def delete(self, user_id: str) -> None:
        self.users.pop(user_id)


STORE = Store()
security = HTTPBasic(auto_error=False)
USERS = {"admin": "secret", "member": "secret"}


class UserForm(FormModel):
    name: Annotated[str, Field(min_length=1)]
    email: Annotated[str, Field(min_length=3)]
    role: Role = "member"


def get_store() -> Store:
    return STORE


def require_user(
    request: Request,
    credentials: Annotated[HTTPBasicCredentials | None, Depends(security)],
) -> str:
    if credentials is None or USERS.get(credentials.username) != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    request.state.hedron_authenticated = True
    return credentials.username


def require_admin(username: Annotated[str, Depends(require_user)]) -> str:
    if username != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    return username


def users_table_component(store: Store) -> Table:
    rows = [[u.id, u.name, u.email, u.role] for u in store.list_users()]
    return Table(headers=["ID", "Name", "Email", "Role"], rows=rows, caption="Team members")


@addressable(distribution="hedron-reference")
async def user_table(store: Store = Depends(get_store)) -> Table:
    return users_table_component(store)


def dashboard_page(*, csrf_token: str, username: str, form_errors: tuple[str, ...] = ()) -> Page:
    table_ref = ComponentRef(
        logical_id="hedron-reference:examples.reference-app.app.user_table",
        path="/users/table",
        method="GET",
        target="#user-table",
    )
    return Page(
        Header(
            Heading("Hedron Team Admin", level=1),
            Nav(
                html.a("Dashboard", href=SafeUrl.parse("/", purpose=UrlPurpose.NAVIGATION)),
                Text(f"Signed in as {username}"),
            ),
        ),
        Main(
            Section(
                Stack(
                    Heading("Users", level=2),
                    Lazy(ref=table_ref, target_id="user-table"),
                    RefreshButton(ref=table_ref, target="#user-table", label="Refresh users"),
                    Card(
                        _create_form(csrf_token=csrf_token, form_errors=form_errors),
                        title="Create user",
                    ),
                    Alert(
                        "Authenticated CRUD with CSRF, lazy addressable table, and HTMX swaps.",
                        tone="info",
                        title="Phase 0.2",
                    ),
                    _status_banner_section(),
                )
            )
        ),
        Footer(Text("© Hedron reference application")),
        title="Team Admin",
        lang="en",
    )


def _status_banner_section() -> Any:
    """Python StatusBanner beside an HDN-compiled twin with equivalent output."""
    import importlib.util
    from pathlib import Path

    from hedron_core import compile_css, compile_hdn, run_program
    from hedron_core.html import _HtmlTag

    root = Path(__file__).resolve().parent / "components" / "StatusBanner"
    spec = importlib.util.spec_from_file_location(
        "reference_status_banner",
        root / "component.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    StatusBanner = module.StatusBanner

    python_banner = StatusBanner(label="Phase 0.3 ready", tone="info")
    css = compile_css(
        (root / "styles.css").read_text(encoding="utf-8"),
        component_id="hedron-reference:StatusBanner",
    )
    hdn_nodes = run_program(
        compile_hdn((root / "template.hdn").read_text(encoding="utf-8")).program,
        {"label": "Phase 0.3 ready", "tone": "info"},
    )
    disclose = _HtmlTag("hedron-disclose")(
        html.p("Web Component disclose survives HTMX swaps."),
        **{"label": "About phase 0.3"},
    )
    return Stack(
        Heading("Authoring twins", level=3),
        Text("Python StatusBanner and HDN StatusBanner produce equivalent structure."),
        python_banner,
        *hdn_nodes,
        disclose,
        Text(f"Scoped root class: {css.manifest.symbols.get('root', '')}"),
    )


def _create_form(*, csrf_token: str, form_errors: tuple[str, ...] = ()) -> Any:
    import json

    from hedron import Form

    return Form(
        FormErrors(form_errors),
        html.input(type="hidden", name="csrf_token", value=csrf_token),
        FormField(
            name="name",
            label="Name",
            control=TextInput("name", required=True),
            required=True,
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
        **{  # type: ignore[arg-type]
            "hx-post": "/users",
            "hx-target": "#user-table",
            "hx-swap": "innerHTML",
            "hx-headers": json.dumps({"X-CSRF-Token": csrf_token}),
        },
    )


def build_hedron_app() -> Hedron:
    import hedron_core
    from hedron_core import reset_registry_for_tests

    reset_registry_for_tests()
    hedron_core._register_builtins()  # type: ignore[attr-defined]
    # Re-bind the addressable descriptor after registry reset.
    from hedron_core.registry import register_addressable

    register_addressable(
        logical_id=user_table.logical_id,
        name=user_table.name,
        module=user_table.module,
        distribution=user_table.distribution,
        methods=user_table.methods,
        include_in_schema=user_table.include_in_schema,
        cache_private=user_table.cache_private,
        tags=user_table.tags,
        docs=user_table.docs,
        factory=user_table.factory,
    )

    app = Hedron(
        title="Hedron Team Admin",
        security="standard",
        explorer="development",
        session_secret="reference-app-secret",
        theme="default",
    )
    users = HedronRouter(prefix="/users", dependencies=[Depends(require_user)])

    @app.page("/")
    def home(request: Request, username: Annotated[str, Depends(require_user)]) -> Page:
        token = request.cookies.get("hedron_csrf") or generate_csrf_token()
        return dashboard_page(csrf_token=token, username=username)

    @users.component("/table")
    async def table(store: Annotated[Store, Depends(get_store)]) -> Table:
        return users_table_component(store)

    users.include_component(user_table, path="/table-shared", dependencies=[Depends(require_user)])

    @users.action("", method="POST")
    async def create_user(
        name: Annotated[str, Form()],
        email: Annotated[str, Form()],
        role: Annotated[Role, Form()] = "member",
        store: Store = Depends(get_store),
        _: str = Depends(require_admin),
    ) -> Table | ErrorState:
        try:
            UserForm(name=name, email=email, role=role)
        except Exception as exc:  # noqa: BLE001
            return ErrorState(str(exc), retry_href="/users/table", target="#user-table")
        store.create(name=name, email=email, role=role)
        return users_table_component(store)

    @users.action("/{user_id}", method="POST")
    async def update_user(
        user_id: str,
        name: Annotated[str, Form()],
        email: Annotated[str, Form()],
        role: Annotated[Role, Form()] = "member",
        store: Store = Depends(get_store),
        _: str = Depends(require_admin),
    ) -> Table:
        store.update(user_id, name=name, email=email, role=role)
        return users_table_component(store)

    @users.action("/{user_id}/delete", method="POST")
    async def delete_user(
        user_id: str,
        store: Store = Depends(get_store),
        _: str = Depends(require_admin),
    ) -> Table:
        store.delete(user_id)
        return users_table_component(store)

    app.include_router(users)
    return app


def build_plain_fastapi_app() -> FastAPI:
    """Plain FastAPI + HedronRouter mode (no Hedron subclass)."""
    from starlette.middleware.sessions import SessionMiddleware

    import hedron_core
    from hedron.app import mount_hedron_static
    from hedron.lifespan import compose_lifespan
    from hedron.openapi import install_openapi
    from hedron.security.headers import SecurityHeadersMiddleware
    from hedron.security.policy import SecurityPolicy
    from hedron_core import reset_registry_for_tests

    reset_registry_for_tests()
    hedron_core._register_builtins()  # type: ignore[attr-defined]

    policy = SecurityPolicy.from_name("standard")
    app = FastAPI(title="Hedron Team Admin (plain)", lifespan=compose_lifespan())
    app.state.hedron_security = policy
    app.add_middleware(SessionMiddleware, secret_key="reference-app-secret")
    app.add_middleware(SecurityHeadersMiddleware, policy=policy)
    install_openapi(app)
    mount_hedron_static(app)

    router = HedronRouter(dependencies=[Depends(require_user)])

    @router.page("/")
    def home(request: Request, username: Annotated[str, Depends(require_user)]) -> Page:
        token = request.cookies.get("hedron_csrf") or generate_csrf_token()
        return dashboard_page(csrf_token=token, username=username)

    users = HedronRouter(prefix="/users", dependencies=[Depends(require_user)])

    @users.component("/table")
    async def table(store: Annotated[Store, Depends(get_store)]) -> Table:
        return users_table_component(store)

    @users.action("", method="POST")
    async def create_user(
        name: Annotated[str, Form()],
        email: Annotated[str, Form()],
        role: Annotated[Role, Form()] = "member",
        store: Store = Depends(get_store),
        _: str = Depends(require_admin),
    ) -> Table:
        store.create(name=name, email=email, role=role)
        return users_table_component(store)

    @users.action("/{user_id}", method="POST")
    async def update_user(
        user_id: str,
        name: Annotated[str, Form()],
        email: Annotated[str, Form()],
        role: Annotated[Role, Form()] = "member",
        store: Store = Depends(get_store),
        _: str = Depends(require_admin),
    ) -> Table:
        store.update(user_id, name=name, email=email, role=role)
        return users_table_component(store)

    @users.action("/{user_id}/delete", method="POST")
    async def delete_user(
        user_id: str,
        store: Store = Depends(get_store),
        _: str = Depends(require_admin),
    ) -> Table:
        store.delete(user_id)
        return users_table_component(store)

    app.include_router(router)
    app.include_router(users)
    return app


# Phase 0.1 offline static helpers (still used by snapshot/offline tests).
USERS_STATIC = (
    ("1", "Ada Lovelace", "ada@example.com", "admin"),
    ("2", "Grace Hopper", "grace@example.com", "member"),
    ("3", "Alan Turing", "alan@example.com", "member"),
)


def users_table() -> Table:
    return Table(
        headers=["ID", "Name", "Email", "Role"],
        rows=[list(row) for row in USERS_STATIC],
        caption="Team members",
    )


def create_user_form(*, errors: tuple[str, ...] = ()) -> Card:
    from hedron import Form

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
    from hedron import Button

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


def render_page():
    from hedron_core import RenderContext, RenderMode, render

    return render(
        team_admin_page(),
        context=RenderContext.standalone(locale="en", theme="default"),
        mode=RenderMode.PAGE,
    )


def render_users_fragment():
    from hedron_core import RenderContext, RenderMode, render

    return render(
        users_table(),
        context=RenderContext.standalone(locale="en"),
        mode=RenderMode.FRAGMENT,
    )


_app: Hedron | None = None


def get_app() -> Hedron:
    global _app
    if _app is None:
        _app = build_hedron_app()
    return _app


def __getattr__(name: str) -> object:
    if name == "app":
        return get_app()
    raise AttributeError(name)


if __name__ == "__main__":
    print(render_page().html)
