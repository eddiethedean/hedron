"""Authenticated team-admin CRUD reference application (0.18 train)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated, Any, Literal

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from hedron import (
    Alert,
    Auto,
    Card,
    ColorModeToggle,
    DownloadButton,
    ErrorState,
    FileUpload,
    Footer,
    FormErrors,
    FormField,
    Header,
    Heading,
    Hedron,
    HedronRouter,
    JSONViewer,
    Lazy,
    Main,
    Metric,
    Nav,
    Page,
    Progress,
    RefreshButton,
    Section,
    Select,
    Stack,
    Status,
    SubmitButton,
    Table,
    Text,
    TextInput,
    cache_data,
    html,
)
from hedron.color_mode import apply_color_mode_cookie, read_color_mode_preference
from hedron.routing.reverse import ComponentRef
from hedron.security.csrf import csrf_token_for_request, prepare_csrf_from_request, validate_csrf
from hedron.security.policy import SecurityPolicy
from hedron_core import ColorMode, Field, FormModel, Model, addressable, resolve_color_mode
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_data import (
    AsyncInMemoryDataSource,
    Column,
    DataChanges,
    DataEditor,
    DataQuery,
    DataSaveResult,
    DataTable,
    InMemoryDataSource,
)

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
AUDIT_LOG: list[str] = []


class EmployeeRow(Model):
    id: Annotated[str, Field(read_only=True, sortable=True)]
    name: Annotated[str, Field(sortable=True, filterable=True)]
    title: Annotated[str, Field()]
    active: Annotated[bool, Field(editor="boolean")] = True


class UserForm(FormModel):
    name: Annotated[str, Field(min_length=1)]
    email: Annotated[str, Field(min_length=3)]
    role: Role = "member"


def _audit_employees(changes: DataChanges[dict[str, object]]) -> None:
    AUDIT_LOG.append(
        f"updates={len(changes.updates)} inserts={len(changes.inserts)} "
        f"deletes={len(changes.deletes)}"
    )


EMPLOYEE_SOURCE = InMemoryDataSource(
    [
        {"id": "e1", "name": "Ada Lovelace", "title": "Analyst", "active": True},
        {"id": "e2", "name": "Grace Hopper", "title": "Engineer", "active": True},
        {"id": "e3", "name": "Alan Turing", "title": "Researcher", "active": False},
        {"id": "e4", "name": "Katherine Johnson", "title": "Mathematician", "active": True},
        {"id": "e5", "name": "Donald Knuth", "title": "Scientist", "active": True},
    ],
    key_field="id",
    schema=tuple(
        Column(
            name=c.name,
            label=c.label,
            editor=c.editor,
            read_only=c.read_only,
            hidden=c.hidden,
            sortable=c.sortable,
            filterable=c.filterable,
        ).to_schema()
        for c in (
            Column(name="id", read_only=True, sortable=True),
            Column(name="name", sortable=True, filterable=True),
            Column(name="title"),
            Column(name="active", editor="boolean"),
        )
    ),
    writable_fields=frozenset({"name", "title", "active"}),
    version="1",
    audit_hook=_audit_employees,
)
ASYNC_EMPLOYEE_SOURCE = AsyncInMemoryDataSource(EMPLOYEE_SOURCE)


@cache_data(ttl=30, scope="tenant", tags=("team-summary",), vary_on=("team_id",))
async def load_team_summary(team_id: int) -> dict[str, object]:
    return {
        "team_id": team_id,
        "members": len(STORE.list_users()),
        "employees": len(EMPLOYEE_SOURCE.fetch(DataQuery(limit=100)).rows),
    }


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


def dashboard_page(
    *,
    csrf_token: str,
    username: str,
    form_errors: tuple[str, ...] = (),
    request: Request | None = None,
) -> Page:
    table_ref = ComponentRef(
        logical_id="hedron-reference:examples.reference-app.app.user_table",
        path="/users/table",
        method="GET",
        target="#user-table",
    )
    preference = ColorMode.SYSTEM
    data_theme: str | None = None
    if request is not None:
        preference = read_color_mode_preference(request)
        if preference is not ColorMode.SYSTEM:
            data_theme = resolve_color_mode(preference)
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
                        title="Phase 0.3",
                    ),
                    _phase05_section(
                        csrf_token=csrf_token,
                        preference=preference,
                    ),
                    _phase06_section(csrf_token=csrf_token),
                    _status_banner_section(request=request),
                )
            )
        ),
        Footer(Text("© Hedron reference application")),
        title="Team Admin",
        lang="en",
        data_theme=data_theme,
    )


async def _employee_page() -> Any:
    return await ASYNC_EMPLOYEE_SOURCE.fetch(
        DataQuery(
            limit=5,
            allowlisted_sort_fields=frozenset({"id", "name"}),
            allowlisted_filter_fields=frozenset({"active"}),
        )
    )


def _phase05_section(
    *,
    csrf_token: str,
    preference: ColorMode = ColorMode.SYSTEM,
    page: Any | None = None,
) -> Any:
    if page is None:
        page = EMPLOYEE_SOURCE.fetch(
            DataQuery(
                limit=5,
                allowlisted_sort_fields=frozenset({"id", "name"}),
                allowlisted_filter_fields=frozenset({"active"}),
            )
        )
    editor = DataEditor(
        page=page,
        key="employees",
        row_model=EmployeeRow,
        key_field="id",
        columns=[
            Column(name="id", read_only=True, sortable=True),
            Column(name="name", sortable=True, filterable=True),
            Column(name="title"),
            Column(name="active", editor="boolean"),
        ],
        source=ASYNC_EMPLOYEE_SOURCE,
        save_endpoint="/employees/save",
        caption="Employees",
    )
    sample_rows = [{"id": u.id, "name": u.name, "role": u.role} for u in STORE.list_users()]
    return Stack(
        Heading("Data application toolkit", level=2),
        ColorModeToggle(
            preference=preference,
            action="/color-mode",
            csrf_token=csrf_token,
        ),
        Metric("Team size", len(STORE.list_users()), delta="+0", delta_tone="neutral"),
        Status("Cache and editor demos ready", tone="success"),
        Progress(40, maximum=100, label="Onboarding"),
        Auto(sample_rows),
        Auto({"region": "east", "active": True}),
        JSONViewer({"csrf": "***", "users": len(STORE.list_users())}),
        DataTable(page=page, row_model=EmployeeRow, caption="Employees (read-only)"),
        editor,
        FileUpload(accept=".csv,text/csv", maximum_size=1_000_000, label="Upload roster CSV"),
        DownloadButton(
            href=SafeUrl.parse("/downloads/roster.csv", purpose=UrlPurpose.NAVIGATION),
            filename="roster.csv",
            label="Download roster",
        ),
        html.meta(name="csrf-token", content=csrf_token),
        Alert(
            "Paged async DataEditor, Auto(), cache_data, utilities, and ColorMode (phase 0.5).",
            tone="info",
            title="Phase 0.5",
        ),
    )


def _phase06_section(*, csrf_token: str) -> Any:
    from hedron.content import Markdown
    from hedron_charts import LineChart

    chart_rows = [
        {"month": "Jan", "revenue": 10, "secret_token": "nope"},
        {"month": "Feb", "revenue": 14, "secret_token": "nope"},
        {"month": "Mar", "revenue": 18, "secret_token": "nope"},
    ]
    return Stack(
        Heading("Visualization and interactions", level=2),
        LineChart(
            chart_rows,
            x="month",
            y="revenue",
            title="Monthly revenue",
            description="Revenue increased during the period.",
        ),
        html.div(
            RefreshButton(
                "Refresh chart fragment",
                href="/charts/fragment",
                target="#chart-region",
            ),
            id="chart-region",
        ),
        html.div(Text("OOB status idle"), id="oob-status"),
        Markdown("# Phase 0.6\n\nTyped HTMX interactions and charts."),
        html.form(
            html.input(type="hidden", name="csrf_token", value=csrf_token),
            TextInput("query", value=""),
            SubmitButton("Search"),
            action=SafeUrl.parse("/charts/search", purpose=UrlPurpose.FORM_ACTION),
            method="post",
            **{
                "hx-post": "/charts/search",
                "hx-target": "#chart-region",
                "hx-sync": "closest form:drop",
            },
        ),
        Alert(
            "Charts, Markdown, typed InteractionResult, declared regions, and sync forms.",
            tone="info",
            title="Phase 0.6",
        ),
    )


_STATUS_BANNER_MOD = None


def _load_status_banner_module():
    global _STATUS_BANNER_MOD
    if _STATUS_BANNER_MOD is not None:
        return _STATUS_BANNER_MOD
    import importlib.util
    from pathlib import Path

    root = Path(__file__).resolve().parent / "components" / "StatusBanner"
    spec = importlib.util.spec_from_file_location(
        "reference_status_banner",
        root / "component.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _STATUS_BANNER_MOD = module
    return module


def _status_banner_section(*, request: Request | None = None) -> Any:
    """Python StatusBanner with build-produced scoped styles."""
    from hedron_core.compile_gate import assert_runtime_compile_allowed, is_production_env
    from hedron_core.html import _HtmlTag

    module = _load_status_banner_module()
    StatusBanner = module.StatusBanner

    style_symbols = None
    if request is not None:
        manifest = getattr(request.app.state, "hedron_build_manifest", None)
        if manifest is not None:
            for sym in manifest.css_symbols:
                if "StatusBanner" in sym.component_id:
                    style_symbols = dict(sym.symbols)
                    break

    production = None
    if request is not None:
        production = getattr(request.app.state, "hedron_production", None)
    in_production = is_production_env(production=production)

    if style_symbols is not None:
        styles = module.load_styles(style_symbols)
    elif in_production:
        assert_runtime_compile_allowed(production=True, what="CSS")
        styles = module.load_styles()  # pragma: no cover
    else:
        styles = module.load_styles()

    python_banner = StatusBanner(label="0.18 train ready", tone="info")
    disclose = _HtmlTag("hedron-disclose")(
        html.p("Web Component disclose survives HTMX swaps."),
        **{"label": "About the reference app"},
    )
    return Stack(
        Heading("Typed component authoring", level=3),
        Text("Python components remain the canonical reusable component model."),
        python_banner,
        disclose,
        Text(f"Scoped root class: {styles.root}"),
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


def build_hedron_app(*, ensure_build: bool = True) -> Hedron:
    from pathlib import Path

    import hedron_core
    from hedron.build import run_build
    from hedron.config import HedronSettings
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

    ref_root = Path(__file__).resolve().parent
    build_dir = ref_root / ".hedron" / "build"
    if ensure_build:
        settings = HedronSettings(
            component_roots=("components",),
            build_dir=".hedron/build",
            theme="default",
        )
        run_build(project_dir=ref_root, settings=settings, production=True)

    app = Hedron(
        title="Hedron Team Admin",
        security="strict",
        explorer="development",
        session_secret="reference-app-secret",
        theme="default",
        build_dir=build_dir,
    )
    users = HedronRouter(prefix="/users", dependencies=[Depends(require_user)])

    @app.page("/")
    def home(request: Request, username: Annotated[str, Depends(require_user)]) -> Page:
        policy = getattr(request.app.state, "hedron_security", SecurityPolicy.from_name("strict"))
        token = csrf_token_for_request(request, policy)
        return dashboard_page(csrf_token=token, username=username, request=request)

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

    mount_phase05_routes(app)
    mount_phase06_routes(app)
    app.include_router(users)
    return app


def mount_phase06_routes(app: FastAPI) -> None:
    """Phase 0.6 chart + interaction demo routes."""
    from hedron.interaction import FragmentRegion, InteractionPolicy, InteractionResult, OobUpdate
    from hedron_charts import LineChart

    regions = (
        FragmentRegion(id="chart-region", selector="#chart-region", description="Chart panel"),
        FragmentRegion(id="oob-status", selector="#oob-status", description="OOB status"),
    )
    router = HedronRouter(prefix="/charts", dependencies=[Depends(require_user)])

    @router.component("/fragment", fragment_regions=regions)
    def chart_fragment() -> InteractionResult:
        chart = LineChart(
            [
                {"month": "Jan", "revenue": 10},
                {"month": "Feb", "revenue": 16},
                {"month": "Mar", "revenue": 22},
            ],
            x="month",
            y="revenue",
            title="Monthly revenue",
            description="Updated fragment chart.",
        )
        oob = html.div(Text("OOB status refreshed"), id="oob-status", **{"hx-swap-oob": "true"})
        return InteractionResult(
            content=chart,
            oob=(OobUpdate(content=oob),),
            policy=InteractionPolicy(declared_regions=regions, vary_on_target=True),
            cache="vary-htmx",
            explanation="Declared chart region with OOB status update",
        )

    @router.action("/search", method="POST")
    async def chart_search(
        request: Request,
        query: Annotated[str, Form()] = "",
    ) -> InteractionResult:
        rows = [
            {"month": "Jan", "revenue": 10},
            {"month": "Feb", "revenue": 14 if "feb" not in query.lower() else 20},
            {"month": "Mar", "revenue": 18},
        ]
        return InteractionResult(
            content=LineChart(
                rows,
                x="month",
                y="revenue",
                title="Search results",
                description=f"Filtered by {query or 'all'}.",
            ),
            policy=InteractionPolicy(declared_regions=regions, hx_sync="drop"),
            explanation="Synchronized search form submission",
        )

    app.include_router(router)


def mount_phase05_routes(app: FastAPI) -> None:
    """Shared 0.5 mutation/download/cache routes for Hedron and plain FastAPI builders."""

    @app.post("/color-mode")
    async def set_color_mode(
        request: Request,
        color_mode: Annotated[str, Form()] = "system",
        _: str = Depends(require_user),
    ) -> Any:
        from fastapi.responses import RedirectResponse

        policy = getattr(request.app.state, "hedron_security", SecurityPolicy.from_name("strict"))
        await prepare_csrf_from_request(request, policy)
        validate_csrf(request, policy)
        try:
            pref = ColorMode(color_mode)
        except ValueError:
            pref = ColorMode.SYSTEM
        response = RedirectResponse("/", status_code=303)
        apply_color_mode_cookie(response, pref)
        if hasattr(request, "session"):
            request.session["color_mode"] = pref.value
        return response

    @app.post("/employees/save")
    async def save_employees(
        request: Request,
        _: str = Depends(require_admin),
    ) -> dict[str, object]:
        from hedron_data import CellUpdate, filter_writable_changes

        policy = getattr(request.app.state, "hedron_security", SecurityPolicy.from_name("strict"))
        await prepare_csrf_from_request(request, policy)
        validate_csrf(request, policy)
        payload = await request.json()
        changes = DataChanges(
            updates=tuple(
                CellUpdate(
                    row_key=str(u["row_key"]),
                    field=str(u["field"]),
                    value=u.get("value"),
                    row_version=u.get("row_version"),
                )
                for u in payload.get("updates", [])
            ),
            inserts=tuple(payload.get("inserts", [])),
            deletes=tuple(str(d) for d in payload.get("deletes", [])),
            dataset_version=payload.get("dataset_version"),
        )
        cleaned, errors = filter_writable_changes(
            changes,
            writable_fields=frozenset({"name", "title", "active"}),
            read_only_fields=frozenset({"id"}),
            hidden_fields=frozenset(),
            allow_deletes=True,
            key_field="id",
        )
        if errors:
            return {
                "ok": False,
                "errors": [
                    {"row_key": e.row_key, "field": e.field, "message": e.message} for e in errors
                ],
                "conflicts": [],
            }
        result: DataSaveResult[dict[str, object]] = await ASYNC_EMPLOYEE_SOURCE.apply(cleaned)
        return {
            "ok": result.ok,
            "errors": [
                {"row_key": e.row_key, "field": e.field, "message": e.message}
                for e in result.errors
            ],
            "conflicts": [
                {
                    "row_key": c.row_key,
                    "field": c.field,
                    "server_value": c.server_value,
                    "client_value": c.client_value,
                    "message": c.message,
                }
                for c in result.conflicts
            ],
            "version": result.version,
        }

    @app.get("/downloads/roster.csv")
    async def download_roster(_: str = Depends(require_user)) -> Any:
        from fastapi.responses import Response

        page = EMPLOYEE_SOURCE.fetch(DataQuery(limit=100))
        table = DataTable(page=page, row_model=EmployeeRow)
        return Response(
            content=table.to_csv(),
            media_type="text/csv",
            headers={
                "Content-Disposition": 'attachment; filename="roster.csv"',
                "Cache-Control": "private, no-store",
            },
        )

    @app.get("/api/team-summary")
    async def team_summary(_: str = Depends(require_user)) -> dict[str, object]:
        return await load_team_summary(team_id=1)


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
        policy = getattr(request.app.state, "hedron_security", SecurityPolicy.from_name("standard"))
        token = csrf_token_for_request(request, policy)
        return dashboard_page(csrf_token=token, username=username, request=request)

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

    mount_phase05_routes(app)
    mount_phase06_routes(app)
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
