"""SessionAuthFlow: login/logout/session page plumbing (phase 0.58)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Generic, Literal, Protocol, TypeVar

from fastapi import Depends, Request
from pydantic import BaseModel

from hedron.app.form_commands import SafeLocalPath
from hedron.auth.session import mark_authenticated
from hedron.handles import ActionHandle
from hedron.security.auth_rate_limit import AuthRateLimiter, auth_rate_limit_dependency
from hedron.security.login_csrf import LOGIN_CSRF_KEY, validate_login_csrf
from hedron.security.redirects import redirect_local
from hedron_core.bundles import FeatureBundle, FeatureRequirement
from hedron_core.catalog import PackageProjection, ProjectionCapability
from hedron_core.codes import HED_AUTHFLOW_0001, HED_AUTHFLOW_0002, HED_AUTHFLOW_0003
from hedron_core.diagnostics import error
from hedron_core.htmx_contract import is_local_path

__all__ = [
    "AuthDenied",
    "AuthResult",
    "AuthSuccess",
    "RateLimitPolicy",
    "SessionAuthFlow",
    "SessionRotationPolicy",
]

CredentialsT = TypeVar("CredentialsT", bound=BaseModel)
PrincipalT = TypeVar("PrincipalT")
SessionT = TypeVar("SessionT")

SessionRotationPolicy = Literal["on_login", "never"]


class _AuthFlowApp(Protocol):
    """Minimal Hedron host surface for SessionAuthFlow materialization."""

    def screen(
        self,
        path: str,
        *,
        title: str,
        name: str | None = None,
    ) -> Callable[[Callable[..., object]], object]: ...

    def command(
        self,
        path: str,
        *,
        name: str | None = None,
        fallback: str | None = None,
        dependencies: Sequence[object] | None = None,
        outcomes: object | None = None,
    ) -> Callable[[Callable[..., object]], ActionHandle[Any, Any]]: ...


@dataclass(frozen=True, slots=True)
class RateLimitPolicy:
    """Explicit auth-endpoint rate limit (required for Supported production)."""

    limit: int = 10
    window_seconds: float = 60.0

    def __post_init__(self) -> None:
        if self.limit < 1:
            raise error(
                HED_AUTHFLOW_0001,
                title="Invalid rate limit",
                explanation="limit must be >= 1.",
                remediation="Pass RateLimitPolicy(limit=..., window_seconds=...).",
            )
        if self.window_seconds <= 0:
            raise error(
                HED_AUTHFLOW_0001,
                title="Invalid rate limit window",
                explanation="window_seconds must be > 0.",
                remediation="Pass a positive window_seconds.",
            )

    def to_limiter(self) -> AuthRateLimiter:
        return AuthRateLimiter(limit=self.limit, window_seconds=self.window_seconds)


@dataclass(frozen=True, slots=True)
class AuthSuccess(Generic[PrincipalT]):
    """Closed authentication success result."""

    principal: PrincipalT
    kind: Literal["success"] = "success"


@dataclass(frozen=True, slots=True)
class AuthDenied:
    """Closed authentication denial (generic; no enumeration detail)."""

    kind: Literal["denied"] = "denied"


AuthResult = AuthSuccess[PrincipalT] | AuthDenied


class SessionAuthFlow(Generic[CredentialsT, PrincipalT, SessionT]):
    """Compose login/logout surfaces around explicit identity callbacks."""

    def __init__(
        self,
        credentials: type[CredentialsT],
        authenticate: Callable[[CredentialsT], AuthSuccess[PrincipalT] | AuthDenied],
        serialize_principal: Callable[[PrincipalT], SessionT],
        load_principal: Callable[[SessionT], PrincipalT | None],
        *,
        login_path: str = "/login",
        logout_path: str = "/logout",
        after_login: SafeLocalPath = "/",
        rate_limit: RateLimitPolicy,
        rotation: SessionRotationPolicy = "on_login",
        session_key: str = "user",
        provider: str = "hedron",
        provider_version: str = "0.58.0",
    ) -> None:
        if not is_local_path(after_login):
            raise error(
                HED_AUTHFLOW_0001,
                title="Unsafe after_login path",
                explanation=f"after_login={after_login!r} is not a safe local path.",
                remediation="Use a path starting with '/' and no scheme/host.",
            )
        if rotation not in {"on_login", "never"}:
            raise error(
                HED_AUTHFLOW_0001,
                title="Invalid session rotation policy",
                explanation=f"rotation={rotation!r} is unsupported.",
                remediation="Use 'on_login' or 'never'.",
            )
        self.credentials = credentials
        self.authenticate = authenticate
        self.serialize_principal = serialize_principal
        self.load_principal = load_principal
        self.login_path = login_path
        self.logout_path = logout_path
        self.after_login = after_login
        self.rate_limit = rate_limit
        self.rotation = rotation
        self.session_key = session_key
        self.provider = provider
        self.provider_version = provider_version
        self._limiter = rate_limit.to_limiter()
        self.login_screen: object | None = None
        self.login_command: object | None = None
        self.login_form: object | None = None
        self.logout_command: object | None = None

    def current_principal(self) -> Callable[..., PrincipalT | None]:
        """FastAPI dependency that loads the principal from the session."""
        flow = self

        def _dependency(request: Request) -> PrincipalT | None:
            session = getattr(request, "session", None)
            if session is None:
                return None
            get = getattr(session, "get", None)
            if not callable(get):
                return None
            stored = get(flow.session_key)
            if stored is None:
                return None
            try:
                return flow.load_principal(stored)  # type: ignore[arg-type]
            except Exception:  # noqa: BLE001
                return None

        return _dependency

    def _rotate_session(self, request: object) -> None:
        if self.rotation != "on_login":
            return
        session = getattr(request, "session", None)
        if session is None:
            raise error(
                HED_AUTHFLOW_0003,
                title="Session rotation unavailable",
                explanation="rotation='on_login' requires a mutable request session.",
                remediation="Enable Hedron sessions or set rotation='never'.",
            )
        clear = getattr(session, "clear", None)
        if not callable(clear):
            raise error(
                HED_AUTHFLOW_0003,
                title="Session rotation unavailable",
                explanation="rotation='on_login' requires session.clear().",
                remediation="Use a session backend that supports clear(), or set rotation='never'.",
            )
        csrf = None
        get = getattr(session, "get", None)
        if callable(get):
            csrf = get(LOGIN_CSRF_KEY)
        clear()
        if csrf is not None and hasattr(session, "__setitem__"):
            session[LOGIN_CSRF_KEY] = csrf

    def to_bundle(self) -> FeatureBundle:
        flow = self
        rate_dep = Depends(auth_rate_limit_dependency(flow._limiter))

        def _ensure_login_command(app: _AuthFlowApp) -> ActionHandle[Any, Any]:
            if flow.login_command is not None:
                return flow.login_command  # type: ignore[return-value]

            from hedron.app.form_commands import form_command

            credentials_model = flow.credentials

            async def login_command(data: CredentialsT, request: Request) -> object:
                session = request.session
                form = await request.form()
                raw = form.get(LOGIN_CSRF_KEY)
                token = str(raw) if isinstance(raw, str) else None
                # Fail closed: login CSRF is required (router CSRF is separate).
                validate_login_csrf(token, session=session)
                try:
                    outcome = flow.authenticate(data)
                except Exception as exc:
                    raise error(
                        HED_AUTHFLOW_0002,
                        title="Authentication failed",
                        explanation="authenticate() raised; details are not disclosed.",
                        remediation="Return AuthSuccess/AuthDenied from authenticate.",
                    ) from exc
                if isinstance(outcome, AuthDenied):
                    raise error(
                        HED_AUTHFLOW_0002,
                        title="Authentication failed",
                        explanation="Credentials were not accepted.",
                        remediation="Check credentials and try again.",
                    )
                try:
                    encoded = flow.serialize_principal(outcome.principal)
                except Exception as exc:
                    raise error(
                        HED_AUTHFLOW_0003,
                        title="Session serialization failed",
                        explanation="serialize_principal() failed.",
                        remediation="Return a bounded session reference value.",
                    ) from exc
                flow._rotate_session(request)
                session[flow.session_key] = encoded
                mark_authenticated(request, value=True)
                return redirect_local(flow.after_login)

            login_command.__annotations__ = {
                "data": credentials_model,
                "request": Request,
                "return": object,
            }
            login_handle = form_command(
                app,
                flow.login_path,
                name=f"{flow.provider}-login-command",
                fallback=flow.login_path,
                dependencies=(rate_dep,),
            )(login_command)

            flow.login_command = login_handle
            flow.login_form = login_handle.form
            return login_handle

        def login_screen_factory(app: _AuthFlowApp) -> object:
            from hedron import Form, LoginCsrfField, Stack, Text

            login_handle = _ensure_login_command(app)

            @app.screen(flow.login_path, title="Sign in", name=f"{flow.provider}-login")
            def login_screen(request: Request) -> object:
                generated = login_handle.form(submit_label="Sign in")
                children = list(getattr(generated, "_children", ()) or ())
                html_attrs = dict(getattr(generated, "_html_attrs", {}) or {})
                return Stack(
                    Text("Sign in"),
                    Form(
                        LoginCsrfField(session=request.session),
                        *children,
                        action=login_handle,
                        method="post",
                        **html_attrs,
                    ),
                )

            flow.login_screen = login_screen
            return login_screen

        def login_command_factory(app: _AuthFlowApp) -> object:
            return _ensure_login_command(app)

        def logout_command_factory(app: _AuthFlowApp) -> object:
            @app.command(flow.logout_path, name=f"{flow.provider}-logout", fallback="/")
            def logout_command(request: Request) -> object:
                session = request.session
                clear = getattr(session, "clear", None)
                if callable(clear):
                    clear()
                mark_authenticated(request, value=False)
                return redirect_local("/")

            flow.logout_command = logout_command
            return logout_command

        projection = PackageProjection(
            namespace="hedron.auth.session_flow",
            provider=self.provider,
            provider_version=self.provider_version,
            capabilities=(ProjectionCapability(name="SessionAuthFlow", support="supported"),),
            data={
                "login_path": self.login_path,
                "logout_path": self.logout_path,
                "rotation": self.rotation,
                "surfaces": [
                    "login_screen",
                    "login_command",
                    "login_form",
                    "logout_command",
                ],
            },
            limitations=("no IdP/user DB/roles; application owns authenticate/serialize/load",),
        )
        return FeatureBundle(
            logical_id=f"{self.provider}:session-auth",
            provider=self.provider,
            provider_version=self.provider_version,
            views=(login_screen_factory,),
            commands=(login_command_factory, logout_command_factory),
            projections=(projection,),
            requirements=(FeatureRequirement(name="hedron", required=True),),
            limitations=("session plumbing only; authorization stays on route dependencies",),
        )
