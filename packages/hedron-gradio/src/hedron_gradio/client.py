"""Gradio client protocol adapter (optional gradio_client at runtime)."""

from __future__ import annotations

import logging
import re
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any

from hedron_gradio.artifacts import ArtifactStore
from hedron_gradio.errors import GradioRemoteError
from hedron_gradio.jobs import GradioJobManager, job_scope_key
from hedron_gradio.policy import GradioRemoteConfig, redact_sensitive_text, validate_remote_url

_logger = logging.getLogger("hedron.gradio")
_GRADIO_CLIENT_IMPORT_ERROR = (
    "gradio_client is required for live Gradio discovery and predict calls. "
    "Install with: pip install gradio-client"
)

_VERSION_RE = re.compile(r"^(\d+)\.(\d+)(?:\.(\d+))?")

__all__ = [
    "GradioClientAdapter",
    "GradioEndpoint",
    "GradioRemoteError",
]


@dataclass(frozen=True)
class GradioEndpoint:
    name: str
    api_name: str
    parameters: Mapping[str, Any]
    supports_stream: bool = False


@dataclass
class GradioClientAdapter:
    """Disabled-by-default Gradio client interop adapter."""

    base_url: str
    auth_token: str | None = None
    supported_gradio_range: tuple[int, int] = (6, 22)
    enabled: bool = False
    endpoints: tuple[GradioEndpoint, ...] = ()
    gradio_version: str | None = None
    remote_config: GradioRemoteConfig | None = None
    tenant_id: str | None = None
    auth_subject: str | None = None
    _transport: Callable[..., Any] | None = field(default=None, repr=False)
    _offline: bool = field(default=False, repr=False)
    session_state: dict[str, Any] = field(default_factory=dict)
    _artifact_store: ArtifactStore | None = field(default=None, repr=False)
    _job_manager: GradioJobManager | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.remote_config is None and self.base_url.strip():
            object.__setattr__(
                self,
                "remote_config",
                GradioRemoteConfig.from_base_url(self.base_url),
            )
        if self._artifact_store is None and self.remote_config is not None:
            object.__setattr__(
                self,
                "_artifact_store",
                ArtifactStore(
                    max_bytes=self.remote_config.max_download_bytes,
                    retention_seconds=self.remote_config.artifact_retention_seconds,
                ),
            )
        if self._job_manager is None and self.remote_config is not None:
            object.__setattr__(
                self,
                "_job_manager",
                GradioJobManager(
                    default_timeout_seconds=self.remote_config.request_timeout_seconds
                ),
            )

    def consume_catalog(self, catalog: Any) -> tuple[str, ...]:
        """Read catalog facts. Catalog registration does not enable Gradio."""
        entries = getattr(catalog, "entries", {}) or {}
        return tuple(sorted(str(key) for key in entries))

    @property
    def scope_key(self) -> str:
        return job_scope_key(tenant_id=self.tenant_id, auth_subject=self.auth_subject)

    def discover(self) -> list[GradioEndpoint]:
        if not self.enabled:
            return []
        if self._offline:
            return []
        self._validate_base_url()
        if self.endpoints:
            return list(self.endpoints)
        if self._transport is not None:
            return self._discover_via_transport()
        return self._discover_via_gradio_client()

    def check_version_compat(self, version: str) -> None:
        major_floor, minor_ceiling = self.supported_gradio_range
        match = _VERSION_RE.match(version.strip())
        if match is None:
            raise GradioRemoteError(f"Unsupported Gradio version format: {version!r}")
        major = int(match.group(1))
        minor = int(match.group(2))
        minor_floor = 17
        if major != major_floor:
            raise GradioRemoteError(
                f"Gradio version {version} is outside supported major "
                f"{major_floor}.x (supported: {major_floor}.{minor_floor}+ "
                f"through {major_floor}.{minor_ceiling}.x)"
            )
        if minor < minor_floor or minor > minor_ceiling:
            raise GradioRemoteError(
                f"Gradio version {version} is outside supported range "
                f"{major_floor}.{minor_floor}+ through {major_floor}.{minor_ceiling}.x"
            )

    def predict(self, endpoint_name: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        self._require_enabled()
        self._validate_base_url()
        endpoint = self._resolve_endpoint(endpoint_name)
        if self._transport is not None:
            result = self._transport("predict", endpoint=endpoint, payload=dict(payload))
            if isinstance(result, dict):
                return result
            return {"result": result}
        if self.endpoints:
            return {"endpoint": endpoint.name, "payload": dict(payload), "status": "ok"}
        raise GradioRemoteError(_GRADIO_CLIENT_IMPORT_ERROR)

    def submit_job(self, endpoint_name: str, payload: Mapping[str, Any]) -> str:
        self._require_enabled()
        self._validate_base_url()
        endpoint = self._resolve_endpoint(endpoint_name)
        job_manager = self._require_job_manager()
        return job_manager.submit(
            endpoint.name,
            payload,
            scope_key=self.scope_key,
        )

    def job_status(self, job_id: str) -> dict[str, Any]:
        self._require_enabled()
        job_manager = self._require_job_manager()
        if self._transport is not None:
            job_manager.mark_running(job_id, scope_key=self.scope_key)
            raw = self._transport(
                "job_status",
                job_id=job_id,
                endpoint_name="",
                payload={},
            )
            if isinstance(raw, dict) and raw.get("status") == "complete":
                status = job_manager.complete(
                    job_id,
                    scope_key=self.scope_key,
                    result=dict(raw.get("result") or raw),
                )
                return status.as_dict()
        status = job_manager.poll(job_id, scope_key=self.scope_key)
        if status.status == "running" and self.endpoints:
            record = job_manager._get_scoped(job_id, self.scope_key)
            status = job_manager.complete(
                job_id,
                scope_key=self.scope_key,
                result={
                    "endpoint": record.endpoint_name,
                    "payload": dict(record.payload),
                    "status": "ok",
                },
            )
        return status.as_dict()

    def cancel_job(self, job_id: str) -> bool:
        self._require_enabled()
        job_manager = self._require_job_manager()
        if self._transport is not None:
            self._transport("cancel", job_id=job_id, endpoint_name="", payload={})
        return job_manager.cancel(job_id, scope_key=self.scope_key)

    def stream_results(
        self, endpoint_name: str, payload: Mapping[str, Any]
    ) -> Iterator[dict[str, Any]]:
        self._require_enabled()
        self._validate_base_url()
        endpoint = self._resolve_endpoint(endpoint_name)
        if not endpoint.supports_stream:
            raise GradioRemoteError(f"Endpoint {endpoint_name!r} does not support streaming")
        if self._transport is not None:
            chunks = self._transport("stream", endpoint=endpoint, payload=dict(payload))
            if isinstance(chunks, Iterator):
                yield from chunks
                return
            if isinstance(chunks, list):
                yield from chunks
                return
        yield {"endpoint": endpoint.name, "chunk": 0, "payload": dict(payload)}
        yield {"endpoint": endpoint.name, "chunk": 1, "done": True}

    def upload_file(self, name: str, data: bytes) -> str:
        self._require_enabled()
        self._validate_base_url()
        artifact_store = self._require_artifact_store()
        if self.remote_config is not None and len(data) > self.remote_config.max_upload_bytes:
            raise GradioRemoteError("Upload exceeds configured max_upload_bytes")
        return artifact_store.store(name, data, scope_key=self.scope_key)

    def download_artifact(self, artifact_id: str) -> bytes:
        self._require_enabled()
        return self._require_artifact_store().fetch(artifact_id, scope_key=self.scope_key)

    def close(self) -> None:
        if self._artifact_store is not None:
            self._artifact_store.clear()
        if self._job_manager is not None:
            self._job_manager.clear()

    def _validate_base_url(self) -> None:
        if self.remote_config is None:
            return
        validate_remote_url(self.base_url.strip(), self.remote_config, label="base_url")

    def _require_enabled(self) -> None:
        if not self.enabled:
            raise GradioRemoteError("GradioClientAdapter is disabled")

    def _require_job_manager(self) -> GradioJobManager:
        """Return the job manager or raise when remote_config/_job_manager was never set."""
        if self._job_manager is None:
            raise GradioRemoteError(
                "Gradio job manager is not configured; set remote_config or provide _job_manager"
            )
        return self._job_manager

    def _require_artifact_store(self) -> ArtifactStore:
        """Return the artifact store or raise when remote_config/_artifact_store was never set."""
        if self._artifact_store is None:
            raise GradioRemoteError(
                "Gradio artifact store is not configured; "
                "set remote_config or provide _artifact_store"
            )
        return self._artifact_store

    def _resolve_endpoint(self, endpoint_name: str) -> GradioEndpoint:
        for endpoint in self.endpoints:
            if endpoint.name == endpoint_name:
                return endpoint
        raise GradioRemoteError(f"Unknown endpoint: {endpoint_name}")

    def _discover_via_transport(self) -> list[GradioEndpoint]:
        if self._transport is None:
            return []
        result = self._transport("discover", base_url=self.base_url)
        if not isinstance(result, list):
            return []
        return [item for item in result if isinstance(item, GradioEndpoint)]

    def _discover_via_gradio_client(self) -> list[GradioEndpoint]:
        try:
            import gradio_client  # type: ignore[import-not-found]
            from gradio_client import Client  # type: ignore[import-not-found]
        except ImportError as exc:
            raise GradioRemoteError(_GRADIO_CLIENT_IMPORT_ERROR) from exc

        version = getattr(gradio_client, "__version__", None)
        if isinstance(version, str):
            self.check_version_compat(version)
            self.gradio_version = version

        try:
            client_kwargs: dict[str, Any] = {}
            if self.auth_token:
                client_kwargs["hf_token"] = self.auth_token
            client = Client(self.base_url, **client_kwargs)
        except Exception as exc:
            message = redact_sensitive_text(str(exc))
            raise GradioRemoteError(f"Failed to connect to Gradio app: {message}") from exc

        endpoints = self._endpoints_from_client(client)
        if not endpoints:
            raise GradioRemoteError(
                "Gradio client connected but no discoverable endpoints were found"
            )
        object.__setattr__(self, "endpoints", tuple(endpoints))
        return endpoints

    def _endpoints_from_client(self, client: Any) -> list[GradioEndpoint]:
        """Best-effort endpoint discovery across gradio_client view_api shapes."""
        info: Any = None
        for attr in ("view_api", "endpoints_info", "api_info"):
            candidate = getattr(client, attr, None)
            if callable(candidate):
                try:
                    info = candidate(return_format="dict") if attr == "view_api" else candidate()
                except TypeError:
                    try:
                        info = candidate()
                    except Exception as exc:  # noqa: BLE001
                        _logger.debug("Gradio endpoint probe %s() failed: %s", attr, exc)
                        continue
                except Exception as exc:  # noqa: BLE001
                    _logger.debug("Gradio endpoint probe %s failed: %s", attr, exc)
                    continue
                break
            if candidate is not None and not callable(candidate):
                info = candidate
                break
        if info is None:
            config = getattr(client, "config", None)
            if isinstance(config, Mapping):
                info = config

        named: dict[str, Any] = {}
        if isinstance(info, Mapping):
            for key in ("named_endpoints", "endpoints", "api"):
                block = info.get(key)
                if isinstance(block, Mapping):
                    named.update(dict(block))
            deps = info.get("dependencies")
            if isinstance(deps, list):
                for idx, dep in enumerate(deps):
                    if not isinstance(dep, Mapping):
                        continue
                    api_name = str(dep.get("api_name") or dep.get("name") or f"/fn_{idx}")
                    named[api_name] = dep
        elif isinstance(info, list):
            for idx, dep in enumerate(info):
                if isinstance(dep, Mapping):
                    api_name = str(dep.get("api_name") or dep.get("name") or f"/fn_{idx}")
                    named[api_name] = dep

        endpoints: list[GradioEndpoint] = []
        for api_name, meta in named.items():
            if not isinstance(meta, Mapping):
                continue
            name = str(meta.get("name") or api_name).lstrip("/")
            params = meta.get("parameters") or meta.get("inputs") or {}
            if not isinstance(params, Mapping):
                params = {"items": params}
            supports_stream = bool(
                meta.get("supports_stream")
                or meta.get("streaming")
                or "stream" in str(meta.get("type", "")).lower()
            )
            endpoints.append(
                GradioEndpoint(
                    name=name or str(api_name).lstrip("/"),
                    api_name=str(api_name),
                    parameters=dict(params),
                    supports_stream=supports_stream,
                )
            )
        return endpoints
