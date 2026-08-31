"""A Hedron application facade for Posit Workbench / Connect deployments."""

from __future__ import annotations

import ipaddress
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from typing import Any
from urllib.parse import urlsplit

from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.types import Receive, Scope, Send

from hedron import Hedron
from hedron.mount import cookie_path_for_mount, normalize_mount_path
from hedron_posit.config import (
    ConnectConfig,
    DeploymentCapabilities,
    PositConfig,
    PositStatus,
    ResolvedDeployment,
    ResolvedPositDeployment,
    WorkbenchConfig,
    WorkbenchMode,
    WorkbenchTopology,
    resolve_posit_deployment,
)
from hedron_posit.connect import native_connect_base_from_request
from hedron_posit.cookies import ConnectCookieMode, CookieRegistry, CookieSpec
from hedron_posit.detect import truthy
from hedron_posit.middleware import WorkbenchPathMiddleware
from hedron_posit.products import PositProduct
from hedron_posit.redact import redact_record, redact_text
from hedron_posit.urls import (
    ExternalBase,
    browser_mount_from_request,
    compose_external_url,
    is_ephemeral_workbench_mount,
    local_href,
    mounted_redirect,
    validate_external_base_url,
)


class HedronPosit(Hedron):
    """``Hedron`` with Posit Workbench / Connect deployment handling built in.

    ``posit`` is resolved without binding a port, executing ``rserver-url``,
    or importing any application code.  An explicit ``root_path`` still wins.
    Use ``hedron-posit run`` when the deployment needs session-URL discovery
    before importing the application.
    """

    __hedron_posit__ = True

    def __init__(
        self,
        *args: Any,
        posit: PositConfig | None = None,
        workbench: WorkbenchConfig | None = None,
        workbench_mode: WorkbenchMode | str | None = None,
        workbench_mount: str | None = None,
        workbench_public_base_url: str | None = None,
        workbench_debug: bool | None = None,
        workbench_topology: WorkbenchTopology | str | None = None,
        external_base_url: str | None = None,
        root_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._hedron_external_base = (
            validate_external_base_url(external_base_url) if external_base_url is not None else None
        )
        workbench_config = workbench or (
            posit.workbench if posit is not None else WorkbenchConfig()
        )
        workbench_config = replace(
            workbench_config,
            mode=(
                WorkbenchMode.parse(workbench_mode)
                if workbench_mode is not None
                else workbench_config.mode
            ),
            mount=workbench_mount if workbench_mount is not None else workbench_config.mount,
            public_base_url=(
                workbench_public_base_url
                if workbench_public_base_url is not None
                else workbench_config.public_base_url
            ),
            debug=workbench_debug if workbench_debug is not None else workbench_config.debug,
            topology=(
                WorkbenchTopology.parse(workbench_topology)
                if workbench_topology is not None
                else workbench_config.topology
            ),
        )
        connect_config = posit.connect if posit is not None else ConnectConfig()
        if posit is None:
            cookie_mode = os.environ.get("HEDRON_POSIT_CONNECT_COOKIE_MODE")
            if cookie_mode:
                connect_config = replace(
                    connect_config,
                    cookie_mode=ConnectCookieMode.parse(cookie_mode),
                )
        posit_config = PositConfig(
            product=posit.product if posit is not None else PositProduct.AUTO,
            workbench=workbench_config,
            connect=connect_config,
            hands_off=(
                bool(posit.hands_off)
                if posit is not None
                else truthy(os.environ.get("HEDRON_POSIT_HANDS_OFF"))
            ),
        )
        self._posit_config = posit_config
        self._cookie_registry: CookieRegistry | None = None
        # Broad compatibility aliases such as HOST/PORT/BASE_PATH belong to the
        # launcher. Ignoring them here keeps an inactive subclass byte-for-byte
        # compatible with ordinary Hedron on generic hosting platforms.
        resolved_posit = resolve_posit_deployment(
            posit_config,
            compatibility_aliases=False,
            compatibility_facade=bool(getattr(type(self), "__hedron_workbench__", False)),
        )
        self.hedron_posit: ResolvedPositDeployment = resolved_posit
        self.hedron_workbench: ResolvedDeployment = resolved_posit.workbench
        resolved_root_path = root_path
        if root_path is not None and self.hedron_workbench.active:
            root_resolution = resolve_posit_deployment(
                replace(
                    posit_config,
                    workbench=replace(posit_config.workbench, mount=root_path),
                ),
                compatibility_aliases=False,
                compatibility_facade=resolved_posit.compatibility_facade,
            )
            resolved_root_path = root_resolution.workbench.browser_mount
        if resolved_root_path is None and self.hedron_workbench.active:
            resolved_root_path = self.hedron_workbench.browser_mount or "/"

        super().__init__(*args, root_path=resolved_root_path, **kwargs)
        effective_mount = str(self.state.hedron_mount_path or "")
        if self.hedron_workbench.active and effective_mount != self.hedron_workbench.browser_mount:
            normalized = normalize_mount_path(effective_mount)
            updated_wb = replace(
                self.hedron_workbench,
                browser_mount=normalized,
                cookie_mount=cookie_path_for_mount(normalized),
                source="explicit:root_path"
                if root_path is not None
                else self.hedron_workbench.source,
            )
            self.hedron_workbench = updated_wb
            self.hedron_posit = replace(self.hedron_posit, workbench=updated_wb)
        self.state.hedron_workbench = self.hedron_workbench
        self.state.hedron_workbench_active = self.hedron_workbench.active
        self.state.hedron_posit = self.hedron_posit
        self.state.hedron_posit_hands_off = bool(self._posit_config.hands_off)
        # Give the normalizer FastAPI's ASGI implementation, rather than this
        # facade, to avoid re-entering this method after normalization.
        # hands_off (#510) opts into the same validated same-app Location/HTMX/
        # owned-cookie Path adaptation without requiring Workbench detection.
        hands_off = bool(self._posit_config.hands_off)
        hands_off_mount = ""
        if hands_off and not self.hedron_workbench.active:
            hands_off_mount = normalize_mount_path(
                str(resolved_root_path or getattr(self.state, "hedron_mount_path", "") or "")
            )
        expected_mount = (
            self.hedron_workbench.browser_mount
            if self.hedron_workbench.active
            else (hands_off_mount or None)
        )
        # hands_off must not stay stuck in WorkbenchMode.OFF: request mount strip
        # and response adaptation both need _should_normalize to admit the mount.
        middleware_mode = self.hedron_workbench.mode
        if hands_off and expected_mount and middleware_mode is WorkbenchMode.OFF:
            middleware_mode = WorkbenchMode.AUTO
        absolute_origin = self._workbench_absolute_redirect_origin()
        self._workbench_asgi = WorkbenchPathMiddleware(
            super().__call__,
            mode=middleware_mode,
            expected_mount=expected_mount,
            active=self.hedron_workbench.active or bool(hands_off and expected_mount),
            debug=self.hedron_workbench.debug,
            expected_origins=(self.hedron_workbench.external_origin,),
            runtime_mounts=bool(self.hedron_workbench.active or (hands_off and expected_mount)),
            mounted_response_headers=True,
            absolute_redirects=absolute_origin is not None,
            absolute_origin=absolute_origin,
            owned_cookie_names=self._owned_cookie_names(),
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Normalize Workbench scopes before FastAPI routes the request."""
        if scope.get("type") == "http" and self.hedron_posit.product is PositProduct.CONNECT:
            # Validate Connect's base/root contract at request ingress. Without
            # this, a malformed base header can survive ordinary requests and
            # fail only when an application later asks for a URL helper.
            native_connect_base_from_request(
                Request(scope),
                product=self.hedron_posit.product,
                trusted_peers=self._posit_config.connect.trusted_peers,
            )
        await self._workbench_asgi(scope, receive, send)

    def workbench_status(self) -> dict[str, object]:
        """Return a redacted, non-secret Workbench deployment diagnostic record."""
        payload = redact_record(self.hedron_workbench.as_dict())
        payload["app_mount"] = redact_text(str(self.state.hedron_mount_path or ""))
        payload["app_cookie_path"] = redact_text(str(self.state.hedron_cookie_path or "/"))
        payload["normalizer_count"] = 1
        return payload

    def posit_status(self) -> PositStatus:
        """Return a typed, secret-free Posit deployment status record."""
        caps = self.deployment_capabilities()
        return PositStatus(
            product=self.hedron_posit.product,
            evidence=self.hedron_posit.evidence,
            mount_source=str(self.hedron_workbench.source or self.hedron_posit.evidence),
            browser_mount=redact_text(
                str(self.hedron_workbench.browser_mount or self.state.hedron_mount_path or "")
            ),
            cookie_strategy=self.hedron_posit.cookie_mode.value,
            bridge_enabled=self.hedron_posit.bridge_enabled,
            registered_cookie_count=len(
                {
                    *self._owned_cookie_names(),
                    *(self._cookie_registry.names() if self._cookie_registry else ()),
                }
            ),
            normalizer_count=1,
            compatibility_facade=self.hedron_posit.compatibility_facade,
            capabilities=caps,
        )

    def _owned_cookie_names(self) -> tuple[str, ...]:
        names = {"session", "hedron_color_mode"}
        names.update(self._posit_config.connect.owned_cookie_names)
        policy = getattr(self.state, "hedron_security", None)
        csrf_name = getattr(policy, "csrf_cookie_name", None)
        if isinstance(csrf_name, str) and csrf_name:
            names.add(csrf_name)
        return tuple(sorted(names))

    def _refresh_owned_cookie_middleware(self) -> None:
        """Keep response Path repair in sync with late cookie registration (#508)."""
        registry_names = self._cookie_registry.names() if self._cookie_registry else ()
        owned = tuple(sorted({*self._owned_cookie_names(), *registry_names}))
        setter = getattr(self._workbench_asgi, "set_owned_cookie_names", None)
        if callable(setter):
            setter(owned)
        else:
            self._workbench_asgi.owned_cookie_names = frozenset(owned)

    @property
    def cookies(self) -> CookieRegistry:
        """Deployment-aware cookie registry (set/delete share one Path)."""
        if self._cookie_registry is None:
            self._cookie_registry = CookieRegistry(self)
        return self._cookie_registry

    def register_cookie(self, spec: CookieSpec) -> None:
        """Register an application cookie for lifecycle management."""
        self.cookies.register(spec)

    def _connect_base(self, request: Request) -> ExternalBase | None:
        return native_connect_base_from_request(
            request,
            product=self.hedron_posit.product,
            trusted_peers=self._posit_config.connect.trusted_peers,
        )

    def _workbench_absolute_redirect_origin(self) -> str | None:
        """Return a trusted origin for Workbench-safe absolute redirects.

        Workbench discovery and explicit configuration are trusted deployment
        inputs. A loopback origin is not safe for browser redirects because it
        points users at the local listener rather than the public proxy.
        """
        if not self.hedron_workbench.active:
            return None
        hostname = urlsplit(self.hedron_workbench.external_origin).hostname or ""
        try:
            loopback = ipaddress.ip_address(hostname).is_loopback
        except ValueError:
            loopback = hostname.lower() == "localhost"
        return None if loopback else self.hedron_workbench.external_origin

    def _external_base(self, *, request: Request | None = None) -> ExternalBase:
        if self._hedron_external_base is not None:
            return self._hedron_external_base
        if self.hedron_workbench.active:
            hostname = urlsplit(self.hedron_workbench.external_origin).hostname or ""
            try:
                loopback_origin = ipaddress.ip_address(hostname).is_loopback
            except ValueError:
                loopback_origin = hostname.lower() == "localhost"
            if loopback_origin:
                raise ValueError(
                    "Workbench resolved only a loopback origin; configure "
                    "workbench_public_base_url or external_base_url for public links"
                )
            return ExternalBase(
                origin=self.hedron_workbench.external_origin,
                mount=self.hedron_workbench.browser_mount,
                source=self.hedron_workbench.source,
            )
        if request is not None:
            connect_base = self._connect_base(request)
            if connect_base is not None:
                return connect_base
        raise ValueError(
            "no trusted public base URL is available; configure external_base_url, "
            "run in Workbench, or pass a validated Posit Connect request"
        )

    def external_base(self, *, request: Request | None = None) -> ExternalBase:
        """Capture the validated immutable browser base for later/background use."""
        return self._external_base(request=request)

    def _absolute_redirect_base(self, *, request: Request | None = None) -> ExternalBase:
        """Return the trusted deployment base used by scheme-absolute redirects."""
        if self._hedron_external_base is not None:
            return self._hedron_external_base
        if self.hedron_workbench.active:
            return ExternalBase(
                origin=self.hedron_workbench.external_origin,
                mount=self.hedron_workbench.browser_mount,
                source=self.hedron_workbench.source,
            )
        if request is not None:
            connect_base = self._connect_base(request)
            if connect_base is not None:
                return connect_base
        raise ValueError(
            "no trusted public base URL is available for an absolute redirect; "
            "configure external_base_url, run in Workbench, or pass a validated "
            "Posit Connect request"
        )

    def _durable_external_base(self, *, request: Request | None = None) -> ExternalBase:
        base = self._external_base(request=request)
        if is_ephemeral_workbench_mount(base.mount):
            raise ValueError(
                "Posit Workbench session URLs are ephemeral and cannot be used for "
                "email, OAuth, or durable callbacks; configure external_base_url to "
                "a stable deployment (typically Posit Connect)"
            )
        return base

    def browser_url(
        self,
        path: str,
        *,
        request: Request | None = None,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
    ) -> str:
        """Build a URL usable in the current interactive browser session."""
        return compose_external_url(
            path,
            base=self._external_base(request=request),
            query=query,
            fragment=fragment,
        )

    def browser_url_for(
        self,
        name: str,
        *,
        request: Request | None = None,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
        **path_params: object,
    ) -> str:
        """Reverse a route name for the current interactive browser session."""
        path = str(self.url_path_for(name, **path_params))
        return self.browser_url(path, request=request, query=query, fragment=fragment)

    def external_url(
        self,
        path: str,
        *,
        request: Request | None = None,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
    ) -> str:
        """Build a durable public URL for email, OAuth, and background callbacks."""
        return compose_external_url(
            path,
            base=self._durable_external_base(request=request),
            query=query,
            fragment=fragment,
        )

    def external_url_for(
        self,
        name: str,
        *,
        request: Request | None = None,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
        **path_params: object,
    ) -> str:
        """Reverse a route name and build its stable public URL."""
        path = str(self.url_path_for(name, **path_params))
        return self.external_url(path, request=request, query=query, fragment=fragment)

    durable_url = external_url
    durable_url_for = external_url_for

    def href(
        self,
        path: str,
        *,
        request: Request | None = None,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
    ) -> str:
        """Prefix a local browser path once using construction or request mount."""
        mount = str(self.state.hedron_mount_path or "")
        if request is not None:
            mount = browser_mount_from_request(request)
        return local_href(path, mount=mount, query=query, fragment=fragment)

    def href_for(
        self,
        name: str,
        *,
        request: Request | None = None,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
        **path_params: object,
    ) -> str:
        """Reverse a route name into a mount-aware local browser path."""
        return self.href(
            str(self.url_path_for(name, **path_params)),
            request=request,
            query=query,
            fragment=fragment,
        )

    def redirect(
        self,
        path: str,
        *,
        request: Request | None = None,
        status_code: int = 303,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
        absolute: bool = False,
    ) -> Response:
        """Return a same-app redirect with automatic mount adaptation.

        Set ``absolute=True`` for a scheme-absolute ``Location`` built from the
        trusted Workbench / Connect / configured deployment base. This is useful
        when an outer Workbench proxy rewrites path-absolute Location headers.
        """
        if absolute:
            target = compose_external_url(
                path,
                base=self._absolute_redirect_base(request=request),
                query=query,
                fragment=fragment,
            )
            return RedirectResponse(url=target, status_code=status_code)
        mount = str(self.state.hedron_mount_path or "")
        if request is not None:
            mount = browser_mount_from_request(request)
        return mounted_redirect(
            path,
            mount=mount,
            status_code=status_code,
            query=query,
            fragment=fragment,
        )

    def redirect_for(
        self,
        name: str,
        *,
        request: Request | None = None,
        status_code: int = 303,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
        absolute: bool = False,
        **path_params: object,
    ) -> Response:
        """Reverse a route and return a mount-aware same-app redirect."""
        return self.redirect(
            str(self.url_path_for(name, **path_params)),
            request=request,
            status_code=status_code,
            query=query,
            fragment=fragment,
            absolute=absolute,
        )

    def browser_redirect(
        self,
        path: str,
        *,
        request: Request | None = None,
        status_code: int = 303,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
    ) -> Response:
        """Return a scheme-absolute redirect for the current deployment."""
        return self.redirect(
            path,
            request=request,
            status_code=status_code,
            query=query,
            fragment=fragment,
            absolute=True,
        )

    def browser_redirect_for(
        self,
        name: str,
        *,
        request: Request | None = None,
        status_code: int = 303,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
        **path_params: object,
    ) -> Response:
        """Reverse a route into a scheme-absolute current-deployment redirect."""
        return self.redirect_for(
            name,
            request=request,
            status_code=status_code,
            query=query,
            fragment=fragment,
            absolute=True,
            **path_params,
        )

    def posit_for(self, request: Request) -> PositContext:
        """Return a request-bound context for links, redirects, cookies, and capabilities."""
        return PositContext(app=self, request=request)

    @property
    def hands_off(self) -> bool:
        """Whether opt-in hands-off local URL adaptation is enabled."""
        return bool(self._posit_config.hands_off)

    def adapt_local_url(self, path: str, *, request: Request | None = None) -> str:
        """Prefix a validated same-app path once (same helper as ``href``).

        Middleware response rewriting (``Location`` / HTMX / owned cookies) is
        gated by ``hands_off`` or an active Workbench mount. This helper always
        builds a correctly mounted path for authors who call it explicitly.
        """
        return self.href(path, request=request)

    def deployment_capabilities(
        self,
        *,
        request: Request | None = None,
    ) -> DeploymentCapabilities:
        """Describe link and transport guarantees for the current deployment."""
        if self.hedron_posit.product is PositProduct.CONNECT:
            platform = "connect"
        elif self.hedron_workbench.active:
            platform = "workbench"
        else:
            platform = "hedron"
        base: ExternalBase | None = None
        if request is not None and not self.hedron_workbench.active:
            base = self._connect_base(request)
            if base is not None:
                platform = "connect"
        if base is None:
            try:
                base = self._external_base(request=request)
            except ValueError:
                base = None
        ephemeral = bool(base and base.ephemeral)
        durable = base is not None and not ephemeral
        notes: list[str] = []
        if ephemeral:
            notes.append("session may be suspended, killed, or replaced")
        if base is None:
            notes.append("no trusted public base URL is available")
        if self.hedron_posit.cookie_mode is not ConnectCookieMode.NATIVE:
            notes.append("non-native Connect cookie mode selected")
        if self.hedron_workbench.topology is WorkbenchTopology.REVERSE_PROXY:
            notes.append("load-balanced deployments require Workbench session stickiness")
        if self.hedron_workbench.topology in {
            WorkbenchTopology.LAUNCHER_KUBERNETES,
            WorkbenchTopology.LAUNCHER_SLURM,
        }:
            notes.append("launcher network policy must allow Workbench to reach the app listener")
        return DeploymentCapabilities(
            platform=platform,
            topology=self.hedron_workbench.topology,
            mounted=bool(base and base.mount),
            browser_links=base is not None,
            durable_links=durable,
            background_links=durable,
            websockets=True,
            ephemeral_session=ephemeral,
            notes=tuple(notes),
        )


@dataclass(frozen=True, slots=True)
class PositContext:
    """Request-bound HedronPosit helpers (links, redirects, cookies, capabilities)."""

    app: HedronPosit
    request: Request

    def __post_init__(self) -> None:
        bound = getattr(self.request, "app", None)
        if bound is not None and bound is not self.app:
            raise ValueError("request does not belong to the expected HedronPosit application")

    def href(
        self,
        path: str,
        *,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
    ) -> str:
        return self.app.href(path, request=self.request, query=query, fragment=fragment)

    def href_for(
        self,
        name: str,
        *,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
        **path_params: object,
    ) -> str:
        return self.app.href_for(
            name,
            request=self.request,
            query=query,
            fragment=fragment,
            **path_params,
        )

    def redirect(
        self,
        path: str,
        *,
        status_code: int = 303,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
        absolute: bool = False,
    ) -> Response:
        return self.app.redirect(
            path,
            request=self.request,
            status_code=status_code,
            query=query,
            fragment=fragment,
            absolute=absolute,
        )

    def redirect_for(
        self,
        name: str,
        *,
        status_code: int = 303,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
        absolute: bool = False,
        **path_params: object,
    ) -> Response:
        return self.app.redirect_for(
            name,
            request=self.request,
            status_code=status_code,
            query=query,
            fragment=fragment,
            absolute=absolute,
            **path_params,
        )

    def browser_redirect(
        self,
        path: str,
        *,
        status_code: int = 303,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
    ) -> Response:
        return self.app.browser_redirect(
            path,
            request=self.request,
            status_code=status_code,
            query=query,
            fragment=fragment,
        )

    def browser_redirect_for(
        self,
        name: str,
        *,
        status_code: int = 303,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
        **path_params: object,
    ) -> Response:
        return self.app.browser_redirect_for(
            name,
            request=self.request,
            status_code=status_code,
            query=query,
            fragment=fragment,
            **path_params,
        )

    def browser_url(
        self,
        path: str,
        *,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
    ) -> str:
        return self.app.browser_url(path, request=self.request, query=query, fragment=fragment)

    def durable_url(
        self,
        path: str,
        *,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
    ) -> str:
        return self.app.durable_url(path, request=self.request, query=query, fragment=fragment)

    def capabilities(self) -> DeploymentCapabilities:
        return self.app.deployment_capabilities(request=self.request)

    @property
    def cookies(self) -> CookieRegistry:
        return self.app.cookies
