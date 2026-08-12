"""A Hedron application facade for Posit Workbench deployments."""

from __future__ import annotations

import ipaddress
from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Any
from urllib.parse import urlsplit

from starlette.requests import Request
from starlette.types import Receive, Scope, Send

from hedron import Hedron
from hedron.mount import cookie_path_for_mount, normalize_mount_path
from hedron_workbench.config import ResolvedDeployment, WorkbenchConfig, WorkbenchMode
from hedron_workbench.middleware import WorkbenchPathMiddleware
from hedron_workbench.redact import redact_record, redact_text
from hedron_workbench.resolve import resolve_deployment
from hedron_workbench.urls import (
    ExternalBase,
    compose_external_url,
    connect_external_base_from_request,
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

    def external_url(
        self,
        path: str,
        *,
        request: Request | None = None,
        query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
        fragment: str | None = None,
    ) -> str:
        """Build a stable public URL for email, OAuth, and background callbacks."""
        return compose_external_url(
            path,
            base=self._external_base(request=request),
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
