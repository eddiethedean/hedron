"""A Hedron application facade for Posit Workbench deployments."""

from __future__ import annotations

import ipaddress
from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Any
from urllib.parse import urlsplit

from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Receive, Scope, Send

from hedron import Hedron
from hedron.mount import cookie_path_for_mount, normalize_mount_path
from hedron_workbench.config import (
    DeploymentCapabilities,
    ResolvedDeployment,
    WorkbenchConfig,
    WorkbenchMode,
    WorkbenchTopology,
)
from hedron_workbench.middleware import WorkbenchPathMiddleware
from hedron_workbench.redact import redact_record, redact_text
from hedron_workbench.resolve import resolve_deployment
from hedron_workbench.urls import (
    ExternalBase,
    browser_mount_from_request,
    compose_external_url,
    connect_external_base_from_request,
    is_ephemeral_workbench_mount,
    local_href,
    mounted_redirect,
    validate_external_base_url,
)


class HedronWorkbench(Hedron):
    """``Hedron`` with Workbench mount and path handling built in.

    ``workbench`` is resolved without binding a port, executing ``rserver-url``,
    or importing any application code.  An explicit ``root_path`` still wins.
    Use ``hedron-workbench run`` when the deployment needs session-URL discovery
    before importing the application.
    """

    __hedron_workbench__ = True

    def __init__(
        self,
        *args: Any,
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
        config = workbench or WorkbenchConfig()
        config = replace(
            config,
            mode=(
                WorkbenchMode.parse(workbench_mode) if workbench_mode is not None else config.mode
            ),
            mount=workbench_mount if workbench_mount is not None else config.mount,
            public_base_url=(
                workbench_public_base_url
                if workbench_public_base_url is not None
                else config.public_base_url
            ),
            debug=workbench_debug if workbench_debug is not None else config.debug,
            topology=(
                WorkbenchTopology.parse(workbench_topology)
                if workbench_topology is not None
                else config.topology
            ),
        )
        # Broad compatibility aliases such as HOST/PORT/BASE_PATH belong to the
        # launcher. Ignoring them here keeps an inactive subclass byte-for-byte
        # compatible with ordinary Hedron on generic hosting platforms.
        self.hedron_workbench: ResolvedDeployment = resolve_deployment(
            config, compatibility_aliases=False
        )
        resolved_root_path = root_path
        if root_path is not None and self.hedron_workbench.active:
            root_resolution = resolve_deployment(
                replace(config, mount=root_path), compatibility_aliases=False
            )
            resolved_root_path = root_resolution.browser_mount
        if resolved_root_path is None and self.hedron_workbench.active:
            resolved_root_path = self.hedron_workbench.browser_mount or "/"

        super().__init__(*args, root_path=resolved_root_path, **kwargs)
        effective_mount = str(self.state.hedron_mount_path or "")
        if self.hedron_workbench.active and effective_mount != self.hedron_workbench.browser_mount:
            normalized = normalize_mount_path(effective_mount)
            self.hedron_workbench = replace(
                self.hedron_workbench,
                browser_mount=normalized,
                cookie_mount=cookie_path_for_mount(normalized),
                source="explicit:root_path"
                if root_path is not None
                else self.hedron_workbench.source,
            )
        self.state.hedron_workbench = self.hedron_workbench
        self.state.hedron_workbench_active = self.hedron_workbench.active
        # Give the normalizer FastAPI's ASGI implementation, rather than this
        # facade, to avoid re-entering this method after normalization.
        self._workbench_asgi = WorkbenchPathMiddleware(
            super().__call__,
            mode=self.hedron_workbench.mode,
            expected_mount=(
                self.hedron_workbench.browser_mount if self.hedron_workbench.active else None
            ),
            active=self.hedron_workbench.active,
            debug=self.hedron_workbench.debug,
            expected_origins=(self.hedron_workbench.external_origin,),
            runtime_mounts=True,
            mounted_response_headers=True,
            owned_cookie_names=self._owned_cookie_names(),
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Normalize Workbench scopes before FastAPI routes the request."""
        await self._workbench_asgi(scope, receive, send)

    def workbench_status(self) -> dict[str, object]:
        """Return a redacted, non-secret deployment diagnostic record."""
        payload = redact_record(self.hedron_workbench.as_dict())
        payload["app_mount"] = redact_text(str(self.state.hedron_mount_path or ""))
        payload["app_cookie_path"] = redact_text(str(self.state.hedron_cookie_path or "/"))
        payload["normalizer_count"] = 1
        return payload

    def _owned_cookie_names(self) -> tuple[str, ...]:
        names = {"session", "hedron_color_mode"}
        policy = getattr(self.state, "hedron_security", None)
        csrf_name = getattr(policy, "csrf_cookie_name", None)
        if isinstance(csrf_name, str) and csrf_name:
            names.add(csrf_name)
        return tuple(sorted(names))

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
            connect_base = connect_external_base_from_request(request)
            if connect_base is not None:
                return connect_base
        raise ValueError(
            "no trusted public base URL is available; configure external_base_url, "
            "run in Workbench, or pass a validated Posit Connect request"
        )

    def external_base(self, *, request: Request | None = None) -> ExternalBase:
        """Capture the validated immutable browser base for later/background use."""
        return self._external_base(request=request)

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

    def href(self, path: str, *, request: Request | None = None) -> str:
        """Prefix a local browser path once using construction or request mount."""
        mount = str(self.state.hedron_mount_path or "")
        if request is not None:
            mount = browser_mount_from_request(request)
        return local_href(path, mount=mount)

    def href_for(
        self,
        name: str,
        *,
        request: Request | None = None,
        **path_params: object,
    ) -> str:
        """Reverse a route name into a mount-aware local browser path."""
        return self.href(str(self.url_path_for(name, **path_params)), request=request)

    def redirect(
        self,
        path: str,
        *,
        request: Request | None = None,
        status_code: int = 303,
    ) -> Response:
        """Return a same-app redirect with automatic mount adaptation."""
        mount = str(self.state.hedron_mount_path or "")
        if request is not None:
            mount = browser_mount_from_request(request)
        return mounted_redirect(path, mount=mount, status_code=status_code)

    def redirect_for(
        self,
        name: str,
        *,
        request: Request | None = None,
        status_code: int = 303,
        **path_params: object,
    ) -> Response:
        """Reverse a route and return a mount-aware same-app redirect."""
        return self.redirect(
            str(self.url_path_for(name, **path_params)),
            request=request,
            status_code=status_code,
        )

    def deployment_capabilities(
        self,
        *,
        request: Request | None = None,
    ) -> DeploymentCapabilities:
        """Describe link and transport guarantees for the current deployment."""
        platform = "workbench" if self.hedron_workbench.active else "hedron"
        base: ExternalBase | None = None
        if request is not None and not self.hedron_workbench.active:
            base = connect_external_base_from_request(request)
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
