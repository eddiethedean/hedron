"""Gradio client protocol adapter (optional gradio_client at runtime)."""

from __future__ import annotations

import logging
import re
import uuid
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any

_logger = logging.getLogger("hedron.gradio")
_GRADIO_CLIENT_IMPORT_ERROR = (
    "gradio_client is required for live Gradio discovery and predict calls. "
    "Install with: pip install gradio-client"
)

_VERSION_RE = re.compile(r"^(\d+)\.(\d+)(?:\.(\d+))?")


class GradioRemoteError(Exception):
    """Raised when a remote Gradio call or version check fails."""


@dataclass(frozen=True)
class GradioEndpoint:
    name: str
    api_name: str
    parameters: Mapping[str, Any]
    supports_stream: bool = False


@dataclass
class _JobRecord:
    endpoint_name: str
    payload: Mapping[str, Any]
    status: str = "pending"
    result: dict[str, Any] | None = None


@dataclass
class GradioClientAdapter:
    """Disabled-by-default Gradio client interop adapter."""

    base_url: str
    auth_token: str | None = None
    supported_gradio_range: tuple[int, int] = (6, 22)
    enabled: bool = False
    endpoints: tuple[GradioEndpoint, ...] = ()
    gradio_version: str | None = None
    _transport: Callable[..., Any] | None = field(default=None, repr=False)
    _offline: bool = field(default=False, repr=False)
    session_state: dict[str, Any] = field(default_factory=dict)
    _files: dict[str, bytes] = field(default_factory=dict, repr=False)
    _jobs: dict[str, _JobRecord] = field(default_factory=dict, repr=False)

    def discover(self) -> list[GradioEndpoint]:
        if not self.enabled:
            return []
        if self._offline:
            return []
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
        endpoint = self._resolve_endpoint(endpoint_name)
        job_id = uuid.uuid4().hex
        self._jobs[job_id] = _JobRecord(endpoint_name=endpoint.name, payload=dict(payload))
        return job_id

    def job_status(self, job_id: str) -> dict[str, Any]:
        self._require_enabled()
        record = self._jobs.get(job_id)
        if record is None:
            raise GradioRemoteError(f"Unknown job id: {job_id}")
        if record.status == "pending":
            record.status = "complete"
            record.result = {
                "endpoint": record.endpoint_name,
                "payload": record.payload,
                "status": "ok",
            }
        return {"job_id": job_id, "status": record.status, "result": record.result}

    def cancel_job(self, job_id: str) -> bool:
        self._require_enabled()
        record = self._jobs.get(job_id)
        if record is None:
            return False
        if record.status in {"complete", "cancelled"}:
            return False
        record.status = "cancelled"
        return True

    def stream_results(
        self, endpoint_name: str, payload: Mapping[str, Any]
    ) -> Iterator[dict[str, Any]]:
        self._require_enabled()
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
        file_id = f"{name}:{uuid.uuid4().hex}"
        self._files[file_id] = data
        return file_id

    def download_artifact(self, artifact_id: str) -> bytes:
        self._require_enabled()
        try:
            return self._files[artifact_id]
        except KeyError as exc:
            raise GradioRemoteError(f"Unknown artifact id: {artifact_id}") from exc

    def _require_enabled(self) -> None:
        if not self.enabled:
            raise GradioRemoteError("GradioClientAdapter is disabled")

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
            raise GradioRemoteError(f"Failed to connect to Gradio app: {exc}") from exc

        endpoints = self._endpoints_from_client(client)
        if not endpoints:
            raise GradioRemoteError(
                "Gradio client connected but no discoverable endpoints were found"
            )
        self.endpoints = tuple(endpoints)
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
                    except Exception as exc:
                        _logger.debug("Gradio endpoint probe %s() failed: %s", attr, exc)
                        continue
                except Exception as exc:
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
            # Some clients nest under dependencies / fns
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
